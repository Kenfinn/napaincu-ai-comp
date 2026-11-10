"""Tiga bahasa: English, 繁體中文, Bahasa Indonesia.

Satu kamus untuk seluruh teks — tampilan maupun pesan yang ditulis agent. Agent
menyimpan **kode pesan + parameter** di jejak audit, bukan hanya kalimat jadi, sehingga
jejak yang sama bisa dibaca juri Taiwan, juri internasional, dan tim kita.

Teks Indonesia tetap ikut disimpan di jejak sebagai kalimat utuh (kolom `alasan`,
`nama`, `tahap`), supaya berkas JSON mentah tetap terbaca tanpa kamus ini dan jejak
lama yang belum punya kode tetap tampil.

Menambah teks: tambahkan satu kunci dengan ketiga bahasa. Tes memastikan tidak ada
kunci yang kurang satu bahasa.
"""

from __future__ import annotations

BAHASA = {"en": "English", "zh": "繁體中文", "id": "Bahasa Indonesia"}
BAWAAN = "en"
URUTAN = ("en", "zh", "id")

# kunci: (English, 繁體中文, Bahasa Indonesia)
_T: dict[str, tuple[str, str, str]] = {
    # --- B2/D3 (Antigravity) ---
    "va.mode.otomatis": ("Automatic", "自動計算", "Otomatis"),
    "va.mode.manual": ("Manual", "手動工作表", "Manual"),
    "va.mode.tidak_berlaku": ("Not applicable", "不適用", "Tidak berlaku"),
    "va.mode.tidak_bisa": ("Cannot be computed", "無法計算", "Tidak bisa dihitung"),
    "va.dibangun_pada": ("Built {waktu}", "建立於 {waktu}", "Dibangun {waktu}"),
    "va.beta_label": ("Beta (2y weekly vs TAIEX)", "Beta（2 年週報酬對加權指數）", "Beta (mingguan 2 tahun vs TAIEX)"),
    "va.beta_cadangan_label": ("Fallback beta 1.0 ({alasan})", "備用 Beta 1.0（{alasan}）", "Beta cadangan 1,0 ({alasan})"),
    "va.beta_terhitung_label": (
        "Beta {beta} ({n} weekly pairs vs TAIEX)",
        "Beta {beta}（與加權指數共 {n} 週配對）",
        "Beta {beta} ({n} pasangan minggu vs TAIEX)",
    ),
    "va.otomatis.keuangan": (
        "Financial-sector issuer ({industri}): a free-cash-flow (FCFF) DCF model does not apply because debt and deposits are operating raw materials rather than financing.",
        "金融保險業公司（{industri}）：自由現金流量（FCFF）折現模型不適用，因其負債與存款屬於營運原料而非單純籌資。",
        "Emiten sektor keuangan ({industri}): model DCF berbasis arus kas bebas (FCFF) tidak berlaku karena utang dan simpanan merupakan bahan baku operasi, bukan pendanaan biasa.",
    ),
    "va.otomatis.tanpa_harga": (
        "Market closing price for {kode} is not available from TWSE/TPEx OpenAPI.",
        "無法自 TWSE/TPEx OpenAPI 取得 {kode} 的收盤價。",
        "Harga penutupan pasar untuk {kode} belum tersedia dari OpenAPI TWSE/TPEx.",
    ),
    "va.otomatis.tanpa_saham": (
        "Issued share count for {kode} is zero or unavailable in both exchange profile and balance sheet.",
        "交易所基本資料與資產負債表中皆無 {kode} 的已發行股數（或為零）。",
        "Jumlah saham beredar untuk {kode} nol atau tidak tersedia baik di profil bursa maupun neraca.",
    ),
    "va.otomatis.kurang_3_tahun": (
        "Fewer than 3 full fiscal years of operating cash flow and capital expenditure data are available ({n} year(s) found; 3 required).",
        "完整會計年度的營業現金流與資本支出資料少於 3 年（僅找到 {n} 年，需滿 3 年）。",
        "Data arus kas operasi dan belanja modal tahun fiskal penuh kurang dari 3 tahun (ditemukan {n} tahun; wajib minimal 3 tahun).",
    ),
    "va.otomatis.tanpa_neraca": (
        "Balance sheet data (cash and debt) for {kode} is unavailable.",
        "無法取得 {kode} 的資產負債表（現金與負債）資料。",
        "Data neraca (kas dan utang) untuk {kode} belum tersedia.",
    ),
    "va.otomatis.fcff_negatif": (
        "Latest free cash flow to the firm (FCFF {tahun}) is non-positive ({fcff} NT$ million), so an implied perpetual growth rate cannot be meaningfully solved.",
        "最近一期企業自由現金流量（{tahun} 年 FCFF = {fcff} 百萬新台幣）為零或負值，無法求解有意義的隱含永續成長率。",
        "Arus kas bebas perusahaan terakhir (FCFF {tahun} = {fcff} juta NTD) bernilai nol atau negatif, sehingga tingkat pertumbuhan abadi tersirat tidak bermakna.",
    ),
    "va.otomatis.ev_negatif": (
        "Enterprise value is non-positive ({ev} NT$ million: cash exceeds market cap plus debt), so reverse DCF does not apply.",
        "企業價值為零或負值（{ev} 百萬新台幣：現金高於市值加負債），不適用反向 DCF。",
        "Nilai perusahaan bernilai nol atau negatif ({ev} juta NTD: kas melebihi kapitalisasi pasar ditambah utang), sehingga reverse DCF tidak berlaku.",
    ),
    "va.beta.kurang_data": (
        "fewer than 52 weekly return pairs ({n} week(s))",
        "週報酬配對少於 52 週（僅 {n} 週）",
        "pasangan return mingguan kurang dari 52 minggu ({n} minggu)",
    ),
    "va.beta.gagal_ambil": (
        "price history unavailable from official exchange endpoint",
        "無法自交易所官方取得歷史股價",
        "riwayat harga dari bursa resmi tidak tersedia",
    ),
    "va.beta.varians_nol": (
        "market index variance is zero",
        "市場指數變異數為零",
        "varians indeks pasar bernilai nol",
    ),
    "va.warn.bunga_pakai_bayar": (
        "InterestExpense was absent in cash flow statement; used PayTheInterest (cash interest paid) instead.",
        "現金流量表缺少利息費用（InterestExpense），改用支付之利息（PayTheInterest）。",
        "Pos InterestExpense tidak ada di laporan arus kas; menggunakan PayTheInterest (bunga kas yang dibayar).",
    ),
    "va.warn.bunga_nol": (
        "Both InterestExpense and PayTheInterest were absent; interest expense defaulted to 0.",
        "現金流量表同時缺少利息費用與支付之利息，利息費用設為 0。",
        "Pos InterestExpense maupun PayTheInterest tidak tersedia; beban bunga diisi 0.",
    ),
    "va.warn.saham_neraca": (
        "Issued share count derived from balance sheet CapitalStock (par NT$10) because exchange profile share count was unavailable.",
        "因交易所基本資料無已發行股數，改由資產負債表股本（每股面額 10 元）推算股數。",
        "Jumlah saham beredar dihitung dari CapitalStock neraca (nominal NT$10) karena data lembar profil bursa tidak tersedia.",
    ),
    "va.warn.tanpa_utang": (
        "Issuer has zero interest-bearing debt on the balance sheet; cost of debt is 0% and WACC equals cost of equity.",
        "資產負債表上無付息負債；負債資金成本為 0%，WACC 等於權益資金成本。",
        "Emiten tidak memiliki utang berbunga di neraca; biaya utang 0% dan WACC sama dengan biaya ekuitas.",
    ),
    "va.warn.pajak_tidak_normal": (
        "Pre-tax income or tax expense in fiscal year {tahun} was negative or abnormal; effective tax shield set to 0%.",
        "{tahun} 會計年度稅前淨利或所得稅費用為負值或異常，有效稅盾設為 0%。",
        "Laba sebelum pajak atau beban pajak tahun fiskal {tahun} negatif atau tidak normal; perisai pajak efektif disetel 0%.",
    ),
    "va.warn.utang_lancar_gabung": (
        "FinMind TaiwanStockBalanceSheet folds current portion of long-term debt into OtherCurrentLiabilities; current_portion_lt_debt records ShorttermBorrowings when reported separately.",
        "FinMind 資產負債表將一年內到期長期負債併入其他流動負債；流動付息負債欄位記錄單獨揭露之短期借款。",
        "Dataset neraca FinMind menggabungkan bagian lancar utang jangka panjang ke OtherCurrentLiabilities; current_portion_lt_debt mencatat ShorttermBorrowings bila dilaporkan terpisah.",
    ),
    "va.peringatan_judul": ("Data notes & adjustments", "資料說明與調整", "Catatan & penyesuaian data"),
    # --- umum / menu -----------------------------------------------------------
    "merek.sub": ("Investment Assistant", "投資助理", "Asisten Investasi"),
    "nav.watchlist": ("Watchlist", "自選股", "Watchlist"),
    "nav.feed": ("Alerts", "警示", "Peringatan"),
    "nav.valuasi": ("Valuation {kode}", "評價 {kode}", "Valuasi {kode}"),
    "nav.api": ("API", "API", "API"),
    "nav.review": ("Review", "人工審查", "Review"),
    "rv.kicker": ("Human gate · brief p. 7", "人工把關 · 簡報第 7 頁", "Gerbang manusia · brief hal. 7"),
    "rv.judul": ("Held for review", "待人工審查", "Antrean review"),
    "rv.isi": (
        "Filings the agent did not publish because a check failed or it was unsure. Nothing here is published without your decision, and every decision is recorded in the audit trail.",
        "代理因檢查未通過或不確定而未發布的公告。未經您決定，此處內容不會發布；每項決定都會記錄在稽核軌跡中。",
        "Pengumuman yang tidak diterbitkan agent karena ada pemeriksaan yang gagal atau agent ragu. Tidak ada yang terbit dari sini tanpa keputusanmu, dan setiap keputusan tercatat di jejak audit."),
    "rv.kosong": ("Nothing waiting for review.", "目前沒有待審查的項目。", "Tidak ada yang menunggu review."),
    "rv.sebab": ("Why it was held", "暫緩原因", "Kenapa ditahan"),
    "rv.catatan": ("Note (required)", "備註（必填）", "Catatan (wajib)"),
    "rv.setujui": ("✔ Approve and publish", "✔ 核准並發布", "✔ Setujui dan terbitkan"),
    "rv.arsipkan": ("✕ Archive", "✕ 歸檔", "✕ Arsipkan"),
    "rv.hanya_arsip": ("Only archiving is possible: the figure or quotation could not be found in the document (a sign of fabrication, not doubt).",
                       "僅能歸檔：文件中找不到該數字或引文（這是捏造的跡象，而非不確定）。",
                       "Hanya bisa diarsipkan: angka atau kutipannya tidak ditemukan di dokumen (tanda dikarang, bukan keraguan)."),
    "rv.tanpa_angka": ("No figure to publish: the agent found no amount with its source sentence. Archive it, or check the filing yourself.",
                       "沒有可發布的數字：代理未找到附帶原文句子的金額。可歸檔，或自行查閱公告。",
                       "Tidak ada angka untuk diterbitkan: agent tidak menemukan jumlah beserta kalimat sumbernya. Arsipkan, atau cek pengumumannya sendiri."),
    "rv.riwayat": ("Decision history", "決定紀錄", "Riwayat keputusan"),
    "rv.k_waktu": ("Time (UTC)", "時間（UTC）", "Waktu (UTC)"),
    "rv.k_keputusan": ("Decision", "決定", "Keputusan"),
    "rv.kp.setujui": ("approved", "核准", "disetujui"),
    "rv.kp.arsipkan": ("archived", "歸檔", "diarsipkan"),
    "rv.jenis.verifikasi": ("A verifier check failed", "驗證未通過", "Ada pemeriksaan yang gagal"),
    "rv.jenis.tanpa_valuasi": ("No valuation model for this issuer yet", "此公司尚無評價模型", "Belum ada model valuasi untuk emiten ini"),
    "rv.jenis.tanpa_angka": ("No figure with a source sentence", "無附帶原文句子的數字", "Tidak ada angka bersumber"),
    "rv.jenis.keyakinan": ("Low triage confidence", "分類信心不足", "Keyakinan triase rendah"),
    "msg.review_ok": ("Decision recorded: {kode} {keputusan}.", "已記錄決定：{kode} {keputusan}。", "Keputusan tercatat: {kode} {keputusan}."),
    "msg.review_catatan": ("Write a short note explaining the decision.", "請填寫簡短備註說明決定理由。", "Tulis catatan singkat alasan keputusan."),
    "msg.review_tidak_boleh": ("This case can only be archived.", "此項目僅能歸檔。", "Kasus ini hanya bisa diarsipkan."),
    "al.ditahan": (
        "<b>Not published: held for human review.</b> {sebab} <a href=\"/review\">Open the review queue →</a>",
        "<b>未發布：等待人工審查。</b>{sebab} <a href=\"/review\">開啟審查佇列 →</a>",
        "<b>Tidak diterbitkan: menunggu review manusia.</b> {sebab} <a href=\"/review\">Buka antrean review →</a>"),
    "al.disetujui_manusia": ("<b>Published after human approval.</b> {catatan}", "<b>經人工核准後發布。</b>{catatan}",
                             "<b>Terbit setelah disetujui manusia.</b> {catatan}"),
    "al.angka_disetujui": ("Approved figure (no valuation recompute)", "經核准的數字（未重新計算評價）",
                           "Angka yang disetujui (tanpa hitung ulang valuasi)"),
    "nav.saham": ("My stocks", "我的自選股", "Saham saya"),
    "nav.saham_kosong": ("Add stocks in Watchlist →", "請至自選股新增 →", "Tambah saham di Watchlist →"),
    "nav.bahasa": ("Language", "語言", "Bahasa"),
    "status.mesin": ("Reasoning engine", "推理引擎", "Mesin penalar"),
    "status.aturan": ("rule-based reasoner", "規則式推理", "penalar-aturan"),
    "status.model_aktif": ("Model active.", "模型已啟用。", "Model aktif."),
    "status.tanpa_kunci": ("No API key: rule-based reasoner.", "無 API 金鑰：使用規則式推理。",
                           "Tanpa kunci API — penalar berbasis aturan."),
    "status.sumber": ("Data source:", "資料來源：", "Sumber data:"),
    "sumber.nyata": ("live", "真實資料", "nyata"),
    "sumber.fixture": ("sample", "範例資料", "fixture"),
    "status.tarik": ("Last fetch", "最近擷取", "Penarikan terakhir"),
    "status.belum": ("never", "尚未擷取", "belum pernah"),
    "status.tarik_gagal": ("Fetch failed. Showing the last stored data.",
                           "擷取失敗，顯示最近儲存的資料。",
                           "Gagal menarik. Memakai data terakhir yang tersimpan."),
    "pita.fixture": (
        "<b>Sample data.</b> This screen uses four test cases in <span class=\"mono\">data/fixtures/</span>. "
        "Press <b>Check now</b> to fetch real filings for your watchlist from the exchanges' official "
        "OpenAPI. Real data then replaces the samples, read by exactly the same code.",
        "<b>範例資料。</b>此畫面使用 <span class=\"mono\">data/fixtures/</span> 中的四個測試案例。"
        "按下<b>立即檢查</b>，即從交易所官方 OpenAPI 擷取自選股的真實公告，之後改用真實資料，讀取程式完全相同。",
        "<b>Data contoh.</b> Layar ini memakai empat kasus uji di <span class=\"mono\">data/fixtures/</span>. "
        "Tekan <b>Periksa sekarang</b> untuk menarik pengumuman asli emiten di watchlist dari OpenAPI resmi "
        "bursa. Setelah itu data asli yang dipakai, lewat kode baca yang sama persis."),
    "tombol.periksa": ("⟳ Check now", "⟳ 立即檢查", "⟳ Periksa sekarang"),
    "tombol.proses_ulang": ("Re-run", "重新處理", "Proses ulang"),
    "ya": ("yes", "是", "ya"),
    "tidak": ("no", "否", "tidak"),

    # --- status akhir ------------------------------------------------------------
    "st.terbit": ("Published", "已發布", "Terbit"),
    "st.ditolak": ("Rejected", "已拒絕", "Ditolak"),
    "st.ditahan": ("Held for review", "待人工審查", "Ditahan untuk review"),
    "st.dilewati": ("Archived", "已歸檔", "Diarsipkan"),

    # --- feed --------------------------------------------------------------------
    "feed.kicker": ("MOPS filings · processed by the agent", "MOPS 重大訊息 · 由代理處理",
                    "Pengumuman MOPS · diproses agent"),
    "feed.judul": ("Alerts", "警示", "Peringatan"),
    "feed.kenapa": ("Why four numbers, not one", "為何是四個數字而非一個", "Kenapa empat angka, bukan satu"),
    "feed.kenapa_isi": (
        "Two of the three endings are not “published”. A system that cannot stop and hand over to a human is not an agent; it is a pipeline.",
        "三種結果中有兩種不是「發布」。不會停下來交給人工的系統不是代理，而只是流水線。",
        "Dua dari tiga akhir bukan “terbit”. Sistem yang tidak bisa berhenti dan menyerahkan ke manusia bukan agent — itu pipeline."),
    "feed.kenapa": ("Why three numbers, not one", "為何是三個數字而非一個", "Kenapa tiga angka, bukan satu"),
    "feed.kosong": ("No filings to process yet.", "尚無可處理的公告。", "Belum ada pengumuman untuk diproses."),
    "feed.g": ("g", "g", "g"),

    # --- watchlist -----------------------------------------------------------------
    "wl.kicker": ("Stocks the agent watches", "代理監控的股票", "Saham yang dipantau agent"),
    "wl.judul": ("Watchlist", "自選股", "Watchlist"),
    "wl.kode": ("Stock code", "股票代號", "Kode saham"),
    "wl.contoh": ("e.g. 2454", "例：2454", "mis. 2454"),
    "wl.tambah": ("+ Add", "+ 新增", "+ Tambah"),
    "wl.hapus": ("Remove", "移除", "Hapus"),
    "wl.k_kode": ("Code", "代號", "Kode"),
    "wl.k_nama": ("Name", "名稱", "Nama"),
    "wl.k_valuasi": ("Valuation", "評價", "Valuasi"),
    "wl.k_jumlah": ("Stored filings", "已存公告", "Pengumuman tersimpan"),
    "wl.k_terakhir": ("Latest", "最新", "Terakhir"),
    "wl.dcf": ("✔ DCF available", "✔ 已有 DCF", "✔ DCF tersedia"),
    "wl.angka_saja": ("— figures only", "— 僅數字", "— angka saja"),
    "wl.belum": ("none yet", "尚無", "belum ada"),
    "wl.kosong": ("Watchlist is empty. Add a stock code above.", "自選股為空，請在上方新增股票代號。",
                  "Watchlist kosong. Tambahkan kode saham di atas."),
    "wl.sumber": (
        "<b>Where the data comes from.</b> <i>Check now</i> fetches the latest material-information filings "
        "(重大訊息) from the official TWSE OpenAPI (<span class=\"mono\">t187ap04_L</span>) and TPEx OpenAPI "
        "(<span class=\"mono\">mopsfin_t187ap04_O</span>) and keeps those of watchlisted issuers. The endpoints "
        "only hold the current day, so history builds up with every check. Stored filings are never fetched twice.",
        "<b>資料來源。</b><i>立即檢查</i>會從證交所官方 OpenAPI（<span class=\"mono\">t187ap04_L</span>）與櫃買中心 "
        "OpenAPI（<span class=\"mono\">mopsfin_t187ap04_O</span>）擷取最新重大訊息，並保留自選股的公告。"
        "這些端點只提供當日資料，因此歷史資料隨每次檢查累積，已儲存的公告不會重複擷取。",
        "<b>Dari mana datanya.</b> Tombol <i>Periksa sekarang</i> menarik pengumuman material (重大訊息) terbaru "
        "dari OpenAPI resmi TWSE (<span class=\"mono\">t187ap04_L</span>) dan TPEx "
        "(<span class=\"mono\">mopsfin_t187ap04_O</span>), lalu menyimpan yang milik emiten di watchlist. Endpoint "
        "itu hanya memuat pengumuman hari berjalan, jadi riwayat terkumpul dari setiap pemeriksaan. Pengumuman "
        "yang sudah tersimpan tidak ditarik dua kali."),
    "wl.terakhir": ("Last check:", "最近檢查：", "Pemeriksaan terakhir:"),
    "wl.sumber_ok": ("OK ({n} filings, {m} on watchlist)", "成功（{n} 則公告，{m} 則屬自選股）",
                     "OK ({n} pengumuman, {m} di watchlist)"),

    # --- pesan kilat ---------------------------------------------------------------
    "msg.kode_salah": ("“{kode}” is not a valid Taiwan stock code (4–6 letters or digits).",
                       "「{kode}」不是有效的台股代號（4–6 位數字或英文字母）。",
                       "“{kode}” bukan bentuk kode saham Taiwan (4–6 angka/huruf)."),
    "msg.sudah_ada": ("{kode} is already on the watchlist.", "{kode} 已在自選股中。",
                      "{kode} sudah ada di watchlist."),
    "msg.ditambah": ("{kode} added. Press “Check now” to fetch its filings.",
                     "已新增 {kode}。按「立即檢查」擷取其公告。",
                     "{kode} ditambahkan. Tekan “Periksa sekarang” untuk menarik pengumumannya."),
    "msg.tidak_dikenal": ("{kode} is not traded on TWSE or TPEx. Check the code (ordinary shares start at 1101).",
                          "{kode} 不是證交所或櫃買中心的交易代號，請確認代號（普通股代號自 1101 起）。",
                          "{kode} tidak diperdagangkan di TWSE maupun TPEx. Periksa kodenya (saham biasa dimulai dari 1101)."),
    "msg.ditambah_nama": ("{kode} {nama} added. Its filings appear after the next check, once the exchange publishes them.",
                          "已新增 {kode} {nama}。交易所公布後，其公告會在下次檢查時出現。",
                          "{kode} {nama} ditambahkan. Pengumumannya muncul di pemeriksaan berikutnya, setelah bursa menerbitkannya."),
    "msg.ditambah_belum_pasti": ("{kode} added, but the exchange list could not be reached to confirm the code exists.",
                                 "已新增 {kode}，但無法連線至交易所清單確認此代號是否存在。",
                                 "{kode} ditambahkan, tapi daftar bursa tidak bisa dijangkau untuk memastikan kodenya ada."),
    "msg.dihapus": ("{kode} removed from the watchlist.", "已將 {kode} 從自選股移除。",
                    "{kode} dihapus dari watchlist."),
    "msg.tarik_ok": ("Checked: {n} filings from watchlisted issuers in this fetch, {baru} new.",
                     "檢查完成：本次擷取中有 {n} 則自選股公告，其中 {baru} 則為新公告。",
                     "Diperiksa: {n} pengumuman emiten watchlist di tarikan ini, {baru} baru."),
    "msg.tarik_gagal": ("Fetch failed ({sebab}). The last stored data is still used.",
                        "擷取失敗（{sebab}），仍使用最近儲存的資料。",
                        "Penarikan gagal ({sebab}). Data terakhir yang tersimpan tetap dipakai."),

    "msg.perlu_akses": ("This action needs an access code. Ask the team for the access link.",
                        "此操作需要存取碼，請向團隊索取存取連結。",
                        "Tindakan ini butuh kode akses. Minta tautan akses ke tim."),
    "msg.akses_ok": ("Access granted for this browser.", "此瀏覽器已獲得存取權限。",
                     "Akses dibuka untuk browser ini."),
    "msg.akses_salah": ("Wrong access code.", "存取碼錯誤。", "Kode akses salah."),
    "label.contoh": ("sample", "範例", "contoh"),

    # --- detail peringatan ---------------------------------------------------------
    "al.ditolak": (
        "<b>Alert not published.</b> The verifier failed the claim before the figure could touch the "
        "valuation. The reasons are recorded below and in the audit trail.",
        "<b>未發布警示。</b>驗證器在數字影響評價之前即否決此主張，原因記錄於下方及稽核軌跡中。",
        "<b>Peringatan tidak diterbitkan.</b> Pemeriksa menggagalkan klaim sebelum angkanya menyentuh "
        "valuasi. Alasannya tercatat di bawah dan di jejak audit."),
    "al.injeksi": (
        "<b>This document contains text that looks like an instruction.</b> Markers: {penanda}. "
        "It does not change the agent's behaviour: document text is data, not instructions. Logged for human review.",
        "<b>此文件含有類似指令的文字。</b>標記：{penanda}。這不會改變代理的行為：文件內容是資料而非指令。已記錄供人工審查。",
        "<b>Dokumen ini memuat teks yang menyerupai perintah.</b> Penanda: {penanda}. Tidak mengubah perilaku "
        "agent — isi dokumen adalah data, bukan instruksi. Dicatat untuk ditinjau manusia."),
    "al.sumber": ("Source", "來源", "Sumber"),
    "al.cocokkan": ("Verify on MOPS ↗", "至 MOPS 核對 ↗", "Cocokkan di MOPS ↗"),
    "al.mops_asli": ("Original MOPS page ↗", "MOPS 原始頁面 ↗", "Halaman MOPS asli ↗"),
    "al.kode_tgl": ("code {kode} · {tgl}", "代號 {kode} · {tgl}", "kode {kode} · {tgl}"),
    "al.pii": ("Personal data dropped at ingestion", "擷取時即刪除的個人資料", "Data pribadi dibuang di hulu"),
    "al.jejak": ("Audit trail", "稽核軌跡", "Jejak audit"),
    "al.lihat_langkah": ("View {n} steps →", "查看 {n} 個步驟 →", "Lihat {n} langkah →"),
    "al.hitung_ulang": ("Recomputation · {input}", "重新計算 · {input}", "Perhitungan ulang — {input}"),
    "al.butir": ("Item {no}", "第 {no} 項", "Butir {no}"),
    "al.konvensi": ("TWD (MOPS convention)", "新台幣（MOPS 慣例）", "TWD (konvensi MOPS)"),
    "al.juta_ntd": ("NT$ million", "百萬新台幣", "juta NTD"),
    "al.fcff0": ("Base-year FCFF (NT$ million)", "基期 FCFF（百萬新台幣）", "FCFF tahun dasar (juta NTD)"),
    "al.g_pasar": ("Perpetual growth implied by the market", "市場隱含的永續成長率",
                   "Pertumbuhan abadi yang diasumsikan pasar"),
    "al.wajar_g": ("Fair value at g = {g} (scenario, not a forecast)", "g = {g} 時的合理價值（情境，非預測）",
                   "Nilai wajar pada g = {g} (skenario, bukan ramalan)"),
    "al.harga": ("Market price", "市價", "Harga pasar"),
    "al.melampaui": (
        "Implied g <b>{g}</b> exceeds the perpetual-growth ceiling {batas}. The market is pricing growth that "
        "cannot last forever: a sign of overvaluation, not a sell signal.",
        "隱含 g <b>{g}</b> 超過永續成長上限 {batas}。市場所反映的成長無法永遠維持，這是高估的跡象，而非賣出訊號。",
        "g tersirat <b>{g}</b> melampaui batas pertumbuhan abadi {batas}. Pasar memberi harga untuk pertumbuhan "
        "yang tidak bisa dipertahankan selamanya — indikasi kemahalan, bukan sinyal jual."),
    "al.pemeriksaan": ("Checks · {lolos}/{total} passed", "檢查 · {lolos}/{total} 通過",
                       "Pemeriksaan — {lolos}/{total} lolos"),
    "al.ditolak_input": ("Rejected · {input}", "已拒絕 · {input}", "Ditolak — {input}"),

    # --- jejak audit ---------------------------------------------------------------
    "jj.kicker": ("Operation trace · required by Appendix 2 item 6", "作業軌跡 · 附件二第 6 項要求",
                  "Operation trace · diwajibkan Appendix 2 butir 6"),
    "jj.judul": ("Audit trail · {kode}", "稽核軌跡 · {kode}", "Jejak audit — {kode}"),
    "jj.durasi": ("Duration", "耗時", "Durasi"),
    "jj.langkah": ("Steps", "步驟", "Langkah"),
    "jj.panggilan": ("Model calls", "模型呼叫", "Panggilan model"),
    "jj.data": ("data", "資料", "data"),
    "jj.cache": ("Cached answers", "快取回覆", "Jawaban cache"),
    "jj.token_masuk": ("Input tokens", "輸入 token", "Token masuk"),
    "jj.token_keluar": ("Output tokens", "輸出 token", "Token keluar"),
    "jj.biaya": ("Cost", "成本", "Biaya"),
    "jj.retry": ("Retries", "重試", "Retry"),
    "jj.cadangan": ("Fallback mode", "備援模式", "Mode cadangan"),
    "jj.pita_cadangan": (
        "<b>Run with the rule-based reasoner.</b> No API key is set, so triage and extraction used the "
        "deterministic path. This path is also the <b>baseline</b> Appendix 2 asks for, so the figures above "
        "remain valid evaluation material.",
        "<b>以規則式推理執行。</b>未設定 API 金鑰，因此分類與擷取採用確定性路徑。此路徑同時也是附件二要求的"
        "<b>基準</b>，故上方數字仍可作為評估資料。",
        "<b>Dijalankan dengan penalar berbasis aturan.</b> Tidak ada kunci API terpasang, jadi tahap pemilah dan "
        "penyari memakai jalur deterministik. Jalur ini sekaligus <b>baseline</b> pembanding yang diminta "
        "Appendix 2 — jadi angka di atas tetap sah sebagai bahan evaluasi."),
    "jj.cadangan_sebab": ("fallback: {sebab}", "備援：{sebab}", "cadangan: {sebab}"),
    "jj.berkas": (
        "The raw JSON of this trace is in <span class=\"mono\">data/traces/{id}.json</span> and at "
        "<a href=\"/api/jejak/{id}\" class=\"mono\">/api/jejak/{id}</a>. It is written during normal use, "
        "not assembled before a deadline.",
        "此軌跡的原始 JSON 位於 <span class=\"mono\">data/traces/{id}.json</span>，亦可透過 "
        "<a href=\"/api/jejak/{id}\" class=\"mono\">/api/jejak/{id}</a> 取得。它在日常使用中自動寫入，而非在截止前拼湊。",
        "Berkas JSON mentah jejak ini ada di <span class=\"mono\">data/traces/{id}.json</span>, dan tersedia "
        "lewat <a href=\"/api/jejak/{id}\" class=\"mono\">/api/jejak/{id}</a>. Ditulis sebagai bagian dari "
        "pemakaian biasa, bukan dikarang menjelang tenggat."),
    "jst.lolos": ("passed", "通過", "lolos"),
    "jst.berhenti": ("stopped", "停止", "berhenti"),
    "jst.tolak": ("rejected", "拒絕", "tolak"),
    "jst.tercatat": ("logged", "已記錄", "tercatat"),

    # --- nama tahap ----------------------------------------------------------------
    "tahap.ambil": ("Fetched from source", "自來源擷取", "Diambil dari sumber"),
    "tahap.validasi": ("Response shape validated", "回應格式驗證", "Bentuk respons divalidasi"),
    "tahap.review": ("Human review", "人工審查", "Tinjauan manusia"),
    "tahap.review_abaikan": ("Human review (decision ignored)", "人工審查（決定未採用）", "Tinjauan manusia (keputusan diabaikan)"),
    "tahap.saring": ("0 · Clause screen", "0 · 條款篩選", "0 · Saringan pasal"),
    "tahap.pilah_sari": ("1–2 · Triage & extraction", "1–2 · 分類與擷取", "1–2 · Pemilah & penyari"),
    "tahap.injeksi": ("· Injection marker", "· 注入標記", "· Penanda injeksi"),
    "tahap.periksa_awal": ("4a · Pre-computation verifier ({input})", "4a · 計算前驗證（{input}）",
                           "4a · Pemeriksa pra-hitung ({input})"),
    "tahap.hitung": ("3 · Recompute ({input})", "3 · 重新計算（{input}）", "3 · Penghitung ({input})"),
    "tahap.periksa_akhir": ("4b · Post-computation verifier ({input})", "4b · 計算後驗證（{input}）",
                            "4b · Pemeriksa pasca-hitung ({input})"),
    "tahap.selesai": ("· Done", "· 完成", "· Selesai"),

    # --- alasan akhir pipeline -----------------------------------------------------
    "akhir.tanpa_angka": ("No figure could be extracted together with its source sentence.",
                          "無法擷取附帶原文句子的數字。",
                          "Tidak ada angka yang bisa ditarik lengkap dengan kalimat sumbernya."),
    "akhir.tanpa_valuasi": (
        "No valuation file for issuer {kode} yet. The figure was extracted, but there is no model to recompute.",
        "發行公司 {kode} 尚無評價檔。數字已擷取，但沒有可重新計算的模型。",
        "Belum ada berkas valuasi untuk emiten {kode}. Angka tertarik, tapi tidak ada model untuk menghitung ulang."),
    "akhir.disetujui": ("Approved by a human reviewer: {catatan}", "經人工審查核准：{catatan}", "Disetujui peninjau manusia: {catatan}"),
    "akhir.diarsipkan": ("Archived by a human reviewer: {catatan}", "經人工審查歸檔：{catatan}", "Diarsipkan peninjau manusia: {catatan}"),
    "akhir.terbit": ("{n} finding(s) passed every check.", "{n} 項發現通過所有檢查。",
                     "{n} temuan lolos seluruh pemeriksaan."),

    # --- saringan pasal -----------------------------------------------------------
    "saring.tanpa_pasal": (
        "No 符合條款 clause number on the page, so there is no basis to screen. Passed on, flagged for human review.",
        "頁面上沒有符合條款編號，無從篩選。已放行並標記供人工審查。",
        "Nomor 符合條款 tidak ada di halaman, tidak ada dasar menyaring. Diteruskan dengan tanda supaya ditinjau manusia."),
    "saring.di_luar": (
        "Clause {k} is not on the list of clauses that can change a valuation input. Not sent to the model.",
        "第 {k} 款不在可能影響評價輸入的條款清單中，未送交模型。",
        "Pasal {k} tidak ada dalam daftar pasal yang dapat mengubah input valuasi. Tidak diteruskan ke model."),
    "saring.cocok": ("Clause {k} · {nama}. May affect: {input}.", "第 {k} 款 · {nama}。可能影響：{input}。",
                     "Pasal {k} — {nama}. Dapat menyentuh: {input}."),
    "klausa.11": ("Board decision on capital expenditure", "董事會決議資本支出", "Keputusan dewan direksi atas belanja modal"),
    "klausa.20": ("Acquisition or disposal of assets", "取得或處分資產", "Perolehan atau pelepasan aset"),
    "klausa.22": ("Significant lending or guarantees", "重大資金貸與或背書保證", "Pinjaman dana atau penjaminan signifikan"),
    "klausa.2": ("Bounced cheque, default or financial distress", "退票、違約或財務困難",
                 "Cek kosong, gagal bayar, atau kesulitan keuangan"),

    # --- pemeriksa ----------------------------------------------------------------
    "cek.label": ("Item label valid for this input", "項目標籤適用於此輸入", "Label butir sah untuk input ini"),
    "cek.label.ok": ("Label '{label}' is on the valid-label list for {input}: {sah}",
                     "標籤「{label}」在 {input} 的有效標籤清單中：{sah}",
                     "Label '{label}' ada dalam daftar label sah untuk {input}: {sah}"),
    "cek.label.x": ("Label '{label}' is NOT on the valid-label list for {input}: {sah}",
                    "標籤「{label}」不在 {input} 的有效標籤清單中：{sah}",
                    "Label '{label}' TIDAK ada dalam daftar label sah untuk {input}: {sah}"),
    "cek.kutipan": ("Quotation found in the source document", "引文存在於原始文件", "Kutipan ditemukan di dokumen sumber"),
    "cek.kutipan.ok": ("Quotation matches the document text", "引文與文件內容相符", "Kutipan cocok dengan isi dokumen"),
    "cek.kutipan.x": ("Quotation '{kutipan}' not found in the document: likely fabricated",
                      "文件中找不到引文「{kutipan}」，可能為捏造",
                      "Kutipan '{kutipan}' tidak ditemukan di dokumen — kemungkinan dikarang"),
    "cek.angka": ("Figure found in the source document", "數字存在於原始文件", "Angka ditemukan di dokumen sumber"),
    "cek.angka.ok": ("Figure {angka} is in the document", "數字 {angka} 存在於文件中", "Angka {angka} ada di dokumen"),
    "cek.angka.x": ("Figure {angka} is NOT in the document: hallucination", "文件中沒有數字 {angka}：幻覺",
                    "Angka {angka} TIDAK ada di dokumen — halusinasi"),
    "cek.mu": ("Currency supported by the model", "幣別為模型所支援", "Mata uang didukung model"),
    "cek.mu.asumsi": ("NTD (assumed, per MOPS convention)", "新台幣（依 MOPS 慣例推定）",
                      "NTD (diasumsikan, sesuai konvensi MOPS)"),
    "cek.mu.ok": ("NTD", "新台幣", "NTD"),
    "cek.mu.x": ("Amount is in {mu}. The valuation model holds no exchange rate, so the figure must not be "
                 "converted silently.",
                 "金額以 {mu} 計價。評價模型不含匯率，不得私下換算。",
                 "Jumlah berdenominasi {mu}. Model valuasi tidak memuat kurs, jadi angka ini tidak boleh "
                 "dikonversi diam-diam."),
    "cek.satuan": ("Unit recognised", "單位可辨識", "Satuan dikenali"),
    "cek.satuan.ok": ("Unit '{satuan}' recognised (×{pengali} to NT$ million)", "單位「{satuan}」可辨識（換算百萬新台幣 ×{pengali}）",
                      "Satuan '{satuan}' dikenali (pengali {pengali} ke juta NTD)"),
    "cek.satuan.x": ("Unit '{satuan}' not recognised: cannot be converted safely", "無法辨識單位「{satuan}」，無法安全換算",
                     "Satuan '{satuan}' tidak dikenali — tidak bisa dikonversi dengan aman"),
    "cek.konversi": ("Converted value available", "已取得換算值", "Nilai terkonversi tersedia"),
    "cek.konversi.ok": ("{nilai} NT$ million", "{nilai} 百萬新台幣", "{nilai} juta NTD"),
    "cek.konversi.x": ("Not converted: fail-closed because of unit or currency", "未換算：因單位或幣別而採失效關閉",
                       "Konversi tidak dilakukan — gagal-tertutup karena satuan atau mata uang"),
    "cek.besaran": ("Magnitude plausible", "數量級合理", "Besaran masuk akal"),
    "cek.besaran.na": ("Cannot be judged: the new or current value is unavailable", "無法判斷：缺少新值或現值",
                       "Tidak bisa dinilai — nilai baru atau nilai lama tidak tersedia"),
    "cek.besaran.ok": ("{nilai} vs {lama} NT$ million = {rasio}× (within the {bawah}–{atas}× band)",
                       "{nilai} 對 {lama} 百萬新台幣 = {rasio} 倍（在 {bawah}–{atas} 倍區間內）",
                       "{nilai} berbanding {lama} juta NTD = {rasio}× (dalam pita {bawah}–{atas}×)"),
    "cek.besaran.x": ("{nilai} vs {lama} NT$ million = {rasio}× (OUTSIDE the {bawah}–{atas}× band). A single filing "
                      "that moves an input this far is almost certainly a unit or item error.",
                      "{nilai} 對 {lama} 百萬新台幣 = {rasio} 倍（超出 {bawah}–{atas} 倍區間）。單一公告使輸入變動如此之大，"
                      "幾乎可以確定是單位或項目錯誤。",
                      "{nilai} berbanding {lama} juta NTD = {rasio}× (DI LUAR pita {bawah}–{atas}×). Satu pengumuman "
                      "yang menggeser input sebesar ini hampir pasti salah satuan atau salah butir."),
    "cek.sirkular": ("Circularity intact", "循環一致性完好", "Sirkularitas utuh"),
    "cek.sirkular.ok": ("Feeding g back returns the same EV (drift {drift}%)", "代回 g 得到相同 EV（偏差 {drift}%）",
                        "g dimasukkan kembali mengembalikan EV yang sama (selisih {drift}%)"),
    "cek.sirkular.x": ("Circularity drift {drift}% above the limit: arithmetic bug", "循環偏差 {drift}% 超過上限：計算錯誤",
                       "Selisih sirkularitas {drift}% di atas batas — ada bug aritmetika"),

    # --- hitung ulang -------------------------------------------------------------
    "arti.capex": ("Replaces the latest year's capital expenditure: a scenario in which this level continues",
                   "取代最近一年的資本支出：假設此水準持續的情境",
                   "Mengganti belanja modal tahun terakhir — skenario bila tingkat ini berlanjut"),
    "arti.cash": ("Replaces the cash and cash-equivalents balance", "取代現金及約當現金餘額",
                  "Mengganti saldo kas dan setara kas"),
    "arti.debt": ("Replaces long-term debt", "取代長期借款", "Mengganti utang jangka panjang"),

    # --- halaman saham ------------------------------------------------------------
    "sh.tab.stream": ("Stream", "動態", "Stream"),
    "sh.tab.stats": ("Key Stats", "關鍵數據", "Key Stats"),
    "sh.tab.keu": ("Financials", "財務報表", "Keuangan"),
    "sh.tab.valuasi": ("Valuation", "評價", "Valuasi"),
    "sh.tab.profil": ("Profile", "公司資料", "Profil"),
    "sh.cari": ("Search code, e.g. 2330", "搜尋代號，例：2330", "Cari kode, mis. 2330"),
    "sh.buka": ("Open stock page", "開啟個股頁面", "Buka halaman saham"),
    "sh.harga_per": ("Close · {tgl} · {bursa}", "收盤 · {tgl} · {bursa}", "Penutupan · {tgl} · {bursa}"),
    "sh.tanpa_harga": ("No price data for this code.", "查無此代號的價格資料。", "Tidak ada data harga untuk kode ini."),
    "sh.di_watchlist": ("On watchlist", "已在自選股", "Ada di watchlist"),
    "sh.tambah_wl": ("+ Add to watchlist", "+ 加入自選股", "+ Tambah ke watchlist"),
    "sh.stream_kosong": ("No stored filings for this stock yet. Add it to the watchlist and press Check now.",
                         "尚無此股票的已存公告。請加入自選股並按「立即檢查」。",
                         "Belum ada pengumuman tersimpan untuk saham ini. Tambahkan ke watchlist lalu tekan Periksa sekarang."),
    "sh.lr": ("Income statement", "綜合損益表", "Laba rugi"),
    "sh.neraca": ("Balance sheet", "資產負債表", "Neraca"),
    "sh.arus": ("Cash flow", "現金流量表", "Arus kas"),
    "sh.kuartal": ("Quarterly", "季", "Kuartalan"),
    "sh.tahunan": ("Annual", "年", "Tahunan"),
    "sh.nilai": ("Values", "數值", "Nilai"),
    "sh.yoy": ("YoY growth", "年增率", "Pertumbuhan YoY"),
    "sh.satuan": ("NT$ million (EPS in NT$)", "百萬新台幣（EPS 為新台幣元）", "Juta NTD (EPS dalam NTD)"),
    "sh.satuan_yoy": ("Year-on-year change", "與去年同期相比", "Perubahan dibanding periode sama tahun lalu"),
    "sh.sumber_keu": (
        "Source: FinMind, an aggregator of MOPS financial statements. Cash flows are cumulative in MOPS filings; "
        "quarterly figures here are the difference between consecutive quarters. Annual income-statement figures "
        "are the sum of four quarters. Red = up, green = down (Taiwan convention).",
        "資料來源：FinMind（彙整 MOPS 財務報表）。MOPS 的現金流量為累計數，此處季數字為相鄰兩季之差；"
        "年度損益為四季加總。紅色＝上升，綠色＝下降（台灣慣例）。",
        "Sumber: FinMind, agregator laporan keuangan MOPS. Arus kas di MOPS bersifat kumulatif; angka kuartal di sini "
        "adalah selisih dua kuartal berurutan. Laba rugi tahunan = jumlah empat kuartal. Merah = naik, hijau = turun "
        "(konvensi Taiwan)."),
    "sh.cache": ("Showing cached data from {tgl} because the source could not be reached ({galat}).",
                 "無法連線至資料來源（{galat}），顯示 {tgl} 的快取資料。",
                 "Menampilkan data cache dari {tgl} karena sumber tidak bisa dijangkau ({galat})."),
    "sh.keu_kosong": (
        "Financial statements are not available right now ({galat}). FinMind allows 300 requests per hour without a "
        "token; set FINMIND_TOKEN for more.",
        "目前無法取得財務報表（{galat}）。FinMind 未使用金鑰時每小時限 300 次請求，設定 FINMIND_TOKEN 可提高額度。",
        "Laporan keuangan belum bisa diambil ({galat}). FinMind membatasi 300 permintaan per jam tanpa token; isi "
        "FINMIND_TOKEN untuk kuota lebih besar."),
    "sh.fcf_catatan": ("computed", "計算值", "dihitung"),
    "st.harga": ("Price", "價格", "Harga"),
    "st.ubah": ("Change", "漲跌", "Perubahan"),
    "st.rentang": ("Day range", "當日區間", "Rentang hari ini"),
    "st.volume": ("Volume (shares)", "成交量（股）", "Volume (lembar)"),
    "st.kapitalisasi": ("Market cap", "市值", "Kapitalisasi pasar"),
    "st.per": ("P/E (exchange)", "本益比（交易所）", "PER (bursa)"),
    "st.pbr": ("P/B (exchange)", "股價淨值比（交易所）", "PBR (bursa)"),
    "st.yield": ("Dividend yield", "殖利率", "Imbal hasil dividen"),
    "st.ttm": ("Trailing 12 months to {tgl}", "近四季（至 {tgl}）", "12 bulan terakhir s.d. {tgl}"),
    "st.pendapatan": ("Revenue (TTM)", "營業收入（近四季）", "Pendapatan (TTM)"),
    "st.laba": ("Net income to parent (TTM)", "歸屬母公司淨利（近四季）", "Laba bersih ke induk (TTM)"),
    "st.eps": ("EPS (TTM)", "每股盈餘（近四季）", "EPS (TTM)"),
    "st.mk": ("Gross margin", "毛利率", "Margin kotor"),
    "st.mu": ("Operating margin", "營業利益率", "Margin usaha"),
    "st.mb": ("Net margin", "淨利率", "Margin bersih"),
    "st.roe": ("ROE (TTM)", "股東權益報酬率（近四季）", "ROE (TTM)"),
    "st.lembar": ("Shares outstanding", "流通股數", "Jumlah saham"),
    "st.pasar": ("Market data", "市場數據", "Data pasar"),
    "st.fundamental": ("Fundamentals", "基本面", "Fundamental"),
    "st.sumber": ("Price and ratios: official TWSE/TPEx OpenAPI. Fundamentals: computed from the statements in the Financials tab.",
                  "價格與比率：證交所／櫃買中心官方 OpenAPI。基本面：依「財務報表」分頁之數據計算。",
                  "Harga dan rasio: OpenAPI resmi TWSE/TPEx. Fundamental: dihitung dari laporan di tab Keuangan."),
    "pf.nama": ("Company name", "公司名稱", "Nama perusahaan"),
    "pf.en": ("English short name", "英文簡稱", "Nama singkat (Inggris)"),
    "pf.industri": ("Industry", "產業別", "Industri"),
    "pf.bursa": ("Exchange", "市場別", "Bursa"),
    "pf.berdiri": ("Incorporated", "成立日期", "Berdiri"),
    "pf.tercatat": ("Listed", "上市日期", "Tercatat"),
    "pf.modal": ("Paid-in capital (NT$)", "實收資本額（新台幣）", "Modal disetor (NTD)"),
    "pf.alamat": ("Address", "地址", "Alamat"),
    "pf.situs": ("Website", "網址", "Situs"),
    "pf.keuangan": ("Financial-sector company: a free-cash-flow DCF does not apply.",
                    "金融業公司：不適用自由現金流量折現模型。",
                    "Emiten sektor keuangan: DCF berbasis arus kas bebas tidak berlaku."),
    "pf.pii": ("Names of officers, spokespersons and auditors are dropped at ingestion.",
               "董事長、發言人及簽證會計師等個人姓名於擷取時即刪除。",
               "Nama direksi, juru bicara, dan akuntan dibuang saat data ditarik."),
    "pf.kosong": ("No company profile found for this code.", "查無此代號的公司資料。", "Profil perusahaan tidak ditemukan."),
    "va.belum": ("No valuation model for this issuer yet.", "此公司尚無評價模型。", "Belum ada model valuasi untuk emiten ini."),
    "va.buka": ("Open full valuation →", "開啟完整評價 →", "Buka valuasi lengkap →"),

    # --- pos laporan keuangan (中文 = nama di laporan MOPS) ---
    "pos.Revenue": ('Revenue', '營業收入', 'Pendapatan'),
    "pos.CostOfGoodsSold": ('Cost of revenue', '營業成本', 'Beban pokok penjualan'),
    "pos.GrossProfit": ('Gross profit', '營業毛利', 'Laba kotor'),
    "pos.OperatingExpenses": ('Operating expenses', '營業費用', 'Beban usaha'),
    "pos.OperatingIncome": ('Operating income', '營業利益', 'Laba usaha'),
    "pos.TotalNonoperatingIncomeAndExpense": ('Non-operating income and expense', '營業外收入及支出', 'Pendapatan/beban lain-lain'),
    "pos.PreTaxIncome": ('Income before tax', '稅前淨利', 'Laba sebelum pajak'),
    "pos.TAX": ('Income tax expense', '所得稅費用', 'Beban pajak penghasilan'),
    "pos.IncomeAfterTaxes": ('Net income', '本期淨利', 'Laba bersih'),
    "pos.EquityAttributableToOwnersOfParent": ('Attributable to owners of parent', '歸屬於母公司業主', 'Diatribusikan ke pemilik induk'),
    "pos.OtherComprehensiveIncome": ('Other comprehensive income', '其他綜合損益', 'Pendapatan komprehensif lain'),
    "pos.TotalConsolidatedProfitForThePeriod": ('Total comprehensive income', '本期綜合損益總額', 'Jumlah laba komprehensif'),
    "pos.EPS": ('EPS (basic, NT$)', '基本每股盈餘（元）', 'EPS dasar (NTD)'),
    "pos.CashAndCashEquivalents": ('Cash and cash equivalents', '現金及約當現金', 'Kas dan setara kas'),
    "pos.AccountsReceivableNet": ('Accounts receivable', '應收帳款淨額', 'Piutang usaha'),
    "pos.Inventories": ('Inventories', '存貨', 'Persediaan'),
    "pos.CurrentAssets": ('Total current assets', '流動資產合計', 'Total aset lancar'),
    "pos.PropertyPlantAndEquipment": ('Property, plant and equipment', '不動產、廠房及設備', 'Aset tetap'),
    "pos.NoncurrentAssets": ('Total non-current assets', '非流動資產合計', 'Total aset tidak lancar'),
    "pos.TotalAssets": ('Total assets', '資產總額', 'Total aset'),
    "pos.AccountsPayable": ('Accounts payable', '應付帳款', 'Utang usaha'),
    "pos.CurrentLiabilities": ('Total current liabilities', '流動負債合計', 'Total liabilitas jangka pendek'),
    "pos.BondsPayable": ('Bonds payable', '應付公司債', 'Utang obligasi'),
    "pos.LongtermBorrowings": ('Long-term borrowings', '長期借款', 'Pinjaman jangka panjang'),
    "pos.NoncurrentLiabilities": ('Total non-current liabilities', '非流動負債合計', 'Total liabilitas jangka panjang'),
    "pos.Liabilities": ('Total liabilities', '負債總額', 'Total liabilitas'),
    "pos.CapitalStock": ('Share capital', '股本合計', 'Modal saham'),
    "pos.RetainedEarnings": ('Retained earnings', '保留盈餘合計', 'Laba ditahan'),
    "pos.Equity": ('Total equity', '權益總額', 'Total ekuitas'),
    "pos.NetIncomeBeforeTax": ('Income before tax', '本期稅前淨利', 'Laba sebelum pajak'),
    "pos.Depreciation": ('Depreciation', '折舊費用', 'Penyusutan'),
    "pos.AmortizationExpense": ('Amortisation', '攤銷費用', 'Amortisasi'),
    "pos.CashFlowsFromOperatingActivities": ('Cash flow from operations', '營業活動之淨現金流入（流出）', 'Arus kas operasi'),
    "pos.PropertyAndPlantAndEquipment": ('Capital expenditure (PP&E)', '取得不動產、廠房及設備', 'Belanja modal (aset tetap)'),
    "pos.CashProvidedByInvestingActivities": ('Cash flow from investing', '投資活動之淨現金流入（流出）', 'Arus kas investasi'),
    "pos.CashFlowsProvidedFromFinancingActivities": ('Cash flow from financing', '籌資活動之淨現金流入（流出）', 'Arus kas pendanaan'),
    "pos.FreeCashFlow": ('Free cash flow (CFO + capex)', '自由現金流量', 'Arus kas bebas (CFO + capex)'),
    "pos.CashBalancesIncrease": ('Net change in cash', '本期現金及約當現金增加（減少）數', 'Perubahan kas bersih'),
    "pos.CashBalancesEndOfPeriod": ('Cash at end of period', '期末現金及約當現金餘額', 'Kas akhir periode'),

    # --- industri TWSE (產業別) ---
    "ind.01": ('Cement', '水泥工業', 'Semen'),
    "ind.02": ('Food', '食品工業', 'Makanan'),
    "ind.03": ('Plastics', '塑膠工業', 'Plastik'),
    "ind.04": ('Textiles', '紡織纖維', 'Tekstil'),
    "ind.05": ('Electric machinery', '電機機械', 'Mesin listrik'),
    "ind.06": ('Electrical cable', '電器電纜', 'Kabel listrik'),
    "ind.08": ('Glass and ceramics', '玻璃陶瓷', 'Kaca dan keramik'),
    "ind.09": ('Paper and pulp', '造紙工業', 'Kertas'),
    "ind.10": ('Iron and steel', '鋼鐵工業', 'Besi dan baja'),
    "ind.11": ('Rubber', '橡膠工業', 'Karet'),
    "ind.12": ('Automobile', '汽車工業', 'Otomotif'),
    "ind.14": ('Building materials and construction', '建材營造', 'Bahan bangunan dan konstruksi'),
    "ind.15": ('Shipping and transportation', '航運業', 'Pelayaran dan transportasi'),
    "ind.16": ('Tourism and hospitality', '觀光餐旅', 'Pariwisata'),
    "ind.17": ('Financials and insurance', '金融保險', 'Keuangan dan asuransi'),
    "ind.18": ('Trading and consumer goods', '貿易百貨', 'Perdagangan dan ritel'),
    "ind.20": ('Other', '其他', 'Lainnya'),
    "ind.21": ('Chemicals', '化學工業', 'Kimia'),
    "ind.22": ('Biotechnology and medical', '生技醫療', 'Bioteknologi dan medis'),
    "ind.23": ('Oil, gas and electricity', '油電燃氣', 'Minyak, gas, dan listrik'),
    "ind.24": ('Semiconductors', '半導體業', 'Semikonduktor'),
    "ind.25": ('Computers and peripherals', '電腦及週邊設備業', 'Komputer dan periferal'),
    "ind.26": ('Optoelectronics', '光電業', 'Optoelektronik'),
    "ind.27": ('Communications and internet', '通信網路業', 'Komunikasi dan jaringan'),
    "ind.28": ('Electronic components', '電子零組件業', 'Komponen elektronik'),
    "ind.29": ('Electronics distribution', '電子通路業', 'Distribusi elektronik'),
    "ind.30": ('Information services', '資訊服務業', 'Layanan informasi'),
    "ind.31": ('Other electronics', '其他電子業', 'Elektronik lainnya'),

    # --- ringkasan analisis --------------------------------------------------------
    "sh.tab.ringkasan": ('Summary', '分析摘要', 'Ringkasan'),
    "rk.judul": ('Analysis summary', '分析摘要', 'Ringkasan analisis'),
    "rk.profil_label": ('Your risk profile', '您的風險屬性', 'Profil risiko Anda'),
    "rk.risiko.konservatif": ('conservative', '保守型', 'konservatif'),
    "rk.risiko.moderat": ('moderate', '穩健型', 'moderat'),
    "rk.risiko.agresif": ('aggressive', '積極型', 'agresif'),
    "rk.hasil": ('What the analysis found', '分析結果', 'Hasil analisis'),
    "rk.kesimpulan_judul": ('Conclusion', '結論', 'Kesimpulan'),
    "rk.kuat_judul": ('Strengths', '優勢', 'Kekuatan'),
    "rk.awas_judul": ('Watch-outs', '需留意', 'Perlu diperhatikan'),
    "rk.cek_judul": ('What to check before deciding', '決策前請確認', 'Yang perlu dicek sebelum memutuskan'),
    "rk.narasi_judul": ('In plain words', '白話說明', 'Dalam bahasa sehari-hari'),
    "rk.narasi_model": ('Written by {model} from the facts above; every number was checked against them.', '由 {model} 依據上述事實撰寫；所有數字皆已與事實比對。', 'Dirangkai oleh {model} dari fakta di atas; setiap angka sudah dicocokkan dengan fakta.'),
    "rk.narasi_template": ('No model narrative: {alasan}. The structured analysis above is complete on its own.', '無模型說明：{alasan}。上方結構化分析本身已完整。', 'Tanpa narasi model: {alasan}. Analisis terstruktur di atas sudah lengkap.'),
    "rk.alasan.tanpa_model": ("no API key set", "未設定 API 金鑰", "kunci API belum dipasang"),
    "rk.alasan.gagal": ("the model call failed", "模型呼叫失敗", "panggilan model gagal"),
    "rk.alasan.ditolak": ("the verifier rejected the model's paragraph", "驗證器否決了模型撰寫的段落", "pemeriksa menolak paragraf dari model"),
    "rk.sumber": ('source', '來源', 'sumber'),
    "rk.kosong": ('Not enough data to analyse this stock yet.', '此股票目前資料不足，無法分析。', 'Data belum cukup untuk menganalisis saham ini.'),
    "rk.disclaimer": ("This is research, not a buy or sell recommendation. Robo-advice in Taiwan requires an FSC licence; FEAF analyses, explains and monitors, and the investor makes the decision. Judgement thresholds are working rules pending review by the team's finance members.", '本頁為研究分析，並非買賣建議。在台灣提供自動化投資建議須取得金管會核准；FEAF 負責分析、說明與監控，決策由投資人自行做出。判斷門檻為暫定規則，待團隊財務成員審核。', 'Ini riset, bukan rekomendasi beli atau jual. Saran investasi otomatis di Taiwan wajib berizin FSC; FEAF menganalisis, menjelaskan, dan memantau, sedangkan keputusan ada di tangan investor. Ambang penilaian adalah aturan kerja sementara yang menunggu verifikasi anggota keuangan tim.'),
    "rk.aspek.sektor": ('Sector', '產業', 'Sektor'),
    "rk.aspek.valuasi": ('Valuation (DCF)', '評價（DCF）', 'Valuasi (DCF)'),
    "rk.aspek.valuasi_relatif": ('Valuation vs peers', '與同業相比的評價', 'Valuasi dibanding sesama'),
    "rk.aspek.pertumbuhan": ('Growth', '成長', 'Pertumbuhan'),
    "rk.aspek.profitabilitas": ('Profitability', '獲利能力', 'Profitabilitas'),
    "rk.aspek.utang": ('Debt', '負債', 'Utang'),
    "rk.aspek.arus_kas": ('Cash flow', '現金流量', 'Arus kas'),
    "rk.aspek.pengumuman": ('Filings', '重大訊息', 'Pengumuman'),
    "rk.sektor_keuangan": ('Financial-sector company: the free-cash-flow DCF and the debt ratio do not apply and are left out.', '金融業公司：不適用自由現金流量折現模型與負債比率，故不納入。', 'Emiten sektor keuangan: DCF arus kas bebas dan rasio utang tidak berlaku, jadi tidak dipakai.'),
    "rk.dcf.tinggi": ('The current price implies {g} perpetual growth, above the {batas} ceiling: the price already assumes high expectations.', '目前股價隱含 {g} 的永續成長率，高於 {batas} 的上限：股價已反映高度預期。', 'Harga sekarang mengasumsikan pertumbuhan abadi {g}, di atas batas {batas}: harga sudah memperhitungkan ekspektasi tinggi.'),
    "rk.dcf.wajar": ('The current price implies {g} perpetual growth, within the {batas} ceiling: expectations look attainable.', '目前股價隱含 {g} 的永續成長率，在 {batas} 上限之內：預期看來可以達成。', 'Harga sekarang mengasumsikan pertumbuhan abadi {g}, masih di bawah batas {batas}: ekspektasinya tampak terjangkau.'),
    "rk.per.tinggi": ('P/E {per} is well above the {industri} median of {median} ({n} listed peers): priced richer than peers.', '本益比 {per}，明顯高於{industri}中位數 {median}（{n} 家上市同業）：評價高於同業。', 'PER {per} jauh di atas median {industri} {median} ({n} emiten sejenis): lebih mahal dibanding sesama.'),
    "rk.per.rendah": ('P/E {per} is well below the {industri} median of {median} ({n} listed peers): priced cheaper than peers.', '本益比 {per}，明顯低於{industri}中位數 {median}（{n} 家上市同業）：評價低於同業。', 'PER {per} jauh di bawah median {industri} {median} ({n} emiten sejenis): lebih murah dibanding sesama.'),
    "rk.per.sejalan": ('P/E {per} is close to the {industri} median of {median} ({n} listed peers).', '本益比 {per}，接近{industri}中位數 {median}（{n} 家上市同業）。', 'PER {per} mendekati median {industri} {median} ({n} emiten sejenis).'),
    "rk.tumbuh.kuat": ('Revenue grew {yoy} in {th}; latest quarter {q}: {yoy_q} year on year.', '{th} 年營收成長 {yoy}；最近一季 {q} 年增 {yoy_q}。', 'Pendapatan {th} tumbuh {yoy}; kuartal terakhir {q}: {yoy_q} dibanding tahun lalu.'),
    "rk.tumbuh.sedang": ('Revenue grew modestly, {yoy} in {th}; latest quarter {q}: {yoy_q} year on year.', '{th} 年營收小幅成長 {yoy}；最近一季 {q} 年增 {yoy_q}。', 'Pendapatan {th} tumbuh tipis {yoy}; kuartal terakhir {q}: {yoy_q} dibanding tahun lalu.'),
    "rk.tumbuh.turun": ('Revenue fell {yoy} in {th}; latest quarter {q}: {yoy_q} year on year.', '{th} 年營收衰退 {yoy}；最近一季 {q} 年增 {yoy_q}。', 'Pendapatan {th} turun {yoy}; kuartal terakhir {q}: {yoy_q} dibanding tahun lalu.'),
    "rk.roe.kuat": ('Return on equity {roe} with a {mb} net margin: highly profitable.', '股東權益報酬率 {roe}，淨利率 {mb}：獲利能力強。', 'ROE {roe} dengan margin bersih {mb}: sangat menguntungkan.'),
    "rk.roe.sedang": ('Return on equity {roe} with a {mb} net margin: moderate profitability.', '股東權益報酬率 {roe}，淨利率 {mb}：獲利能力中等。', 'ROE {roe} dengan margin bersih {mb}: profitabilitas sedang.'),
    "rk.roe.lemah": ('Return on equity {roe} with a {mb} net margin: weak profitability.', '股東權益報酬率 {roe}，淨利率 {mb}：獲利能力偏弱。', 'ROE {roe} dengan margin bersih {mb}: profitabilitas lemah.'),
    "rk.utang.tinggi": ('Liabilities are {rasio} of total assets ({q}): a heavy debt load.', '負債占總資產 {rasio}（{q}）：負債偏高。', 'Liabilitas {rasio} dari total aset ({q}): beban utang berat.'),
    "rk.utang.sedang": ('Liabilities are {rasio} of total assets ({q}).', '負債占總資產 {rasio}（{q}）。', 'Liabilitas {rasio} dari total aset ({q}).'),
    "rk.utang.rendah": ('Liabilities are only {rasio} of total assets ({q}): a light debt load.', '負債僅占總資產 {rasio}（{q}）：負債偏低。', 'Liabilitas hanya {rasio} dari total aset ({q}): beban utang ringan.'),
    "rk.fcf.positif": ('Free cash flow was positive in {th}: {fcf} NT$ million.', '{th} 年自由現金流量為正：{fcf} 百萬新台幣。', 'Arus kas bebas {th} positif: {fcf} juta NTD.'),
    "rk.fcf.negatif": ('Free cash flow was negative in {th}: {fcf} NT$ million, so spending exceeded operating cash.', '{th} 年自由現金流量為負：{fcf} 百萬新台幣，支出超過營業現金。', 'Arus kas bebas {th} negatif: {fcf} juta NTD, belanja melebihi kas dari operasi.'),
    "rk.umum.terbit": ('{n} verified alert(s); latest on {tgl}: {judul}', '{n} 則已驗證警示；最新一則 {tgl}：{judul}', '{n} peringatan terverifikasi; terbaru {tgl}: {judul}'),
    "rk.umum.tunggu": ('{n} filing(s) are held or rejected and wait for human review.', '{n} 則公告暫緩或遭拒，等待人工審查。', '{n} pengumuman ditahan atau ditolak dan menunggu tinjauan manusia.'),
    "rk.umum.kosong": ('No processed filings for this stock yet.', '此股票尚無已處理的公告。', 'Belum ada pengumuman yang diproses untuk saham ini.'),
    "rk.k.positif": ('Overall picture is positive: {kuat} strengths and no major watch-outs in the data reviewed.', '整體情況正面：檢視資料中有 {kuat} 項優勢，無重大需留意事項。', 'Gambaran keseluruhan positif: {kuat} kekuatan dan tidak ada hal besar yang perlu diwaspadai dari data yang diperiksa.'),
    "rk.k.campuran": ('Mixed picture: {kuat} strengths against {awas} watch-outs. Weigh them against your own goals.', '情況好壞參半：{kuat} 項優勢對比 {awas} 項需留意事項，請依自身目標權衡。', 'Gambaran campuran: {kuat} kekuatan berhadapan dengan {awas} hal yang perlu diperhatikan. Timbang dengan tujuan Anda sendiri.'),
    "rk.k.waspada": ('Several watch-outs ({awas}) and no clear strengths in the data reviewed.', '檢視資料中有多項需留意事項（{awas} 項），且無明顯優勢。', 'Beberapa hal perlu diwaspadai ({awas}) dan tidak ada kekuatan yang jelas dari data yang diperiksa.'),
    "rk.k.terbatas": ('No strong signal either way in the data reviewed.', '檢視資料中沒有明顯的正面或負面訊號。', 'Tidak ada sinyal kuat ke arah mana pun dari data yang diperiksa.'),
    "rk.p.hati": ('Points to watch for a {profil} profile: see the items marked above.', '{profil}型投資人可留意：上方標示的項目。', 'Hal yang perlu diperhatikan untuk profil {profil}: lihat butir yang ditandai di atas.'),
    "rk.p.aman": ('For a {profil} profile, none of the items above crosses the watch-out thresholds set by the team.', '以{profil}型投資人而言，上方項目皆未超過團隊設定的留意門檻。', 'Untuk profil {profil}, tidak ada butir di atas yang melewati ambang perhatian yang ditetapkan tim.'),
    "rk.cek.valuasi": ('Can the company sustain growth above the perpetual-growth ceiling for years?', '公司能否多年維持高於永續成長上限的成長？', 'Apakah perusahaan mampu mempertahankan pertumbuhan di atas batas abadi selama bertahun-tahun?'),
    "rk.cek.valuasi_relatif": ('Why is it priced above its peers, and is that premium justified?', '為何評價高於同業？此溢價是否合理？', 'Kenapa harganya di atas sesama, dan apakah premi itu wajar?'),
    "rk.cek.pertumbuhan": ('Is the revenue decline temporary or structural?', '營收衰退是暫時性還是結構性？', 'Apakah penurunan pendapatan bersifat sementara atau struktural?'),
    "rk.cek.profitabilitas": ('What would lift profitability, and how soon?', '什麼因素能提升獲利？需要多久？', 'Apa yang bisa menaikkan profitabilitas, dan seberapa cepat?'),
    "rk.cek.utang": ('Can operating cash cover the debt if conditions tighten?', '若環境轉差，營業現金能否支應負債？', 'Apakah kas operasi cukup menutup utang bila kondisi memburuk?'),
    "rk.cek.arus_kas": ('What is the spending for, and when does it start paying back?', '這些支出的用途為何？何時開始回收？', 'Untuk apa belanja itu, dan kapan mulai kembali?'),

    # --- valuasi ------------------------------------------------------------------
    "va.per": ("as of {tgl}", "截至 {tgl}", "per {tgl}"),
    "va.satuan": ("NT$ million unless stated", "除另有說明外為百萬新台幣", "juta NTD kecuali disebut lain"),
    "va.harga": ("Market price", "市價", "Harga pasar"),
    "va.sumber_kurang": (
        "<b>{n} source(s) incomplete:</b> {daftar}. Figures may be computed but must not go into the deck "
        "until every input has a URL the judges can open.",
        "<b>{n} 項來源不完整：</b>{daftar}。數字可以計算，但在每項輸入都有評審可開啟的網址之前，不得放入簡報。",
        "<b>{n} sumber belum lengkap:</b> {daftar}. Angka boleh dihitung, tapi belum boleh masuk deck sebelum "
        "tiap input punya URL yang bisa dibuka juri."),
    "va.jembatan": ("Enterprise-value bridge", "企業價值橋接", "Jembatan nilai perusahaan"),
    "va.kapitalisasi": ("Market capitalisation", "市值", "Kapitalisasi pasar"),
    "va.utang": ("+ Interest-bearing debt", "+ 付息負債", "+ Utang berbunga"),
    "va.kas": ("− Cash & short-term investments", "− 現金及短期投資", "− Kas & investasi jangka pendek"),
    "va.ev": ("= Enterprise value", "= 企業價值", "= Nilai perusahaan"),
    "va.triliun": ("T", "兆", "T"),
    "va.biaya_modal": ("Cost of capital", "資金成本", "Biaya modal"),
    "va.ke": ("Cost of equity", "權益資金成本", "Biaya ekuitas"),
    "va.kd": ("Cost of debt", "負債資金成本", "Biaya utang"),
    "va.we": ("Equity weight", "權益權重", "Bobot ekuitas"),
    "va.pajak": ("Effective tax rate", "有效稅率", "Tarif pajak efektif"),
    "va.fcf": ("Free cash flow", "自由現金流量", "Arus kas bebas"),
    "va.dipakai": (" ← used", " ← 採用", " ← dipakai"),
    "va.rata": ("Average", "平均", "Rata-rata"),
    "va.miliar": ("bn", "十億", "bio"),
    "va.g_pasar": ("Perpetual growth implied by the market", "市場隱含的永續成長率",
                   "Pertumbuhan abadi yang diasumsikan pasar"),
    "va.batas_g": ("Perpetual-growth ceiling (nominal GDP)", "永續成長上限（名目 GDP）",
                   "Batas pertumbuhan abadi (PDB nominal)"),
    "va.sirkular": ("Circularity check", "循環檢查", "Pemeriksaan sirkularitas"),
    "va.selisih": ("drift {d}%", "偏差 {d}%", "selisih {d}%"),
    "va.reverse_isi": (
        "A reverse DCF does <b>not</b> produce an intrinsic value. Feeding its g back into the same formula always "
        "returns the market price: that is a mathematical identity, not a valuation. The judgement comes next: is "
        "that number plausible?",
        "反向 DCF <b>不會</b>產生內在價值。將其 g 代回同一公式必然得到市價，這是數學恆等式，而非評價。"
        "真正的判斷在下一步：這個數字合理嗎？",
        "Reverse DCF <b>tidak</b> menghasilkan nilai intrinsik. Memasukkan g hasilnya kembali ke rumus yang sama "
        "selalu mengembalikan harga pasar — itu identitas matematis, bukan valuasi. Penilaiannya datang dari langkah "
        "berikutnya: masuk akal tidak angka itu?"),
    "va.melampaui": ("Implied g exceeds the ceiling. The market is pricing growth that cannot last forever → a sign "
                     "of overvaluation.",
                     "隱含 g 超過上限。市場所反映的成長無法永遠維持 → 高估的跡象。",
                     "g tersirat melampaui batas. Pasar memberi harga untuk pertumbuhan yang tidak bisa dipertahankan "
                     "selamanya → indikasi kemahalan."),
    "va.sensitivitas": ("Sensitivity · fair value per share (NTD)", "敏感度 · 每股合理價值（新台幣）",
                        "Sensitivitas — nilai wajar per lembar (NTD)"),
    "va.sens_isi": (
        "The middle row is the WACC computed from the input file; the middle column is the implied g. Every figure "
        "on this page comes straight from <span class=\"mono\">scripts/dcf.py</span>, the same function as the CLI "
        "worksheet, so the two cannot silently diverge.",
        "中間列為依輸入檔計算的 WACC；中間欄為隱含 g。本頁所有數字皆直接來自 <span class=\"mono\">scripts/dcf.py</span>，"
        "與命令列工作表使用同一函式，兩者不會在不知不覺中產生差異。",
        "Baris tengah adalah WACC yang dihitung dari berkas input; kolom tengah adalah g tersirat. Seluruh angka di "
        "halaman ini keluaran langsung <span class=\"mono\">scripts/dcf.py</span> — fungsi yang sama yang dipakai "
        "kertas kerja CLI, jadi keduanya tidak bisa berbeda diam-diam."),
    "va.sumber_input": ("Source of each input", "各項輸入的來源", "Sumber tiap input"),

    # --- triase keyakinan + umpan balik 👍/👎 (A2) ------------------------------
    "nav.ambang": ("Thresholds", "門檻", "Ambang"),
    "tahap.triase": ("Triage confidence {skor} vs threshold {ambang}", "分類信心 {skor}，門檻 {ambang}",
                     "Triase: keyakinan {skor} vs ambang {ambang}"),
    "tahap.review_lanjut": ("Human review (continue to the verifier)", "人工審查（續送驗證）",
                            "Tinjauan manusia (lanjut ke pemeriksa)"),
    "akhir.keyakinan_rendah": (
        "Confidence {skor} is just below the threshold {ambang} for clause {k}. Held for a human to decide.",
        "信心 {skor} 略低於第 {k} 款門檻 {ambang}，暫緩由人工決定。",
        "Keyakinan {skor} sedikit di bawah ambang {ambang} untuk pasal {k}. Ditahan untuk diputuskan manusia."),
    "akhir.di_bawah_ambang": (
        "Confidence {skor} is below the threshold {ambang} for clause {k} ({bawah} 👎, {atas} 👍). Archived.",
        "信心 {skor} 低於第 {k} 款門檻 {ambang}（{bawah} 👎、{atas} 👍），已歸檔。",
        "Keyakinan {skor} di bawah ambang {ambang} untuk pasal {k} ({bawah} 👎, {atas} 👍). Diarsipkan."),
    "tri.dasar": ("Base: clause {k} can move a valuation input", "基準：第 {k} 款可能影響評價輸入",
                  "Dasar: pasal {k} dapat menggeser input valuasi"),
    "tri.dasar_ragu": ("Base: clause number unreadable", "基準：無法辨識條款編號", "Dasar: nomor pasal tidak terbaca"),
    "tri.angka": ("{n} amount(s) converted to NT$ million", "{n} 筆金額已換算為新台幣百萬元",
                  "{n} angka terkonversi ke juta NTD"),
    "tri.angka_x": ("No amount could be converted to NT$ (foreign currency or unit)",
                    "沒有可換算為新台幣的金額（外幣或單位）",
                    "Tidak ada angka yang bisa dikonversi ke NTD (mata uang asing atau satuan)"),
    "tri.mat_besar": ("Material: NT${nilai}m = {pct}% of market cap NT${kap}m",
                      "重大：新台幣 {nilai} 百萬元 = 市值 {kap} 百萬元的 {pct}%",
                      "Material: {nilai} juta NTD = {pct}% kapitalisasi {kap} juta NTD"),
    "tri.mat_sedang": ("Fairly material: NT${nilai}m = {pct}% of market cap NT${kap}m",
                       "中度：新台幣 {nilai} 百萬元 = 市值 {kap} 百萬元的 {pct}%",
                       "Cukup material: {nilai} juta NTD = {pct}% kapitalisasi {kap} juta NTD"),
    "tri.mat_kecil": ("Small: NT${nilai}m = {pct}% of market cap NT${kap}m",
                      "偏小：新台幣 {nilai} 百萬元 = 市值 {kap} 百萬元的 {pct}%",
                      "Kecil: {nilai} juta NTD = {pct}% kapitalisasi {kap} juta NTD"),
    "tri.mat_remeh": ("Negligible: NT${nilai}m = {pct}% of market cap NT${kap}m",
                      "微小：新台幣 {nilai} 百萬元 = 市值 {kap} 百萬元的 {pct}%",
                      "Remeh: {nilai} juta NTD = {pct}% kapitalisasi {kap} juta NTD"),
    "tri.mat_na": ("Materiality not assessed (market cap unknown)", "未評估重大性（市值不明）",
                   "Materialitas tidak dinilai (kapitalisasi tidak diketahui)"),
    "tb.judul": ("Triage confidence", "分類信心", "Keyakinan triase"),
    "tb.ambang": ("Threshold for clause {k}", "第 {k} 款門檻", "Ambang pasal {k}"),
    "tb.asal": ("{bawah} 👎 · {atas} 👍 · base {dasar}", "{bawah} 👎 · {atas} 👍 · 基準 {dasar}",
                "{bawah} 👎 · {atas} 👍 · dasar {dasar}"),
    "tb.terkunci": ("locked", "已鎖定", "dikunci"),
    "tb.tanya": ("Was this alert useful to you?", "這則警示對您有幫助嗎？", "Apakah peringatan ini berguna?"),
    "tb.atas": ("👍 Useful", "👍 有幫助", "👍 Berguna"),
    "tb.bawah": ("👎 Not useful", "👎 沒幫助", "👎 Tidak berguna"),
    "tb.hapus": ("Withdraw my vote", "撤回投票", "Cabut suara"),
    "tb.suara_anda": ("Current vote: {s}", "目前投票：{s}", "Suara saat ini: {s}"),
    "tb.cara": (
        "Each 👎 raises this clause's threshold by 0.05, each 👍 lowers it by 0.02, always within 0.40–0.90. Similar filings below the threshold are archived with the reason shown; borderline ones are held for review.",
        "每個 👎 使本款門檻提高 0.05，每個 👍 降低 0.02，範圍固定在 0.40–0.90。低於門檻的同類公告將歸檔並顯示原因；接近門檻者暫緩人工審查。",
        "Setiap 👎 menaikkan ambang pasal ini 0,05, setiap 👍 menurunkannya 0,02, selalu di rentang 0,40–0,90. Pengumuman sejenis di bawah ambang diarsipkan dengan alasannya; yang di perbatasan ditahan untuk review."),
    "tb.semua": ("All thresholds →", "所有門檻 →", "Semua ambang →"),
    "amb.kicker": ("Behavioral feedback → continuous optimization", "行為回饋 → 持續優化",
                   "Umpan balik perilaku → optimasi berkelanjutan"),
    "amb.judul": ("Triage thresholds", "分類門檻", "Ambang triase"),
    "amb.isi": (
        "One set of thresholds for this server, one per clause. They are derived from your 👍/👎 votes, never edited by hand, so every value can be traced back to the votes that produced it.",
        "本伺服器共用一組門檻，每款一個。門檻由您的 👍/👎 投票推導而來，不手動修改，因此每個數值都能追溯到產生它的投票。",
        "Satu set ambang untuk server ini, satu per pasal. Nilainya diturunkan dari suara 👍/👎, tidak pernah diubah tangan, sehingga setiap nilai bisa ditelusuri ke suara yang membentuknya."),
    "amb.kosong": ("No votes yet. Every clause uses the base threshold {dasar}.",
                   "尚無投票。所有條款使用基準門檻 {dasar}。",
                   "Belum ada suara. Semua pasal memakai ambang dasar {dasar}."),
    "amb.k_pasal": ("Clause", "條款", "Pasal"),
    "amb.k_nilai": ("Threshold", "門檻", "Ambang"),
    "amb.k_status": ("Status", "狀態", "Status"),
    "amb.bebas": ("follows votes", "隨投票調整", "mengikuti suara"),
    "amb.reset": ("Reset", "重設", "Reset"),
    "amb.kunci": ("Lock", "鎖定", "Kunci"),
    "amb.buka": ("Unlock", "解鎖", "Buka kunci"),
    "amb.riwayat": ("History", "紀錄", "Riwayat"),
    "amb.k_peristiwa": ("Event", "事件", "Peristiwa"),
    "amb.k_dari_ke": ("Threshold", "門檻", "Ambang"),
    "amb.p.suara": ("vote", "投票", "suara"),
    "amb.p.reset": ("reset", "重設", "reset"),
    "amb.p.kunci": ("locked", "鎖定", "dikunci"),
    "amb.p.buka": ("unlocked", "解鎖", "dibuka"),
    "msg.suara_ok": ("Vote recorded. Threshold for clause {k}: {dari} → {ke}.",
                     "已記錄投票。第 {k} 款門檻：{dari} → {ke}。",
                     "Suara tercatat. Ambang pasal {k}: {dari} → {ke}."),
    "msg.ambang_ok": ("Threshold for clause {k}: {dari} → {ke}.", "第 {k} 款門檻：{dari} → {ke}。",
                      "Ambang pasal {k}: {dari} → {ke}."),
    "msg.tanpa_triase": ("This filing never reached triage, so a vote cannot tune any threshold.",
                         "此公告未進入分類階段，投票無法調整門檻。",
                         "Pengumuman ini tidak sampai ke triase, jadi suara tidak bisa menyetel ambang."),
    "rv.lanjut": ("✔ Approve and send to the verifier", "✔ 核准並送驗證", "✔ Setujui, teruskan ke pemeriksa"),
    "cek.satuan.beda": ("Unit '{satuan}' is not written in the quote or the item label (written: {tertulis})",
                        "引文及項目標題中未出現單位「{satuan}」（實際：{tertulis}）",
                        "Satuan '{satuan}' tidak tertulis di kutipan maupun label butir (tertulis: {tertulis})"),
    "rv.keyakinan_info": (
        "Approving does not publish it directly: the figures still have to pass every verifier check.",
        "核准不會直接發布：數字仍須通過所有驗證檢查。",
        "Menyetujui tidak langsung menerbitkan: angkanya tetap harus lolos semua pemeriksaan."),
}


