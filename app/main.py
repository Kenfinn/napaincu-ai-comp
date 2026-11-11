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

from . import ambang_profil, config, i18n, pasar, review, ringkasan, sitasi, store, tarik, umpan_balik, valuasi_otomatis
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
            # Pengumuman diproses dulu supaya halaman segera memuat data terbaru. Valuasi
            # otomatis (beta: 25 bulan harga harian, jeda 2 detik) bisa makan menit, jadi
            # dibangun sesudahnya, lalu hasil diproses ulang sekali lagi.
            hasil(segarkan=True)
            _segarkan_valuasi_dari_laporan()
            if valuasi_otomatis.panaskan(tarik.baca_watchlist()):
                hasil(segarkan=True)
        except Exception as e:                        # noqa: BLE001
            print(f"[pemantau] gagal: {type(e).__name__}: {e}", flush=True)
        time.sleep(jeda)


_laporan_diproses: set[str] = set()


def _segarkan_valuasi_dari_laporan() -> None:
    """Pasal 31 (laporan kuartal) memicu pembangunan ulang valuasi otomatis emiten watchlist.

    Sekali per pengumuman laporan selama proses hidup. Bila FinMind belum memuat laporannya,
    valuasi dibangun dari kuartal sebelumnya dan diperbarui lagi oleh TTL cache berikutnya.
    """
    wl = set(tarik.baca_watchlist())
    for h in list(_cache or []):
        if h.get("jenis") != "laporan" or h["id"] in _laporan_diproses:
            continue
        kode = (h.get("emiten") or {}).get("kode")
        _laporan_diproses.add(h["id"])
        if kode in wl:
            try:
                valuasi_otomatis.segarkan(kode)
            except Exception as e:                    # noqa: BLE001
                print(f"[laporan→valuasi] {kode}: {type(e).__name__}: {e}", flush=True)


def _panaskan_latar() -> None:
    """Bangun valuasi watchlist di latar belakang, lalu proses ulang. Satu saja sekaligus."""
    if not _kunci_panaskan.acquire(blocking=False):
        return

    def kerja():
        try:
            if valuasi_otomatis.panaskan(tarik.baca_watchlist()):
                hasil(segarkan=True)
        except Exception as e:                        # noqa: BLE001
            print(f"[panaskan] gagal: {type(e).__name__}: {e}", flush=True)
        finally:
            _kunci_panaskan.release()
    threading.Thread(target=kerja, name="panaskan", daemon=True).start()


_kunci_panaskan = threading.Lock()


def _hasil_awal_tanpa_model() -> None:
    """Saat server menyala: susun hasil dulu tanpa panggilan model baru (jawaban cache tetap
    dipakai), supaya halaman langsung terbuka. Pemakaian model menyusul di jalan berikutnya."""
    global _cache
    with _kunci_jalan:
        if _cache is None:
            llm.mulai_jalan(0)
            baru = pipeline.jalankan_semua()
            with _kunci_cache:
                _cache = baru


@asynccontextmanager
async def lifespan(_app):
    try:
        _hasil_awal_tanpa_model()
    except Exception as e:                            # noqa: BLE001 — server tetap menyala
        print(f"[awal] gagal menyusun hasil awal: {type(e).__name__}: {e}", flush=True)
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
tpl.env.globals["mops_laporan"] = sitasi.mops_laporan
tpl.env.globals["mops_cadangan"] = sitasi.mops_cadangan


def bahasa_dari(request: Request) -> str:
    """?lang= di URL menang, lalu cookie, lalu bawaan (English)."""
    return i18n.normal(request.query_params.get("lang") or request.cookies.get("bahasa"))


# --- hasil pipeline, dihitung sekali lalu disimpan ------------------------
# Dengan fixture ini seketika, tapi dengan 711 pengumuman dan panggilan model
# sungguhan ia mahal — jadi jangan dijalankan ulang tiap permintaan.
_cache: list[dict] | None = None
_kunci_cache = threading.Lock()
_kunci_jalan = threading.Lock()


def hasil(segarkan: bool = False) -> list[dict]:
    global _cache
    if segarkan:
        with _kunci_jalan:
            llm.mulai_jalan(config.MODEL_MAKS_PER_JALAN)
            baru = pipeline.jalankan_semua()
            with _kunci_cache:
                _cache = baru
            return _cache

    with _kunci_cache:
        if _cache is not None:
            return _cache

    with _kunci_jalan:
        with _kunci_cache:
            if _cache is not None:
                return _cache
        llm.mulai_jalan(config.MODEL_MAKS_PER_JALAN)
        baru = pipeline.jalankan_semua()
        with _kunci_cache:
            _cache = baru
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
    wl_set = set(tarik.baca_watchlist())
    profil = request.query_params.get("risiko") or request.cookies.get("risiko")
    profil = ambang_profil.normal(profil)
    dasar = {
        "profil_risiko": profil,
        "daftar_profil": ambang_profil.PROFIL,
        "tingkat_sinyal": lambda h: ambang_profil.tingkat(((h or {}).get("muatan") or {}).get("sinyal"), profil),
        "bahasa": bhs,
        "daftar_bahasa": i18n.BAHASA,
        # Posisional saja: kunci terjemahan boleh memakai parameter bernama {k} (pasal).
        "t": lambda *a, **p: i18n.t(a[0], bhs, **p),
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
        "jml_review": sum(1 for h in hasil() if h["status"] == "ditahan" and (h.get("contoh") or (h.get("emiten") or {}).get("kode") in wl_set)),
        "kode": None,
    }
    dasar.update(tambahan)
    return dasar


