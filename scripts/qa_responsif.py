#!/usr/bin/env python3
"""QA Playwright untuk tata letak responsif (desktop & ponsel), menu kiri, dan panel chat (QA-6)."""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest.mock
from pathlib import Path

import uvicorn
from playwright.sync_api import sync_playwright

AKAR = Path(__file__).resolve().parent.parent
if str(AKAR) not in sys.path:
    sys.path.insert(0, str(AKAR))

RUTE_UTAMA = [
    ("/", "feed"),
    ("/watchlist", "watchlist"),
    ("/review", "review"),
    ("/ambang", "ambang"),
    ("/tanya", "tanya"),
    ("/peringatan/2330-2026-09-18-1", "peringatan-terbit"),
    ("/peringatan/2330-2026-09-19-4", "peringatan-ditahan"),
    ("/jejak/2330-2026-09-18-1", "jejak"),
    ("/valuasi/2330", "valuasi"),
    ("/saham/2330?tab=ringkasan", "saham-ringkasan"),
    ("/saham/2330?tab=stream", "saham-stream"),
    ("/saham/2330?tab=stats", "saham-stats"),
    ("/saham/2330?tab=keu", "saham-keu"),
    ("/saham/2330?tab=valuasi", "saham-valuasi"),
    ("/saham/2330?tab=profil", "saham-profil"),
]


def _cari_chrome() -> str | None:
    for kandidat in ("/usr/bin/google-chrome", shutil.which("google-chrome"), shutil.which("chromium")):
        if kandidat and os.path.exists(kandidat):
            return kandidat
    return None