_DIMUAT: set[str] = set()


def _muat_tambahan() -> None:
    """Gabungkan kunci dari app/teks/*.py (lihat app/teks/__init__.py). Aman dipanggil ulang."""
    import importlib
    import pkgutil
    from . import teks
    for m in sorted(pkgutil.iter_modules(teks.__path__), key=lambda x: x.name):
        if m.name in _DIMUAT:
            continue
        tambahan = getattr(importlib.import_module(f"{teks.__name__}.{m.name}"), "T", {})
        bentrok = set(tambahan) & set(_T)
        if bentrok:
            raise ValueError(f"app/teks/{m.name}.py menimpa kunci yang sudah ada: {sorted(bentrok)[:5]}")
        _T.update(tambahan)
        _DIMUAT.add(m.name)


_muat_tambahan()


def normal(kode: str | None) -> str:
    return kode if kode in BAHASA else BAWAAN


def t(kunci: str, bahasa: str = BAWAAN, **param) -> str:
    """Terjemahkan satu kunci. Kunci yang tidak dikenal tampil sebagai ⟦kunci⟧ supaya terlihat."""
    baris = _T.get(kunci)
    if baris is None:
        return f"⟦{kunci}⟧"
    teks = baris[URUTAN.index(normal(bahasa))] or baris[2]
    if param:
        try:
            return teks.format(**param)
        except (KeyError, IndexError):
            return teks
    return teks