@app.get("/", response_class=HTMLResponse)
def feed(request: Request, segarkan: int = 0):
    daftar = hasil(bool(segarkan))
    lingkup = request.query_params.get("lingkup", "watchlist")
    total_semua = len(daftar)
    if lingkup == "semua":
        daftar_tampil = daftar[:300]
    else:
        wl = set(tarik.baca_watchlist())
        daftar_tampil = [h for h in daftar
                         if h.get("contoh") or (h.get("emiten") or {}).get("kode") in wl]
    return tpl.TemplateResponse(
        request=request, name="feed.html",
        context=konteks(request, "feed", daftar=daftar_tampil, lingkup=lingkup,
                        total_semua=total_semua, jml_tampil=len(daftar_tampil)))


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


@app.middleware("http")
async def kunci_baca_middleware(request: Request, call_next):
    kunci_aktif = getattr(config, "KUNCI_BACA", False) and bool(getattr(config, "KODE_AKSES", ""))
    if kunci_aktif:
        path = request.url.path
        jalur_terbuka = (
            path == "/akses"
            or path == "/sehat"
            or path.startswith("/static/")
            or path.startswith("/bahasa/")
            or path == "/api/impor"
        )
        if not jalur_terbuka and not _boleh_ubah(request):
            if path.startswith("/api/"):
                return JSONResponse({"galat": "perlu kode akses"}, status_code=401)
            return tpl.TemplateResponse(
                request=request,
                name="kunci.html",
                context=konteks(request, "kunci"),
                status_code=401,
            )
    return await call_next(request)


@app.get("/akses", include_in_schema=False)
def akses(kode: str = ""):
    """Buka tombol ubah untuk browser ini: /akses?kode=<SENTINEL_KODE_AKSES>."""
    if config.KODE_AKSES and hmac.compare_digest(kode, config.KODE_AKSES):
        r = _balik("/", i18n.pesan("msg.akses_ok"))
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
    _panaskan_latar()            # valuasi bisa makan menit: jangan tahan permintaan ini
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
        if d is None or (d.get("otomatis") and valuasi_otomatis.baca_cache(kode, terima_basi=False) is None):
            d_ambil = valuasi_otomatis.ambil(kode)
            d = store.muat_valuasi(kode) or d_ambil
        ctx["va"] = d
        if valuasi_otomatis.layak_dcf(d):
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


# --- antrean review manusia (HELD FOR REVIEW) -----------------------------
@app.get("/review", response_class=HTMLResponse)
def halaman_review(request: Request):
    semua = hasil()
    lingkup = request.query_params.get("lingkup", "watchlist")
    menunggu_semua = [h for h in semua if h["status"] == "ditahan"]
    wl = set(tarik.baca_watchlist())
    if lingkup == "semua":
        menunggu = menunggu_semua
    else:
        menunggu = [h for h in menunggu_semua
                    if h.get("contoh") or (h.get("emiten") or {}).get("kode") in wl]
    kep = review.baca()
    per_id = {h["id"]: h for h in semua}
    riwayat = sorted(({**v, "id": v.get("id") or k.split("#")[0],
                       "h": per_id.get(v.get("id") or k.split("#")[0])} for k, v in kep.items()),
                     key=lambda x: x["waktu"], reverse=True)
    return tpl.TemplateResponse(request=request, name="review.html",
                                context=konteks(request, "review", menunggu=menunggu, riwayat=riwayat,
                                                lingkup=lingkup, total_menunggu=len(menunggu_semua)))


@app.post("/review/{pengenal}")
async def putuskan_review(request: Request, pengenal: str):
    if not _boleh_ubah(request):
        return _tolak_akses("/review")
    f = await _form(request)
    keputusan, catatan = f.get("keputusan", ""), (f.get("catatan") or "").strip()
    h = next((x for x in hasil() if x["id"] == pengenal and x["status"] == "ditahan"), None)
    if h is None or keputusan not in review.KEPUTUSAN_SAH:
        raise HTTPException(404, "Kasus tidak ada di antrean review")
    if len(catatan) < 3:
        return _balik("/review", i18n.pesan("msg.review_catatan"), ok=False)
    tahan = (h.get("muatan") or {}).get("tahan") or {}
    if keputusan == "setujui" and not tahan.get("boleh_setujui"):
        return _balik("/review", i18n.pesan("msg.review_tidak_boleh"), ok=False)
    review.simpan(pengenal, keputusan, catatan, tahan.get("jenis"))
    hasil(segarkan=True)
    return _balik("/review", i18n.pesan("msg.review_ok", kode=h["emiten"]["kode"],
                                        keputusan=keputusan))


