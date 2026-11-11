"""Kamus i18n putaran 3 (Antigravity).

Memuat teks untuk fitur:
- V1: tab Valuation cepat dan pita beta sementara
- S1: pencarian emiten berdasarkan kode atau nama
- C1a: tautan Tanya FEAF
"""

from __future__ import annotations

T: dict[str, tuple[str, str, str]] = {
    # V1: tab Valuation cepat dan beta sementara
    "va.beta_sementara_pita": (
        "Beta is being calculated from official daily prices. Reload this page in a few minutes.",
        "Beta 正從官方每日收盤價計算中，請於數分鐘後重新整理此頁面。",
        "Beta sedang dihitung dari harga resmi. Muat ulang halaman ini dalam beberapa menit.",
    ),
    "va.beta.sedang_dihitung": (
        "beta 1.0 temporary, official beta is being computed",
        "臨時 Beta 1.0，正式 Beta 計算中",
        "beta 1.0 sementara, beta resmi sedang dihitung",
    ),
    "va.beta_sementara_label": (
        "Temporary beta 1.0 (computing...)",
        "臨時 Beta 1.0（計算中...）",
        "Beta sementara 1,0 (sedang dihitung...)",
    ),
    # S1: pencarian emiten berdasarkan kode atau nama
    "sh.cari_placeholder": (
        "Code or name (2330, TSMC, 台積電)",
        "代號或名稱（2330、TSMC、台積電）",
        "Kode atau nama (2330, TSMC, 台積電)",
    ),
    "sh.tidak_ditemukan": (
        "Issuer '{q}' not found.",
        "查無「{q}」相關上市櫃公司。",
        "Emiten '{q}' tidak ditemukan.",
    ),
    "sh.hasil_cari": (
        "Search results for '{q}'",
        "「{q}」的搜尋結果",
        "Hasil pencarian untuk '{q}'",
    ),
    "sh.pilih_emiten": (
        "Select issuer:",
        "請選擇上市櫃公司：",
        "Pilih emiten:",
    ),
    "sh.ditemukan_n": (
        "{n} issuers found",
        "找到 {n} 家公司",
        "Ditemukan {n} emiten",
    ),
}
