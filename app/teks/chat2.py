"""Trilingual strings for Round 5 Ask FEAF chat panel, multi-turn recap, and menu tools (prefix cp.)."""

from __future__ import annotations

# kunci: (English, 繁體中文, Bahasa Indonesia)
T: dict[str, tuple[str, str, str]] = {
    # --- Recap (C2) ---
    "cp.recap.kosong": (
        "No verified conversation turns yet to summarize. Ask a question about a stock or menu first.",
        "目前尚無已驗證的對話紀錄可供摘要。請先針對個股或選單提出問題。",
        "Belum ada giliran percakapan sah untuk diringkas. Ajukan pertanyaan tentang saham atau menu terlebih dahulu.",
    ),
    "cp.recap.judul": (
        "Conversation recap:",
        "對話重點摘要：",
        "Ringkasan percakapan:",
    ),

    # --- Menu tool templates (C3) ---
    "cp.tpl.feed": (
        "Alerts feed ({total} total: {terbit} published, {ditahan} held for review, {dilewati} archived). Latest: {isi}.",
        "警示動態（共 {total} 則：{terbit} 則已發布、{ditahan} 則待審查、{dilewati} 則已歸檔）。最新項目：{isi}。",
        "Feed peringatan (total {total}: {terbit} terbit, {ditahan} ditahan untuk review, {dilewati} diarsipkan). Terbaru: {isi}.",
    ),
    "cp.tpl.feed_kosong": (
        "No announcements matching that status in the alerts feed yet.",
        "警示動態中尚無符合該狀態的公告。",
        "Belum ada pengumuman dengan status tersebut di feed peringatan.",
    ),
    "cp.tpl.peringatan": (
        "Announcement {id} ({kode}, {tgl}): {judul} — status {status} ({state}), type {jenis}, moderate signal level {tingkat}. Reason: {alasan}. Checks passed: {lolos}/{total_cek}{angka_teks}.",
        "公告 {id}（{kode}，{tgl}）：{judul} — 狀態 {status}（{state}），類型 {jenis}，穩健型訊號等級 {tingkat}。原因：{alasan}。檢查通過：{lolos}/{total_cek}{angka_teks}。",
        "Pengumuman {id} ({kode}, {tgl}): {judul} — status {status} ({state}), jenis {jenis}, tingkat sinyal moderat {tingkat}. Alasan: {alasan}. Pemeriksaan lolos: {lolos}/{total_cek}{angka_teks}.",
    ),
    "cp.tpl.jejak": (
        "Audit trail {id}: {langkah} steps in {durasi} ms, {model} model call(s) ({token_masuk} input / {token_keluar} output tokens), fallback: {cadangan}. States: {states}.",
        "稽核軌跡 {id}：共 {langkah} 個步驟，耗時 {durasi} 毫秒，模型呼叫 {model} 次（輸入 {token_masuk}／輸出 {token_keluar} token），備援模式：{cadangan}。狀態序列：{states}。",
        "Jejak audit {id}: {langkah} langkah dalam {durasi} ms, {model} panggilan model (token masuk {token_masuk} / keluar {token_keluar}), cadangan: {cadangan}. Urutan state: {states}.",
    ),
    "cp.tpl.review": (
        "Review queue has {jumlah} item(s) waiting for human decision: {isi}. To approve or archive, open /review.",
        "人工審查佇列目前有 {jumlah} 個待決項目：{isi}。若要核准或歸檔，請開啟 /review。",
        "Antrean review memiliki {jumlah} pengumuman yang menunggu keputusan manusia: {isi}. Untuk menyetujui atau mengarsipkan, buka /review.",
    ),
    "cp.tpl.review_kosong": (
        "The human review queue is currently empty (0 items waiting).",
        "目前人工審查佇列為空（0 個待審項目）。",
        "Antrean review manusia saat ini kosong (0 item menunggu).",
    ),
    "cp.tpl.ambang": (
        "Triage confidence thresholds by clause: {isi}. Moderate risk profile equity-guarantee alert threshold: {jamin_pct}%.",
        "各條款分類信心門檻：{isi}。穩健型風險設定之背書保證占淨值警戒門檻：{jamin_pct}%。",
        "Ambang keyakinan triase per pasal: {isi}. Ambang waspada penjaminan terhadap ekuitas (profil moderat): {jamin_pct}%.",
    ),
    "cp.tpl.watchlist": (
        "Watchlist has {jumlah} stock(s): {isi}. To add or remove stocks, open /watchlist.",
        "自選股清單目前有 {jumlah} 檔股票：{isi}。若要新增或移除股票，請開啟 /watchlist。",
        "Watchlist memuat {jumlah} saham: {isi}. Untuk menambah atau menghapus saham, buka /watchlist.",
    ),
    "cp.tpl.watchlist_kosong": (
        "The watchlist is currently empty.",
        "目前自選股清單為空。",
        "Watchlist saat ini kosong.",
    ),

    # --- Chat panel & page UI (C4) ---
    "cp.tombol": ("Ask FEAF", "詢問 FEAF", "Tanya FEAF"),
    "cp.judul": ("Ask FEAF", "詢問 FEAF", "Tanya FEAF"),
    "cp.sub": (
        "Read-only assistant · every figure verified",
        "唯讀研究助理 · 每個數字皆經查核",
        "Asisten hanya-baca · setiap angka diverifikasi",
    ),
    "cp.recap": ("Recap", "重點摘要", "Recap"),
    "cp.baru": ("New chat", "新對話", "Percakapan baru"),
    "cp.tutup": ("Close", "關閉", "Tutup"),
    "cp.melihat.saham": ("Viewing: {kode}", "正在查看：{kode}", "Sedang melihat: {kode}"),
    "cp.melihat.peringatan": ("Alert {id}", "警示 {id}", "Peringatan {id}"),
    "cp.melihat.jejak": ("Audit trail {id}", "稽核軌跡 {id}", "Jejak {id}"),
    "cp.melihat.halaman": ("Page: {halaman}", "頁面：{halaman}", "Halaman: {halaman}"),
    "cp.placeholder": (
        "Ask about this stock, filing, valuation, or menu…",
        "詢問此個股、公告、評價或選單…",
        "Tanya soal saham ini, pengumuman, valuasi, atau menu…",
    ),
    "cp.kirim": ("Send", "送出", "Kirim"),
    "cp.memuat": ("Checking tools…", "正在查詢工具…", "Memeriksa alat…"),
    "cp.galat_jaringan": (
        "Could not reach the server. Please try again.",
        "無法連線至伺服器，請稍後再試。",
        "Tidak dapat menghubungi server. Silakan coba lagi.",
    ),
    "cp.galat_akses": (
        "Access code required for this action.",
        "此操作需要存取碼。",
        "Tindakan ini memerlukan kode akses.",
    ),
    "cp.sumber": ("Sources:", "資料來源：", "Sumber:"),
    "cp.buka_halaman": ("Open {jalur} →", "開啟 {jalur} →", "Buka {jalur} →"),
    "cp.jejak": ("Trace", "軌跡", "Jejak"),
    "cp.catatan_tolak": (
        "Note: the model draft failed verification; showing verified template answer instead.",
        "註：模型草稿未通過驗證，改顯示已核對的範本回答。",
        "Catatan: draf model ditolak pemeriksa; menampilkan jawaban template terverifikasi.",
    ),
    "cp.kosong": (
        "Ask a question or choose a suggestion below. Every figure is checked against tool results.",
        "請輸入問題或選擇下方建議。回答中的每個數字皆與工具結果核對。",
        "Ajukan pertanyaan atau pilih saran di bawah. Setiap angka diperiksa terhadap hasil alat.",
    ),
    "cp.saran.saham.1": ("Price & valuation", "股價與評價", "Harga & valuasi"),
    "cp.saran.saham.1.q": (
        "What are the latest price and valuation of {kode}?",
        "{kode} 的最新股價與評價為何？",
        "Berapa harga terbaru dan valuasi {kode}?",
    ),
    "cp.saran.saham.2": ("Latest financials", "最新財報", "Laporan terbaru"),
    "cp.saran.saham.2.q": (
        "What are the latest revenue, net income, EPS, and margins of {kode}?",
        "{kode} 最新的營收、淨利、EPS 與利潤率為何？",
        "Berapa pendapatan, laba bersih, EPS, dan margin terbaru {kode}?",
    ),
    "cp.saran.saham.3": ("Announcements", "重大訊息", "Pengumuman"),
    "cp.saran.saham.3.q": (
        "What are the recent material announcements of {kode}?",
        "{kode} 近期有哪些重大訊息公告？",
        "Apa saja pengumuman material terbaru {kode}?",
    ),
    "cp.saran.peringatan.1": ("Why was this held?", "為何被暫緩？", "Kenapa ini ditahan?"),
    "cp.saran.peringatan.1.q": (
        "Why was this announcement held or published?",
        "為什麼這則公告會被暫緩或發布？",
        "Kenapa ini ditahan atau diterbitkan?",
    ),
    "cp.saran.peringatan.2": ("What does it mean for valuation?", "對評價有何意義？", "Apa artinya untuk valuasi?"),
    "cp.saran.peringatan.2.q": (
        "What does this announcement mean for valuation?",
        "這則公告對評價代表什麼意義？",
        "Apa artinya untuk valuasi?",
    ),
    "cp.saran.peringatan.3": ("Show its audit trail", "顯示稽核軌跡", "Tunjukkan jejaknya"),
    "cp.saran.peringatan.3.q": (
        "Show the audit trail of this announcement.",
        "請顯示這則公告的稽核軌跡。",
        "Tunjukkan jejaknya.",
    ),
    "cp.saran.feed.1": ("What's new today?", "今天有什麼新公告？", "Apa yang baru hari ini?"),
    "cp.saran.feed.1.q": (
        "What are the latest alerts today?",
        "今天有哪些最新警示公告？",
        "Apa yang baru hari ini di peringatan?",
    ),
    "cp.saran.feed.2": ("Waiting for review", "待審查項目", "Apa yang menunggu review?"),
    "cp.saran.feed.2.q": (
        "What items are waiting for human review?",
        "目前有哪些項目正在等待人工審查？",
        "Apa saja yang menunggu review?",
    ),
    "cp.saran.feed.3": ("Watchlist stocks", "自選股清單", "Daftar watchlist"),
    "cp.saran.feed.3.q": (
        "Which stocks are on the watchlist?",
        "目前自選股清單中有哪些股票？",
        "Saham apa saja yang ada di watchlist?",
    ),
    "cp.saran.review.1": ("What is waiting for review?", "有哪些待審查項目？", "Apa saja yang menunggu review?"),
    "cp.saran.review.1.q": (
        "What items are waiting for review?",
        "目前有哪些項目等待審查？",
        "Apa saja yang menunggu review?",
    ),
    "cp.saran.review.2": ("Triage thresholds", "分類門檻", "Ambang triase"),
    "cp.saran.review.2.q": (
        "What are the current triage thresholds?",
        "目前的分類門檻設定為何？",
        "Berapa ambang triase saat ini?",
    ),
    "cp.saran.review.3": ("What's new today?", "最新警示", "Apa yang baru hari ini?"),
    "cp.saran.review.3.q": (
        "What are the latest alerts today?",
        "今天有哪些最新警示公告？",
        "Apa yang baru hari ini?",
    ),
}
