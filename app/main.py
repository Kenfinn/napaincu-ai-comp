"""Aplikasi web Sentinel Saham.

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

import os
import urllib.parse

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import config, store, tarik
from .agent import llm, pipeline

import sys
sys.path.insert(0, os.path.join(config.ROOT, "scripts"))
import dcf                                               # noqa: E402

app = FastAPI(
    title="Sentinel Saham",
    description="Agent pemantau pengumuman MOPS yang menghitung ulang valuasi "
                "dan menolak angka yang tidak bisa ditelusuri ke dokumen sumbernya.",
    version="0.1.0",
)
HERE = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")
tpl = Jinja2Templates(directory=os.path.join(HERE, "templates"))


# --- filter angka: format Indonesia (titik ribuan, koma desimal) ----------
def rb(x, desimal: int = 0):
    if x is None:
        return "—"
    s = f"{x:,.{desimal}f}"
    return s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def pct(x, desimal: int = 2):
    return "—" if x is None else rb(x * 100, desimal) + "%"


tpl.env.filters["rb"] = rb
tpl.env.filters["pct"] = pct


# --- hasil pipeline, dihitung sekali lalu disimpan ------------------------
# Dengan fixture ini seketika, tapi dengan 711 pengumuman dan panggilan model
# sungguhan ia mahal — jadi jangan dijalankan ulang tiap permintaan.
_cache: list[dict] | None = None


def hasil(segarkan: bool = False) -> list[dict]:
    global _cache
    if _cache is None or segarkan:
        _cache = pipeline.jalankan_semua()
    return _cache


def konteks(request: Request, halaman: str, **tambahan) -> dict:
    _, sumber = store.muat_detail()
    dasar = {
        "status_tarik": tarik.baca_status(),
        "jml_watchlist": len(tarik.baca_watchlist()),
        "pesan": request.query_params.get("pesan"),
        "request": request,
        "halaman": halaman,
        "emiten": store.emiten_tervaluasi(),
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
        daftar = [h for h in daftar if (h.get("emiten") or {}).get("kode") in wl]
    return tpl.TemplateResponse(
        request=request, name="feed.html",
        context=konteks(request, "feed", daftar=daftar))


# --- penarikan dinamis & watchlist ----------------------------------------
async def _form(request: Request) -> dict[str, str]:
    """Urai form tanpa dependensi tambahan (python-multipart tidak dibutuhkan)."""
    badan = (await request.body()).decode("utf-8", "replace")
    return {k: v[0] for k, v in urllib.parse.parse_qs(badan).items()}


def _balik(ke: str, pesan: str) -> RedirectResponse:
    pisah = "&" if "?" in ke else "?"
    return RedirectResponse(f"{ke}{pisah}pesan={urllib.parse.quote(pesan)}", status_code=303)


def _ringkas_status(st: dict) -> str:
    if not st.get("ok"):
        sebab = "; ".join(f"{k}: {v.get('jenis')}" for k, v in st["sumber"].items())
        return f"Penarikan gagal ({sebab}). Data terakhir yang tersimpan tetap dipakai."
    return (f"Diperiksa: {st['cocok_watchlist']} pengumuman emiten watchlist di tarikan ini, "
            f"{st['baru']} baru.")


@app.post("/periksa", summary="Tarik pengumuman terbaru untuk watchlist, lalu proses ulang")
async def periksa(request: Request):
    f = await _form(request)
    st = tarik.periksa_sekarang()
    hasil(segarkan=True)
    ke = f.get("kembali") or "/"
    return _balik(ke if ke.startswith("/") else "/", _ringkas_status(st))


@app.get("/watchlist", response_class=HTMLResponse)
def watchlist(request: Request):
    detail, _ = store.muat_detail()
    tervaluasi = set(store.emiten_tervaluasi())
    baris = []
    for k in tarik.baca_watchlist():
        punya = [d for d in detail if d.get("code") == k]
        baris.append({
            "kode": k,
            "nama": next((d.get("name") for d in punya if d.get("name")), None),
            "valuasi": k in tervaluasi,
            "jumlah": len(punya),
            "terakhir": max((f"{d.get('date')} {d.get('time')}" for d in punya), default=None),
        })
    return tpl.TemplateResponse(
        request=request, name="watchlist.html",
        context=konteks(request, "watchlist", baris=baris))


@app.post("/watchlist/tambah")
async def watchlist_tambah(request: Request):
    ok, pesan = tarik.tambah_ke_watchlist((await _form(request)).get("kode", ""))
    if ok:
        pesan += " Tekan “Periksa sekarang” untuk menarik pengumumannya."
    return _balik("/watchlist", pesan)


@app.post("/watchlist/hapus/{kode}")
def watchlist_hapus(kode: str):
    tarik.hapus_dari_watchlist(kode)
    return _balik("/watchlist", f"{kode} dihapus dari watchlist.")


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