@app.get("/api/review", summary="Antrean HELD FOR REVIEW dan riwayat keputusan manusia")
def api_review():
    return JSONResponse({
        "menunggu": [{"id": h["id"], "emiten": h["emiten"], "judul": h["judul"], "alasan": h["alasan"],
                      "boleh_setujui": ((h.get("muatan") or {}).get("tahan") or {}).get("boleh_setujui")}
                     for h in hasil() if h["status"] == "ditahan"],
        "keputusan": review.baca(),
    })


# --- umpan balik 👍/👎 → ambang triase per pasal (A2) ----------------------
def _aman(ke: str | None, cadangan: str) -> str:
    return ke if ke and ke.startswith("/") and not ke.startswith("//") else cadangan


@app.post("/umpan-balik/{pengenal}")
async def beri_umpan_balik(request: Request, pengenal: str):
    f = await _form(request)
    ke = _aman(f.get("kembali"), f"/peringatan/{pengenal}")
    if not _boleh_ubah(request):
        return _tolak_akses(ke)
    h = next((x for x in hasil() if x["id"] == pengenal), None)
    if h is None:
        raise HTTPException(404, "Peringatan tidak ditemukan")
    suara = f.get("suara", "")
    if suara not in umpan_balik.SUARA_SAH + ("hapus",):
        raise HTTPException(400, "Suara tidak dikenal")
    tri = h.get("triase")
    if not tri:
        return _balik(ke, i18n.pesan("msg.tanpa_triase"), ok=False)
    ubah = umpan_balik.beri_suara(pengenal, tri["pasal"], suara, tri.get("skor"), h["emiten"]["kode"])
    hasil(segarkan=True)
    return _balik(ke, i18n.pesan("msg.suara_ok", k=tri["pasal"], dari=ubah["dari"], ke=ubah["ke"]))


def _pasal_terlihat() -> list[str]:
    return sorted({h["triase"]["pasal"] for h in hasil() if h.get("triase")})


@app.get("/ambang", response_class=HTMLResponse)
def halaman_ambang(request: Request):
    data = umpan_balik.semua(_pasal_terlihat())
    per_id = {h["id"]: h for h in hasil()}
    for r in data["riwayat"]:
        r["h"] = per_id.get(r.get("id"))
    return tpl.TemplateResponse(request=request, name="ambang.html",
                                context=konteks(request, "ambang", data=data))


@app.post("/ambang/{pasal}/{aksi}")
async def ubah_ambang(request: Request, pasal: str, aksi: str):
    if not _boleh_ubah(request):
        return _tolak_akses("/ambang")
    if not (pasal.isdigit() or pasal == "?") or aksi not in ("reset", "kunci", "buka"):
        raise HTTPException(404, "Aksi tidak dikenal")
    ubah = umpan_balik.reset(pasal) if aksi == "reset" else umpan_balik.kunci(pasal, aksi == "kunci")
    hasil(segarkan=True)
    return _balik("/ambang", i18n.pesan("msg.ambang_ok", k=pasal, dari=ubah["dari"], ke=ubah["ke"]))


@app.get("/api/ambang", summary="Ambang triase per pasal, asal-usulnya (👍/👎), dan riwayat perubahan")
def api_ambang():
    return JSONResponse(umpan_balik.semua(_pasal_terlihat()))


@app.get("/ekspor/kandidat-gold.csv", include_in_schema=False)
def ekspor_kandidat_gold(request: Request, per_pasal: int = 4):
    """Kandidat gold set dari arsip server, untuk dilabeli tim keuangan (butuh kode akses)."""
    if not _boleh_ubah(request):
        raise HTTPException(403, "Buka /akses?kode=... dulu")
    from fastapi.responses import Response
    from . import gold
    rek = gold.pilih(gold.muat_arsip(), per_pasal=max(1, min(per_pasal, 10)))
    # BOM supaya Excel membuka huruf Mandarin dengan benar.
    return Response("\ufeff" + gold.csv_kandidat(rek), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=kandidat-gold.csv"})


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
    r = tpl.TemplateResponse(
        request=request, name="peringatan.html",
        context=konteks(request, "feed", h=h, injeksi=injeksi,
                        suara=umpan_balik.suara_untuk(pengenal)))
    if request.query_params.get("risiko") in ambang_profil.PROFIL:
        r.set_cookie("risiko", request.query_params["risiko"], max_age=60 * 60 * 24 * 365, samesite="lax")
    return r


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
        context=konteks(request, "valuasi", kode=kode, r=dcf.compute(d, forward_g=g), va=d))


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


# --- Ask FEAF (app/chat.py, milik Claude) ---------------------------------
from . import chat as _chat  # noqa: E402

app.include_router(_chat.router)
