"""Kunci terjemahan tambahan untuk pekerjaan Antigravity (Putaran 2: R3, D-a, dll.)."""

from __future__ import annotations

T: dict[str, tuple[str, str, str]] = {
    # --- R3: Kunci baca ---
    "kunci.judul": ("Access Code Required", "需要存取碼", "Perlu Kode Akses"),
    "kunci.kicker": ("Restricted Access", "存取限制", "Akses Terbatas"),
    "kunci.penjelasan": (
        "Enter the access code to access FEAF research and analysis pages.",
        "請輸入存取碼以瀏覽 FEAF 研究與分析頁面。",
        "Masukkan kode akses untuk membuka halaman riset dan analisis FEAF.",
    ),
    "kunci.label_kode": ("Access code", "存取碼", "Kode akses"),
    "kunci.tombol": ("Unlock", "解鎖", "Buka Akses"),
    "kunci.placeholder": ("Enter access code...", "請輸入存取碼...", "Masukkan kode akses..."),

    # --- D-a: Lingkup tampilan feed & review ---
    "feed.lingkup.watchlist": ("Watchlist", "關注清單", "Watchlist"),
    "feed.lingkup.semua": ("All Issuers", "全部發行公司", "Semua Emiten"),
    "feed.tampil_dari": (
        "Showing {n} of {total} announcements",
        "顯示 {total} 則公告中的 {n} 則",
        "Menampilkan {n} dari {total} pengumuman",
    ),
    "rv.lingkup.watchlist": ("Watchlist", "關注清單", "Watchlist"),
    "rv.lingkup.semua": ("All Issuers", "全部發行公司", "Semua Emiten"),

    # --- D-c: Utang lancar ---
    "va.warn.utang_lancar_tidak_tersedia": (
        "Current portion of long-term debt is not published separately by FinMind; debt may be understated.",
        "FinMind 未單獨揭露一年內到期長期負債；計入的負債可能偏低。",
        "Bagian lancar utang jangka panjang tidak diterbitkan terpisah oleh FinMind; utang mungkin tercatat lebih rendah.",
    ),

    # --- D-b: Mode valuasi otomatis + asumsi ---
    "va.mode.otomatis_asumsi": (
        "Automatic + team assumptions",
        "自動＋團隊假設",
        "Otomatis + asumsi tim",
    ),
    "va.ditimpa_label": (
        "Overridden from team file:",
        "自團隊設定檔覆蓋：",
        "Ditimpa dari berkas tim:",
    ),

    # --- B3: Sitasi MOPS ---
    "sh.sumber_resmi_mops": (
        "Data: FinMind (replicated from MOPS). Official source: MOPS, links per column.",
        "資料來源：FinMind（轉載自 MOPS 公開資訊觀測站）。官方來源：MOPS，詳見各欄連結。",
        "Data: FinMind (salinan dari MOPS). Sumber resmi: MOPS, tautan per kolom.",
    ),
    "sh.tautan_mops": (
        "MOPS ↗",
        "MOPS ↗",
        "MOPS ↗",
    ),
}