def _port_bebas() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _siapkan_server_luring():
    """Jalankan uvicorn terisolasi dari data lokal & jaringan pada thread lokal."""
    tmp = tempfile.TemporaryDirectory()
    tpath = Path(tmp.name)
    parsed = tpath / "parsed"  # kosong agar jatuh ke data/fixtures/
    raw = tpath / "raw" / "openapi"

    from app import (
        config,
        gold,
        harga_resmi,
        indeks_nama,
        main as app_main,
        pasar,
        review,
        tarik,
        umpan_balik,
        valuasi_otomatis,
    )
    from app.agent import llm

    patches = [
        unittest.mock.patch.object(config, "DATA_DIR", str(tpath)),
        unittest.mock.patch.object(config, "PARSED_DIR", str(parsed)),
        unittest.mock.patch.object(config, "TRACE_DIR", str(tpath / "traces")),
        unittest.mock.patch.object(config, "KODE_AKSES", ""),
        unittest.mock.patch.object(config, "SERTAKAN_CONTOH", True),
        unittest.mock.patch.object(tarik, "WATCHLIST_FILE", str(tpath / "watchlist.json")),
        unittest.mock.patch.object(tarik, "STATUS_FILE", str(tpath / "status_tarik.json")),
        unittest.mock.patch.object(tarik, "RAW_DIR", str(raw)),
        unittest.mock.patch.object(tarik, "DETAIL_FILE", str(parsed / "details.json")),
        unittest.mock.patch.object(tarik, "LIST_FILE", str(parsed / "announcements.json")),
        unittest.mock.patch.object(review, "KEPUTUSAN_FILE", str(tpath / "keputusan_review.json")),
        unittest.mock.patch.object(umpan_balik, "FILE", str(tpath / "umpan_balik.json")),
        unittest.mock.patch.object(pasar, "CACHE_DIR", str(tpath / "pasar")),
        unittest.mock.patch.object(valuasi_otomatis, "CACHE_DIR", tpath / "valuasi_otomatis"),
        unittest.mock.patch.object(llm, "CACHE_DIR", str(tpath / "cache_model")),
        unittest.mock.patch.object(indeks_nama, "BERKAS_INDEKS", str(tpath / "indeks_nama.json")),
        unittest.mock.patch.object(gold, "ARSIP_DIR", str(raw)),
        unittest.mock.patch.object(tarik, "_ambil_json", return_value=[]),
        unittest.mock.patch.object(pasar, "_ambil_json", return_value=[]),
        unittest.mock.patch.object(pasar, "_finmind", return_value=[]),
        unittest.mock.patch.object(harga_resmi, "_ambil_json", return_value=None),
        unittest.mock.patch.object(indeks_nama, "_ambil_url_json", return_value=None),
        unittest.mock.patch.object(valuasi_otomatis, "pemicu_hitung_beta_latar", return_value=None),
    ]
    for p in patches:
        p.start()

    sampel = json.loads((AKAR / "tests" / "data" / "pasar_sampel.json").read_text(encoding="utf-8"))
    for nama, isi in sampel.items():
        pasar._tulis_cache(nama, isi)
    va_2330 = json.loads((Path(config.VALUATION_DIR) / "2330.json").read_text(encoding="utf-8"))
    va_copy = copy.deepcopy(va_2330)
    va_copy["otomatis"] = True
    va_copy["bursa"] = "TWSE"
    valuasi_otomatis.simpan_cache("2330", va_copy)

    with app_main._kunci_cache:
        app_main._cache = None
    app_main.hasil()

    port = _port_bebas()
    cfg = uvicorn.Config(app_main.app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(cfg)
    th = threading.Thread(target=server.run, daemon=True)
    th.start()
    batas = time.monotonic() + 10.0
    while not server.started and time.monotonic() < batas:
        time.sleep(0.05)

    def tutup():
        server.should_exit = True
        th.join(timeout=3.0)
        for p in reversed(patches):
            p.stop()
        tmp.cleanup()

    return f"http://127.0.0.1:{port}", tutup


def _cek_halaman(page, url: str, lebar: int, desktop: bool) -> list[str]:
    """Periksa overflow horizontal dan terpotongnya teks menu pada halaman aktif."""
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(120)
    data = page.evaluate("""(isDesktop) => {
        const vw = window.innerWidth;
        const sw = document.documentElement.scrollWidth;
        const bocor = [];
        if (sw > vw + 1) {
            document.querySelectorAll('body *').forEach((el) => {
                const st = getComputedStyle(el);
                if (st.display === 'none') return;
                let cur = el.parentElement, inScroll = false;
                while (cur && cur !== document.body) {
                    const pst = getComputedStyle(cur);
                    if ((pst.overflowX === 'auto' || pst.overflowX === 'scroll') && cur.clientWidth <= vw + 2) {
                        inScroll = true; break;
                    }
                    cur = cur.parentElement;
                }
                if (inScroll) return;
                const r = el.getBoundingClientRect();
                if (r.width > 0 && r.height > 0 && r.right > vw + 1.5 && bocor.length < 5) {
                    const id = el.id ? '#' + el.id : '';
                    const cls = typeof el.className === 'string' && el.className.trim()
                        ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.')
                        : '';
                    bocor.push(`${el.tagName.toLowerCase()}${id}${cls} (right=${Math.round(r.right)})`);
                }
            });
        }
        const terpotong = [];
        if (isDesktop) {
            const rail = document.querySelector('.rail');
            const isi = document.querySelector('.isi');
            const status = document.querySelector('.rail .status-kotak');
            if (rail && isi) {
                const rr = rail.getBoundingClientRect();
                const ri = isi.getBoundingClientRect();
                const rs = getComputedStyle(rail);
                if (rr.width < 260 || rr.width > 285) {
                    terpotong.push(`lebar .rail=${Math.round(rr.width)}px (harus 264-280px)`);
                }
                if (rs.overflowY !== 'auto' && rs.overflowY !== 'scroll') {
                    terpotong.push(`.rail desktop harus overflow-y: auto (kini ${rs.overflowY})`);
                }
                if (rr.right > ri.left + 1) {
                    terpotong.push(`.rail menimpa .isi (${Math.round(rr.right)} > ${Math.round(ri.left)})`);
                }
            }
            if (status && status.scrollWidth > status.clientWidth + 1) {
                terpotong.push(`kotak status meluap (${status.scrollWidth}>${status.clientWidth})`);
            }
            document.querySelectorAll('.rail .nav a, .rail .daftar-saham a').forEach((a) => {
                if (a.scrollWidth > a.clientWidth + 1) {
                    terpotong.push(`menu terpotong: "${a.innerText.trim()}" (${a.scrollWidth}>${a.clientWidth})`);
                }
            });
        }
        return {vw, sw, bocor, terpotong};
    }""", desktop)

    masalah: list[str] = []
    if data["sw"] > data["vw"] + 1:
        detail = "; ".join(data["bocor"]) or "elemen melebar"
        masalah.append(f"overflow horizontal scrollWidth={data['sw']} > innerWidth={data['vw']} [{detail}]")
    masalah.extend(data["terpotong"])
    return masalah


def _cek_laci_ponsel(page, url: str) -> list[str]:
    """Pastikan tombol menu, buka/tutup laci, target sentuh, dan ESC berfungsi di ponsel."""
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(120)
    masalah: list[str] = []

    btn = page.locator("[data-buka-menu]").first
    if not btn.is_visible():
        return ["tombol [data-buka-menu] tidak terlihat di ponsel"]

    box_btn = btn.bounding_box()
    if not box_btn or box_btn["height"] < 40 or box_btn["width"] < 40:
        masalah.append(f"target sentuh tombol menu terlalu kecil: {box_btn}")

    btn.click()
    page.wait_for_timeout(240)

    info_laci = page.evaluate("""() => {
        const rail = document.querySelector('.rail');
        const body = document.body;
        const rr = rail ? rail.getBoundingClientRect() : null;
        const kecil = [];
        document.querySelectorAll('.rail .nav a, .tutup-laci').forEach((el) => {
            const r = el.getBoundingClientRect();
            if (r.height > 0 && r.height < 40) {
                kecil.push(`${el.className || el.textContent.trim()}: h=${Math.round(r.height)}`);
            }
        });
        const pot = [];
        document.querySelectorAll('.rail .nav a, .rail .daftar-saham a').forEach((a) => {
            if (a.scrollWidth > a.clientWidth + 1) {
                pot.push(`laci terpotong: "${a.innerText.trim()}" (${a.scrollWidth}>${a.clientWidth})`);
            }
        });
        return {
            buka: !!(rail && rail.classList.contains('buka')),
            lockBody: getComputedStyle(body).overflowY === 'hidden' && body.classList.contains('laci-terbuka'),
            xRail: rr ? rr.left : -999,
            kecil,
            pot,
        };
    }""")
    if not info_laci["buka"] or info_laci["xRail"] < -2:
        masalah.append(f"laci gagal terbuka penuh: {info_laci}")
    if not info_laci["lockBody"]:
        masalah.append("body tidak mengunci gulir (overflow: hidden) saat laci terbuka")
    if info_laci["kecil"]:
        masalah.append(f"target sentuh < 40px di laci: {info_laci['kecil']}")
    masalah.extend(info_laci["pot"])

    # Tutup lewat tombol ✕
    page.locator("[data-tutup-menu].tutup-laci").first.click()
    page.wait_for_timeout(240)
    if page.locator(".rail.buka").count() > 0 or page.locator("body.laci-terbuka").count() > 0:
        masalah.append("tombol tutup-laci tidak menutup laci sepenuhnya")

    # Buka lagi, tutup lewat backdrop (.latar-laci) di sisi kanan
    btn.click()
    page.wait_for_timeout(240)
    vw = page.viewport_size["width"]
    page.mouse.click(max(vw - 20, 320), 200)
    page.wait_for_timeout(240)
    if page.locator(".rail.buka").count() > 0:
        masalah.append("klik backdrop .latar-laci tidak menutup laci")

    # Buka lagi, tutup lewat tombol Escape
    btn.click()
    page.wait_for_timeout(240)
    page.keyboard.press("Escape")
    page.wait_for_timeout(240)
    if page.locator(".rail.buka").count() > 0:
        masalah.append("tombol Escape tidak menutup laci")

    return masalah


def _cek_panel_chat(page, url: str) -> list[str]:
    """Pastikan #cp-fab dan #cp-panel terlihat, bisa dibuka-tutup, dan muat di viewport."""
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(120)
    masalah: list[str] = []

    fab = page.locator("#cp-fab")
    if fab.count() == 0 or not fab.is_visible():
        return ["#cp-fab tidak terlihat"]

    box_fab = fab.bounding_box()
    vw = page.viewport_size["width"]
    vh = page.viewport_size["height"]
    if not box_fab or box_fab["x"] < 0 or box_fab["y"] < 0 or box_fab["x"] + box_fab["width"] > vw + 1 or box_fab["y"] + box_fab["height"] > vh + 1:
        masalah.append(f"#cp-fab keluar viewport ({vw}x{vh}): {box_fab}")

    if page.locator("#cp-panel").is_hidden():
        fab.click()
        page.wait_for_timeout(400)

    if not page.locator("#cp-panel").is_visible():
        masalah.append("#cp-panel gagal terbuka setelah klik #cp-fab")
        return masalah

    box_panel = page.locator("#cp-panel").bounding_box()
    if not box_panel or box_panel["x"] < -1 or box_panel["y"] < -1 or box_panel["x"] + box_panel["width"] > vw + 1 or box_panel["y"] + box_panel["height"] > vh + 1:
        masalah.append(f"#cp-panel keluar viewport ({vw}x{vh}): {box_panel}")

    sw = page.evaluate("() => document.documentElement.scrollWidth")
    if sw > vw + 1:
        masalah.append(f"overflow horizontal saat #cp-panel terbuka: {sw} > {vw}")

    tutup = page.locator("#cp-tutup")
    if tutup.count() > 0 and tutup.is_visible():
        tutup.click()
        page.wait_for_timeout(400)
        panel_loc = page.locator("#cp-panel")
        if not panel_loc.is_hidden() or panel_loc.get_attribute("hidden") is None:
            masalah.append("#cp-tutup tidak menutup #cp-panel (hidden tidak terpasang)")
        sw_tutup = page.evaluate("() => document.documentElement.scrollWidth")
        if sw_tutup > vw + 1:
            masalah.append(f"overflow horizontal setelah #cp-panel ditutup: {sw_tutup} > {vw}")

    return masalah


def jalankan_qa(
    lebar_list: list[int],
    bahasa_list: list[str],
    simpan_foto: str | None = None,
    rute_filter: list[tuple[str, str]] | None = None,
) -> tuple[bool, list[str]]:
    base_url, tutup_server = _siapkan_server_luring()
    out_dir = Path(simpan_foto) if simpan_foto else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    rute_list = rute_filter or RUTE_UTAMA
    gagal: list[str] = []
    chrome = _cari_chrome()

    try:
        with sync_playwright() as p:
            kwargs = {"headless": True}
            if chrome:
                kwargs["executable_path"] = chrome
            browser = p.chromium.launch(**kwargs)
            try:
                for bhs in bahasa_list:
                    for lebar in lebar_list:
                        tinggi = 844 if lebar < 900 else 900
                        ctx = browser.new_context(viewport={"width": lebar, "height": tinggi})
                        ctx.add_cookies([{"name": "bahasa", "value": bhs, "url": base_url}])
                        page = ctx.new_page()
                        desktop = lebar >= 901

                        for path, slug in rute_list:
                            sep = "&" if "?" in path else "?"
                            url = f"{base_url}{path}{sep}lang={bhs}"
                            masalah = _cek_halaman(page, url, lebar, desktop)
                            for m in masalah:
                                gagal.append(f"[{bhs} {lebar}px {path}] {m}")

                            if out_dir:
                                full = lebar in (390, 1440) and slug in ("feed", "watchlist", "review", "saham-ringkasan", "saham-keu", "valuasi", "peringatan-ditahan", "jejak")
                                if full or lebar in (768, 1024) and slug in ("feed", "saham-ringkasan", "valuasi"):
                                    page.screenshot(path=str(out_dir / f"{slug}-{bhs}-{lebar}.png"), full_page=True)

                        # Uji laci di ponsel pada perwakilan lebar < 900
                        if not desktop:
                            for m in _cek_laci_ponsel(page, f"{base_url}/?lang={bhs}"):
                                gagal.append(f"[{bhs} {lebar}px LACI] {m}")
                            if out_dir and lebar == 390 and bhs == "en":
                                page.goto(f"{base_url}/?lang=en", wait_until="domcontentloaded")
                                page.locator("[data-buka-menu]").first.click()
                                page.wait_for_timeout(200)
                                page.screenshot(path=str(out_dir / f"laci-{bhs}-{lebar}.png"))
                                page.keyboard.press("Escape")

                        # Uji #cp-fab dan #cp-panel di 390 dan 1440 (serta di halaman saham)
                        if lebar in (390, 1440):
                            for r_chat in ("/", "/saham/2330?tab=ringkasan"):
                                for m in _cek_panel_chat(page, f"{base_url}{r_chat}"):
                                    gagal.append(f"[{bhs} {lebar}px CHAT {r_chat}] {m}")

                        ctx.close()
            finally:
                browser.close()
    finally:
        tutup_server()

    return len(gagal) == 0, gagal


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lebar", nargs="+", type=int, default=[390, 1440])
    ap.add_argument("--bahasa", nargs="+", default=["en", "zh", "id"])
    ap.add_argument("--simpan-foto", default=None, help="Simpan tangkapan layar ke folder ini")
    ap.add_argument("--izin-gagal", action="store_true", help="Tetap keluar 0 meski ada temuan (untuk baseline 'sebelum')")
    args = ap.parse_args()

    ok, gagal = jalankan_qa(args.lebar, args.bahasa, simpan_foto=args.simpan_foto)
    if ok:
        print(f"QA responsif LOLOS ({len(RUTE_UTAMA)} rute x {len(args.bahasa)} bahasa x {len(args.lebar)} lebar = 0 temuan).")
        return 0

    print(f"QA responsif GAGAL ({len(gagal)} temuan):")
    for g in gagal:
        print(f"  - {g}")
    return 0 if args.izin_gagal else 1


if __name__ == "__main__":
    raise SystemExit(main())
