"""Aplikasi web FEAF — Agentic AI Investment Assistant.

Server-rendered, tanpa build step, tanpa npm. Satu orang teknis harus bisa merawatnya,
dan juri harus bisa menjalankannya dengan dua perintah.

Tanpa login, dan itu keputusan sadar: aturan mewajibkan akun evaluator hanya "bila
perlu login". Tanpa login berarti tidak ada kata sandi yang disimpan, tidak ada
kewajiban PDPA tambahan, dan tidak ada permukaan serangan yang perlu dipertahankan.

Jalankan:
    pip install -r requirements.txt
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import hmac
import json
import os
import threading
import time
import urllib.parse
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import config, i18n, pasar, ringkasan, store, tarik
from .agent import llm, pipeline

import sys
sys.path.insert(0, os.path.join(config.ROOT, "scripts"))
import dcf                                               # noqa: E402

def _pemantau() -> None:
    """Periksa pengumuman berkala di latar belakang. Galat dicatat di status, tidak mematikan server."""
    jeda = max(config.TARIK_OTOMATIS_DETIK, 300)
    while True:
        try:
            tarik.periksa_sekarang()
            hasil(segarkan=True)
        except Exception as e:                        # noqa: BLE001
            print(f"[pemantau] gagal: {type(e).__name__}: {e}", flush=True)
        time.sleep(jeda)


@asynccontextmanager
async def lifespan(_app):
    if config.TARIK_OTOMATIS_DETIK > 0:
        threading.Thread(target=_pemantau, name="pemantau", daemon=True).start()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="FEAF · Agentic AI Investment Assistant",
    description="Agent pemantau pengumuman MOPS yang menghitung ulang valuasi "
                "dan menolak angka yang tidak bisa ditelusuri ke dokumen sumbernya.",
    version="0.1.0",
)
HERE = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")
tpl = Jinja2Templates(directory=os.path.join(HERE, "templates"))


# --- filter angka: format mengikuti bahasa --------------------------------
# EN/中文: 1,480,000.5 · ID: 1.480.000,5
from jinja2 import pass_context  # noqa: E402


@pass_context
def rb(ctx, x, desimal: int = 0):
    return "—" if x is None else i18n.angka(x, ctx.get("bahasa", i18n.BAWAAN), desimal)


@pass_context
def pct(ctx, x, desimal: int = 2):
    return "—" if x is None else rb(ctx, x * 100, desimal) + "%"


tpl.env.filters["rb"] = rb
tpl.env.filters["pct"] = pct


def bahasa_dari(request: Request) -> str:
    """?lang= di URL menang, lalu cookie, lalu bawaan (English)."""
    return i18n.normal(request.query_params.get("lang") or request.cookies.get("bahasa"))


# --- hasil pipeline, dihitung sekali lalu disimpan ------------------------
# Dengan fixture ini seketika, tapi dengan 711 pengumuman dan panggilan model
# sungguhan ia mahal — jadi jangan dijalankan ulang tiap permintaan.
_cache: list[dict] | None = None
_kunci_cache = threading.Lock()


def hasil(segarkan: bool = False) -> list[dict]:
    global _cache
    with _kunci_cache:
        if _cache is None or segarkan:
            _cache = pipeline.jalankan_semua()
        return _cache


def _saham_samping() -> list[dict]:
    """Daftar watchlist untuk menu samping: kode, nama, perubahan harga (dari cache saja)."""
    detail, _ = store.muat_detail()
    nama_dari_data = {d.get("code"): d.get("name") for d in detail if d.get("name")}
    keluar = []
    for k in tarik.baca_watchlist():
        h = pasar.harga_dari_cache(k) or {}
        keluar.append({"kode": k, "nama": h.get("nama") or nama_dari_data.get(k),
                       "ubah_pct": h.get("ubah_pct")})
    return keluar


def konteks(request: Request, halaman: str, **tambahan) -> dict:
    _, sumber = store.muat_detail()
    bhs = bahasa_dari(request)
    pesan_kilat, pesan_ok = None, True
    if request.query_params.get("pesan"):
        try:
            p = json.loads(request.query_params["pesan"])
            pesan_kilat, pesan_ok = i18n.tr(p, bhs), bool(p.get("ok", True))
        except (ValueError, AttributeError):
            pesan_kilat = None
    dasar = {
        "bahasa": bhs,
        "daftar_bahasa": i18n.BAHASA,
        "t": lambda k, **p: i18n.t(k, bhs, **p),
        "tr": lambda o, cadangan="": i18n.tr(o, bhs, cadangan),
        "path_sekarang": request.url.path,
        "pesan_ok": pesan_ok,
        "status_tarik": tarik.baca_status(),
        "jml_watchlist": len(tarik.baca_watchlist()),
        "pesan": pesan_kilat,
        "request": request,
        "halaman": halaman,
        "saham_samping": _saham_samping(),
        "model": llm.nama_model(),
        "pakai_model": llm.tersedia(),
        "sumber_data": sumber,
        "jml_terbit": sum(1 for h in hasil() if h["status"] == "terbit"),
        "kode": None,
    }
    dasar.update(tambahan)
    return dasar


@app.get("/", response_class=HTMLResponse)
def feed(request: Request, segarkan: int = 0):
    daftar = hasil(bool(segarkan))
    _, sumber = store.muat_detail()
    if sumber == "nyata":
        # Saham yang dihapus dari watchlist berhenti tampil; riwayatnya tetap tersimpan.
        wl = set(tarik.baca_watchlist())
        daftar = [h for h in daftar
                  if h.get("contoh") or (h.get("emiten") or {}).get("kode") in wl]
    return tpl.TemplateResponse(
        request=request, name="feed.html",
        context=konteks(request, "feed", daftar=daftar))


# --- penarikan dinamis & watchlist ----------------------------------------
async def _form(request: Request) -> dict[str, str]:
    """Urai form tanpa dependensi tambahan (python-multipart tidak dibutuhkan)."""
    badan = (await request.body()).decode("utf-8", "replace")
    return {k: v[0] for k, v in urllib.parse.parse_qs(badan).items()}


def _balik(ke: str, pesan: dict, ok: bool = True) -> RedirectResponse:
    """Pesan dikirim sebagai kode i18n, bukan kalimat jadi, supaya tampil di bahasa pengguna."""
    isi = json.dumps({"kode": pesan["kode"], "param": pesan.get("param", {}), "ok": ok},
                     ensure_ascii=False)
    pisah = "&" if "?" in ke else "?"
    return RedirectResponse(f"{ke}{pisah}pesan={urllib.parse.quote(isi)}", status_code=303)


def _ringkas_status(st: dict) -> tuple[dict, bool]:
    if not st.get("ok"):
        sebab = "; ".join(f"{k}: {v.get('jenis')}" for k, v in st["sumber"].items())
        return i18n.pesan("msg.tarik_gagal", sebab=sebab), False
    return i18n.pesan("msg.tarik_ok", n=st["cocok_watchlist"], baru=st["baru"]), True


def _boleh_ubah(request: Request) -> bool:
    """Tanpa SENTINEL_KODE_AKSES semua boleh. Dengan itu, perlu cookie dari /akses."""
    if not config.KODE_AKSES:
        return True
    return hmac.compare_digest(request.cookies.get("akses", ""), config.KODE_AKSES)


def _tolak_akses(ke: str) -> RedirectResponse:
    return _balik(ke, i18n.pesan("msg.perlu_akses"), ok=False)


@app.get("/akses", include_in_schema=False)
def akses(kode: str = ""):
    """Buka tombol ubah untuk browser ini: /akses?kode=<SENTINEL_KODE_AKSES>."""
    if config.KODE_AKSES and hmac.compare_digest(kode, config.KODE_AKSES):
        r = _balik("/watchlist", i18n.pesan("msg.akses_ok"))
        r.set_cookie("akses", kode, max_age=60 * 60 * 24 * 30, httponly=True, samesite="lax")
        return r
    return _balik("/", i18n.pesan("msg.akses_salah"), ok=False)


@app.get("/sehat", include_in_schema=False)
def sehat():
    """Untuk health check Dokploy/Docker: server hidup dan data terbaca."""
    detail, sumber = store.muat_detail()
    return {"ok": True, "sumber": sumber, "pengumuman": len(detail),
            "tarik_terakhir": (tarik.baca_status() or {}).get("waktu")}


@app.post("/periksa", summary="Tarik pengumuman terbaru untuk watchlist, lalu proses ulang")
async def periksa(request: Request):
    f = await _form(request)
    if not _boleh_ubah(request):
        return _tolak_akses("/")
    st = tarik.periksa_sekarang()
    hasil(segarkan=True)
    ke = f.get("kembali") or "/"
    pesan, ok = _ringkas_status(st)
    return _balik(ke if ke.startswith("/") and not ke.startswith("//") else "/", pesan, ok)


@app.get("/watchlist", response_class=HTMLResponse)
def watchlist(request: Request):
    detail, _ = store.muat_detail()
    tervaluasi = set(store.emiten_tervaluasi())
    baris = []
    for k in tarik.baca_watchlist():
        punya = [d for d in detail if d.get("code") == k]
        baris.append({
            "kode": k,
            "nama": (pasar.harga_dari_cache(k) or {}).get("nama")
                    or next((d.get("name") for d in punya if d.get("name")), None),
            "valuasi": k in tervaluasi,
            "jumlah": len(punya),
            "terakhir": max((f"{d.get('date')} {d.get('time')}" for d in punya), default=None),
        })
    return tpl.TemplateResponse(
        request=request, name="watchlist.html",
        context=konteks(request, "watchlist", baris=baris))


@app.post("/watchlist/tambah")
async def watchlist_tambah(request: Request):
    if not _boleh_ubah(request):
        return _tolak_akses("/watchlist")
    f = await _form(request)
    ok, pesan = tarik.tambah_ke_watchlist(f.get("kode", ""), pasar.emiten_dikenal())
    ke = f.get("kembali") or "/watchlist"
    return _balik(ke if ke.startswith("/") and not ke.startswith("//") else "/watchlist", pesan, ok)


@app.post("/watchlist/hapus/{kode}")
def watchlist_hapus(request: Request, kode: str):
    if not _boleh_ubah(request):
        return _tolak_akses("/watchlist")
    tarik.hapus_dari_watchlist(kode)
    return _balik("/watchlist", i18n.pesan("msg.dihapus", kode=kode))


@app.get("/bahasa/{kode}")
def ganti_bahasa(kode: str, ke: str = "/"):
    """Simpan pilihan bahasa di cookie, lalu kembali ke halaman semula."""
    tujuan = ke if ke.startswith("/") and not ke.startswith("//") else "/"
    r = RedirectResponse(tujuan, status_code=303)
    r.set_cookie("bahasa", i18n.normal(kode), max_age=60 * 60 * 24 * 365, samesite="lax")
    return r


# --- halaman saham (Stream · Key Stats · Financials · Valuation · Profile) ---
TAB_SAHAM = ("ringkasan", "stream", "stats", "keu", "valuasi", "profil")


@app.get("/saham", include_in_schema=False)
def cari_saham(kode: str = ""):
    kode = kode.strip().upper()
    return RedirectResponse(f"/saham/{kode}" if tarik.KODE_SAH.match(kode) else "/watchlist", status_code=303)


@app.get("/saham/{kode}", response_class=HTMLResponse)
def saham(request: Request, kode: str, tab: str = "ringkasan", lap: str = "lr",
          per: str = "q", mode: str = "nilai", risiko: str = ""):
    kode = kode.strip().upper()
    if not tarik.KODE_SAH.match(kode):
        raise HTTPException(404, "Kode saham tidak dikenal")
    tab = tab if tab in TAB_SAHAM else "ringkasan"
    risiko = risiko if risiko in ringkasan.PROFIL_RISIKO else (
        request.cookies.get("risiko") if request.cookies.get("risiko") in ringkasan.PROFIL_RISIKO else "moderat")
    lap = lap if lap in pasar.LAPORAN else "lr"
    per = per if per in ("q", "y") else "q"
    mode = mode if mode in ("nilai", "yoy") else "nilai"

    detail, _ = store.muat_detail()
    nama = next((d.get("name") for d in detail if d.get("code") == kode and d.get("name")), None)
    ctx = {"kode_saham": kode, "tab": tab, "lap": lap, "per": per, "mode": mode, "risiko": risiko,
           "harga": pasar.harga(kode), "di_watchlist": kode in tarik.baca_watchlist()}
    if tab == "ringkasan":
        ctx["rk"] = ringkasan.susun(kode, bahasa_dari(request), risiko, hasil())
    elif tab == "stream":
        ctx["daftar"] = [h for h in hasil() if (h.get("emiten") or {}).get("kode") == kode]
    elif tab == "stats":
        ctx["s"] = pasar.statistik(kode)
    elif tab == "keu":
        ctx["tb"] = pasar.tabel(kode, lap, per, mode)
    elif tab == "valuasi":
        d = store.muat_valuasi(kode)
        if d is not None:
            ctx["r"] = dcf.compute(d, forward_g=d.get("assumptions", {}).get("terminal_growth_ceiling"))
    elif tab == "profil":
        ctx["p"] = pasar.profil(kode)
    ctx["nama_saham"] = (ctx["harga"] or {}).get("nama") or nama
    r = tpl.TemplateResponse(request=request, name="saham.html",
                             context=konteks(request, "saham", **ctx))
    if request.query_params.get("risiko") in ringkasan.PROFIL_RISIKO:
        r.set_cookie("risiko", risiko, max_age=60 * 60 * 24 * 365, samesite="lax")
    return r


@app.get("/api/saham/{kode}/keuangan", summary="Tabel laporan keuangan (lr | neraca | arus)")
def api_keuangan(kode: str, lap: str = "lr", per: str = "q", mode: str = "nilai"):
    if not tarik.KODE_SAH.match(kode.upper()) or lap not in pasar.LAPORAN:
        raise HTTPException(404, "Kode atau jenis laporan tidak dikenal")
    return JSONResponse(pasar.tabel(kode.upper(), lap, "y" if per == "y" else "q",
                                    "yoy" if mode == "yoy" else "nilai"))


@app.post("/api/impor", summary="Impor riwayat pengumuman MOPS dari laptop di jaringan Taiwan")
async def api_impor(request: Request):
    """Dipakai scripts/kirim_riwayat.py. Wajib header X-Kode-Akses = SENTINEL_KODE_AKSES.

    Tanpa SENTINEL_KODE_AKSES di server, impor ditutup sama sekali: endpoint yang
    menulis data tidak boleh terbuka untuk siapa pun yang tahu alamatnya.
    """
    kode = request.headers.get("x-kode-akses", "")
    if not config.KODE_AKSES or not hmac.compare_digest(kode, config.KODE_AKSES):
        raise HTTPException(403, "Kode akses salah atau impor belum diaktifkan")
    badan = await request.body()
    if len(badan) > 25 * 1024 * 1024:
        raise HTTPException(413, "Kiriman terlalu besar (maks 25 MB); kirim bertahap")
    try:
        data = json.loads(badan.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(400, "Badan bukan JSON")
    diterima, tolak = tarik.bersihkan_impor(data)
    baru = tarik.gabung(diterima) if diterima else 0
    if baru:
        hasil(segarkan=True)
    return {"diterima": len(diterima), "baru": baru, "ditolak": len(tolak), "contoh_tolak": tolak[:5]}


@app.get("/api/watchlist", summary="Daftar kode saham yang dipantau")
def api_watchlist():
    return JSONResponse({"kode": tarik.baca_watchlist(), "status_tarik": tarik.baca_status()})


@app.get("/peringatan/{pengenal}", response_class=HTMLResponse)
def peringatan(request: Request, pengenal: str):
    h = next((x for x in hasil() if x["id"] == pengenal), None)
    if h is None:
        raise HTTPException(404, "Peringatan tidak ditemukan")
    # Dicari di sini, bukan di template: Jinja tidak punya test pencarian
    # substring, dan logika seperti ini memang bukan urusan lapisan tampilan.
    injeksi = next((l for l in h["jejak"] if "injeksi" in l["tahap"].lower()), None)
    return tpl.TemplateResponse(
        request=request, name="peringatan.html",
        context=konteks(request, "feed", h=h, injeksi=injeksi))


@app.get("/jejak/{pengenal}", response_class=HTMLResponse)
def jejak(request: Request, pengenal: str):
    h = pipeline.muat_jejak(pengenal) or next((x for x in hasil() if x["id"] == pengenal), None)
    if h is None:
        raise HTTPException(404, "Jejak tidak ditemukan")
    return tpl.TemplateResponse(
        request=request, name="jejak.html",
        context=konteks(request, "feed", h=h))


@app.get("/valuasi/{kode}", response_class=HTMLResponse)
def valuasi(request: Request, kode: str):
    d = store.muat_valuasi(kode)
    if d is None:
        raise HTTPException(404, f"Belum ada berkas valuasi untuk {kode}")
    g = d.get("assumptions", {}).get("terminal_growth_ceiling")
    return tpl.TemplateResponse(
        request=request, name="valuasi.html",
        context=konteks(request, "valuasi", kode=kode, r=dcf.compute(d, forward_g=g)))


# --- API JSON — sekalian jadi dokumentasi antarmuka di /docs -------------
@app.get("/api/peringatan", summary="Daftar hasil pemrosesan seluruh pengumuman")
def api_daftar():
    return JSONResponse([{
        "id": h["id"], "status": h["status"], "emiten": h["emiten"],
        "judul": h["judul"], "tanggal": h["tanggal"],
        "alasan": h["alasan"], "sumber_url": h["sumber_url"],
        "ringkasan": h["ringkasan"],
    } for h in hasil()])


@app.get("/api/jejak/{pengenal}", summary="Operation trace satu pengumuman")
def api_jejak(pengenal: str):
    h = pipeline.muat_jejak(pengenal)
    if h is None:
        raise HTTPException(404, "Jejak tidak ditemukan")
    return JSONResponse(h)


@app.get("/api/valuasi/{kode}", summary="Keluaran kalkulator DCF untuk satu emiten")
def api_valuasi(kode: str):
    d = store.muat_valuasi(kode)
    if d is None:
        raise HTTPException(404, f"Belum ada berkas valuasi untuk {kode}")
    return JSONResponse(dcf.compute(d, forward_g=d.get("assumptions", {}).get("terminal_growth_ceiling")))
