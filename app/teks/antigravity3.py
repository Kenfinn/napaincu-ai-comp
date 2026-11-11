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
}
