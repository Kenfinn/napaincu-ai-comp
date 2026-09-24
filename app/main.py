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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import config, store
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
    return tpl.TemplateResponse(
        request=request, name="feed.html",
        context=konteks(request, "feed", daftar=hasil(bool(segarkan))))


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