def angka(x, bahasa: str, desimal: int | None = None):
    """Format angka menurut bahasa: 1,480,000.5 (EN/中文) atau 1.480.000,5 (ID).

    Selain int/float dikembalikan apa adanya. Tanpa `desimal`: bilangan bulat tanpa
    desimal, pecahan kecil (< 100) dua desimal, sisanya tanpa desimal.
    """
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return x
    if desimal is None:
        desimal = 0 if float(x).is_integer() or abs(x) >= 100 else 2
    s = f"{x:,.{desimal}f}"
    if normal(bahasa) == "id":
        s = s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")
    return s


def pesan(kunci: str, **param) -> dict:
    """Pesan agent: kode + parameter + kalimat Indonesia (untuk JSON mentah & jejak lama)."""
    teks = t(kunci, "id", **{k: angka(v, "id") for k, v in param.items()})
    return {"kode": kunci, "param": param, "teks": teks}


def tr(obj, bahasa: str, cadangan: str = "") -> str:
    """Terjemahkan pesan agent. Terima dict pesan, daftar pesan, atau teks biasa."""
    if isinstance(obj, list):
        return "; ".join(tr(o, bahasa).rstrip(".。") for o in obj)
    if isinstance(obj, dict) and obj.get("kode"):
        param = dict(obj.get("param") or {})
        for nama, kunci in (obj.get("param_kode") or {}).items():
            param[nama] = t(kunci, bahasa)
        return t(obj["kode"], bahasa, **{k: angka(v, bahasa) for k, v in param.items()})
    if isinstance(obj, dict) and "nama" in obj and "alasan" in obj:
        return f"{tr(obj['nama'], bahasa)} — {tr(obj['alasan'], bahasa)}"
    if isinstance(obj, str):
        return obj
    return cadangan


def semua_kunci() -> dict[str, tuple[str, str, str]]:
    return dict(_T)
