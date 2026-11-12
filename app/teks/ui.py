"""Teks antarmuka pengguna ramah awam untuk perombakan UI/UX v1.1 (U2–U8).

Semua kunci diawali dengan 'ui.' agar tidak menimpa kunci lama di app/i18n.py.
Urutan tuple: (English, 繁體中文, Bahasa Indonesia).
"""

T = {
    # --- U2: Kerangka, navigasi samping, bilah ponsel, remah roti, pita ---
    "ui.nav.pantau": ("Monitor", "監控", "Pantau"),
    "ui.nav.tinjau": ("Review & Rules", "審查與規則", "Tinjau"),
    "ui.nav.asisten": ("Assistant", "智慧助理", "Asisten"),
    "ui.nav.lainnya": ("Reference", "其他資源", "Lainnya"),
    "ui.nav.buka_menu": ("Open navigation menu", "開啟導覽選單", "Buka menu navigasi"),
    "ui.nav.tutup_menu": ("Close navigation menu", "關閉導覽選單", "Tutup menu navigasi"),
    "ui.tutup": ("Dismiss notice", "關閉提示", "Tutup pemberitahuan"),
    "ui.status.judul": ("System status", "系統狀態", "Status sistem"),
    "ui.status.model_polos": (
        "Agent uses {model}",
        "代理使用 {model}",
        "Agent memakai {model}",
    ),
    "ui.status.aturan_polos": (
        "Agent uses deterministic rule checks (no API key required)",
        "代理使用確定性規則檢查（無須 API 金鑰）",
        "Agent memakai pemeriksaan aturan deterministik (tanpa kunci API)",
    ),
    "ui.status.sumber_nyata": (
        "Live exchange filings (TWSE & TPEx)",
        "交易所即時公告（TWSE 與 TPEx）",
        "Pengumuman resmi bursa (TWSE & TPEx)",
    ),
    "ui.status.sumber_fixture": (
        "Built-in sample filings",
        "內建範例公告",
        "Data contoh bawaan",
    ),
    "ui.status.tarik_waktu": (
        "Last fetched {waktu} UTC",
        "最後更新：{waktu} UTC",
        "Terakhir ditarik {waktu} UTC",
    ),
    "ui.status.tarik_belum": (
        "Not fetched from exchange yet",
        "尚未從交易所擷取最新公告",
        "Belum ditarik dari bursa",
    ),
    "ui.remah.peringatan": ("Alerts", "警示動態", "Peringatan"),
    "ui.remah.saham": ("Stocks", "個股", "Saham"),
    "ui.remah.review": ("Review queue", "人工審查", "Antrean review"),
    "ui.remah.ambang": ("Thresholds", "門檻設定", "Ambang"),
    "ui.remah.watchlist": ("Watchlist", "自選股", "Watchlist"),
    "ui.remah.valuasi": ("Valuation", "評價分析", "Valuasi"),
    "ui.remah.jejak": ("Audit trail", "稽核軌跡", "Jejak audit"),

    # --- U3: Feed peringatan ---
    "ui.feed.ringkas_semua": ("All filings", "全部公告", "Semua pengumuman"),
    "ui.feed.arti_terbit": (
        "Verified by all checks and ready to read.",
        "已通過所有驗證檢查，可直接閱讀。",
        "Lolos semua pemeriksaan dan siap dibaca.",
    ),
    "ui.feed.arti_ditahan": (
        "Waiting for your decision before publishing.",
        "等待您的確認後才會發布。",
        "Menunggu keputusan Anda sebelum diterbitkan.",
    ),
    "ui.feed.arti_dilewati": (
        "Routine or non-financial filings filtered out.",
        "已過濾的例行或非財務類公告。",
        "Pengumuman rutin atau non-keuangan yang disaring.",
    ),
    "ui.feed.filter_semua": ("All types", "全部類型", "Semua jenis"),
    "ui.feed.filter_valuasi": ("Valuation", "評價變動", "Valuasi"),
    "ui.feed.filter_risiko": ("Risk (Guarantees & Loans)", "風險（背書與貸與）", "Risiko"),
    "ui.feed.filter_modal": ("Capital & Dividends", "資本與股利", "Modal"),
    "ui.feed.filter_laporan": ("Quarterly Reports", "季報與財報", "Laporan kuartal"),
    "ui.feed.filter_tata_kelola": ("Governance", "公司治理", "Tata kelola"),
    "ui.feed.filter_berat": ("Distress", "重大異常", "Berat"),
    "ui.feed.hari_ini": ("Today", "今天", "Hari ini"),
    "ui.feed.kemarin": ("Yesterday", "昨天", "Kemarin"),
    "ui.feed.tindakan_review": (
        "Action: review filing →",
        "下一步：前往審查 →",
        "Tindakan: review →",
    ),
    "ui.feed.kenapa_label": (
        "Why are most filings archived?",
        "為何多數公告會被歸檔？",
        "Kenapa sebagian besar diarsip?",
    ),
    "ui.feed.kosong_judul": (
        "No filings match your current view",
        "目前沒有符合條件的公告",
        "Belum ada pengumuman yang cocok dengan tampilan ini",
    ),
    "ui.feed.kosong_isi": (
        "Add stocks to your watchlist or fetch the latest exchange announcements to start monitoring.",
        "請先將關注的股票加入自選股，或立即從交易所擷取最新重大訊息。",
        "Tambahkan saham ke watchlist atau tarik pengumuman terbaru dari bursa untuk mulai memantau.",
    ),
    "ui.feed.tambah_wl": (
        "+ Add stocks to watchlist",
        "+ 新增股票至自選股",
        "+ Tambah saham ke watchlist",
    ),

    # --- U4: Detail peringatan & _sinyal.html ---
    "ui.al.artinya_judul": ("What this means for you", "對您的意義", "Artinya untuk Anda"),
    "ui.al.artinya_terbit_dcf": (
        "Verified filing that shifts the DCF scenario assumptions. Review the before-and-after numbers below.",
        "此公告已通過驗證並改變 DCF 情境假設，請參考下方前後對比數字。",
        "Pengumuman terverifikasi yang menggeser skenario DCF. Lihat perbandingan angka sebelum dan sesudah di bawah.",
    ),
    "ui.al.artinya_terbit_sinyal": (
        "Verified filing with material financial or governance impact. DCF baseline stays unchanged until quarterly statements update.",
        "此公告已通過驗證，具重大財務或治理影響；DCF 基準值將於季報更新時反映。",
        "Pengumuman terverifikasi dengan dampak keuangan atau tata kelola penting. Nilai dasar DCF tetap sampai laporan kuartal terbit.",
    ),
    "ui.al.artinya_ditahan": (
        "Held for human review: the agent stopped automatically because a safety check failed or needed analyst confirmation.",
        "暫緩發布並交由人工審查：因安全檢查未通過或需分析師確認，代理已自動停止。",
        "Ditahan untuk review manusia: agent berhenti otomatis karena pemeriksaan gagal atau butuh konfirmasi analis.",
    ),
    "ui.al.artinya_dilewati": (
        "Archived automatically: this filing does not alter valuation inputs or trigger a risk signal.",
        "已自動歸檔：此公告不影響評價輸入，亦未觸發風險訊號。",
        "Diarsipkan otomatis: pengumuman ini tidak mengubah input valuasi maupun memicu sinyal risiko.",
    ),
    "ui.al.angka_kunci": ("Key figures", "關鍵數字", "Angka kunci"),
    "ui.al.dokumen_asli": ("From the original filing", "原始公告摘錄與來源", "Dari dokumen asli"),
    "ui.al.cek_ringkas_ok": (
        "{lolos} of {total} verification checks passed",
        "通過 {lolos} / {total} 項驗證檢查",
        "{lolos} dari {total} pemeriksaan lolos",
    ),
    "ui.al.cek_ringkas_gagal": (
        "{gagal} failed of {total} checks ({daftar})",
        "{total} 項檢查中有 {gagal} 項未通過（{daftar}）",
        "{gagal} gagal dari {total} pemeriksaan ({daftar})",
    ),
    "ui.al.buka_saham": ("Open stock page ({kode})", "開啟個股頁面（{kode}）", "Buka halaman saham ({kode})"),
    "ui.al.buka_review": ("Open review queue →", "前往人工審查佇列 →", "Buka antrean review →"),
    "ui.al.buka_jejak": ("View audit trail ({n} steps)", "查看稽核軌跡（{n} 步驟）", "Lihat jejak audit ({n} langkah)"),
    "ui.al.detail_teknis": ("Triage & privacy details", "分流分數與隱私保護詳情", "Rincian triase & privasi"),
    "ui.info.g_tersirat": (
        "Implied perpetual growth rate (g): the annual free-cash-flow growth rate baked into the current stock price.",
        "市場隱含永續成長率 (g)：目前股價所反映的未來每年自由現金流成長率。",
        "Pertumbuhan tersirat (g): laju pertumbuhan arus kas bebas tahunan yang sudah tercermin di harga saham saat ini.",
    ),
    "ui.info.wacc": (
        "Weighted Average Cost of Capital: the blended annual return required by debt and equity holders.",
        "加權平均資金成本 (WACC)：債權人與股東要求的綜合年化報酬率。",
        "WACC (Biaya Modal Rata-Rata Tertimbang): tingkat imbalan tahunan gabungan yang disyaratkan pemberi pinjaman dan pemegang saham.",
    ),
    "ui.info.fcff": (
        "Free Cash Flow to Firm: operating cash flow minus capital expenditures, available to all capital providers.",
        "企業自由現金流 (FCFF)：營業現金流扣除資本支出後，可供全體資金提供者分配的現金。",
        "Arus Kas Bebas Perusahaan (FCFF): arus kas operasi dikurangi belanja modal (capex).",
    ),
    "ui.info.penjaminan": (
        "Endorsements & guarantees (背書保證): promises to back another company's debt. High ratios vs equity increase credit risk.",
        "背書保證：為其他公司債務提供擔保。佔淨值比例過高時會增加連帶信用風險。",
        "Penjaminan utang (背書保證): komitmen menjamin utang pihak lain. Rasio tinggi terhadap ekuitas meningkatkan risiko kredit.",
    ),
    "ui.info.materialitas": (
        "Materiality compares the transaction size against the company's market cap or equity.",
        "重大性：將交易金額與公司市值或股東權益進行比例對照。",
        "Materialitas membandingkan nilai transaksi terhadap kapitalisasi pasar atau ekuitas perusahaan.",
    ),

    # --- U5: Halaman saham (6 tab) ---
    "ui.sh.ringkasan_lede": (
        "Plain-language summary of valuation, growth, profitability, balance sheet, and recent MOPS filings.",
        "以白話整理評價、成長、獲利能力、資產負債表與近期重大訊息的綜合摘要。",
        "Ringkasan bahasa polos atas valuasi, pertumbuhan, profitabilitas, neraca, dan pengumuman MOPS terbaru.",
    ),
    "ui.sh.valuasi_kalimat": (
        "At NT$ {harga}, the market price assumes free cash flow grows {g} per year forever (discount rate WACC {wacc}, ceiling {batas}).",
        "以目前股價 {harga} 元計算，市場價格隱含自由現金流每年永續成長 {g}（折現率 WACC 為 {wacc}，成長上限 {batas}）。",
        "Harga sekarang {harga} NTD mengasumsikan arus kas bebas tumbuh {g} per tahun selamanya (diskonto WACC {wacc}, batas {batas}).",
    ),
    "ui.sh.valuasi_langkah_beta": (
        "Temporary beta 1.0 is used so this page loads immediately. Official 2-year weekly beta vs TAIEX is calculating in the background; refresh in 1–2 minutes.",
        "為確保頁面立即開啟，暫時採用 Beta 1.0。系統正在背景計算 2 年期每週股價對加權指數之官方 Beta，請於 1–2 分鐘後重新整理。",
        "Beta sementara 1.0 dipakai agar halaman langsung terbuka. Beta resmi 2 tahun terhadap TAIEX sedang dihitung di latar belakang; muat ulang dalam 1–2 menit.",
    ),
    "ui.sh.keu_langkah": (
        "Try switching between Quarterly/Annual or check the official MOPS financial statements directly.",
        "請嘗試切換季報／年報，或直接開啟公開資訊觀測站（MOPS）原始財報核對。",
        "Coba ganti periode Kuartalan/Tahunan atau buka langsung laporan resmi di MOPS.",
    ),
    "ui.sh.sumber_lipat": (
        "Technical input sources & provenance",
        "技術輸入來源與資料出處",
        "Sumber input teknis & asal data",
    ),
    "ui.info.eps": (
        "Earnings Per Share (EPS): net profit divided by total common shares outstanding.",
        "每股盈餘 (EPS)：稅後淨利除以流通在外普通股股數。",
        "Laba per saham (EPS): laba bersih dibagi jumlah saham beredar.",
    ),
    "ui.info.roe": (
        "Return on Equity (ROE): net income as a percentage of shareholders' equity.",
        "股東權益報酬率 (ROE)：稅後淨利佔股東權益的百分比，衡量自有資本獲利效率。",
        "Return on Equity (ROE): laba bersih dibagi ekuitas pemegang saham.",
    ),
    "ui.info.fcf": (
        "Free Cash Flow (FCF): operating cash flow minus capital expenditures.",
        "自由現金流 (FCF)：營業活動現金流量扣除資本支出。",
        "Arus Kas Bebas (FCF): arus kas operasi dikurangi belanja modal.",
    ),
    "ui.info.g_pasar": (
        "Market implied growth (g): perpetual annual FCFF growth rate implied by the current stock price.",
        "市場隱含成長率 (g)：目前股價所隱含的未來每年企業自由現金流永續成長率。",
        "Pertumbuhan tersirat pasar (g): laju pertumbuhan tahunan FCFF selamanya yang tersirat pada harga saham saat ini.",
    ),
    "ui.info.batas_g": (
        "Terminal growth ceiling: maximum long-run growth assumption (capped near long-term nominal GDP / risk-free rate).",
        "終值成長率上限：長期永續成長率之合理上限（通常不超過長期名目 GDP 或無風險利率）。",
        "Batas pertumbuhan terminal: batas atas asumsi pertumbuhan jangka panjang (di dekat pertumbuhan ekonomi jangka panjang).",
    ),
    "ui.info.beta": (
        "Beta measures how sensitive the stock's weekly returns are relative to the TAIEX market index.",
        "Beta 係數衡量個股每週報酬率相對於台灣加權指數（TAIEX）的波動敏感度。",
        "Beta mengukur kepekaan imbal hasil mingguan saham terhadap pergerakan indeks pasar TAIEX.",
    ),
    "ui.info.per": (
        "Price-to-Earnings Ratio (P/E): share price divided by trailing 12-month EPS.",
        "本益比 (P/E)：股價除以過去四季每股盈餘。",
        "Rasio Harga terhadap Laba (PER): harga saham dibagi EPS 12 bulan terakhir.",
    ),
    "ui.info.pbr": (
        "Price-to-Book Ratio (P/B): share price divided by book value per share.",
        "股價淨值比 (P/B)：股價除以每股淨值。",
        "Rasio Harga terhadap Nilai Buku (PBR): harga saham dibagi nilai buku per lembar.",
    ),

    # --- U6: Review dan Ambang ---
    "ui.rv.lede": (
        "Every filing below was paused by the agent. Review the source quote and choose whether to publish or archive.",
        "以下每則公告皆由代理自動暫緩。請核對原始引文後，決定要核准發布或歸檔。",
        "Setiap pengumuman di bawah ditahan otomatis oleh agent. Periksa kutipan sumber lalu pilih terbitkan atau arsipkan.",
    ),
    "ui.rv.konsekuensi_setujui": (
        "Approve & publish moves this alert to the public feed with your reviewer note attached.",
        "「核准並發布」會將此警示連同您的審查備註一併公開至動態牆。",
        "Setujui & terbitkan memindahkan peringatan ini ke feed publik beserta catatan review Anda.",
    ),
    "ui.rv.konsekuensi_arsip": (
        "Reject / archive hides this filing from active alerts and logs your reason in the audit trail.",
        "「拒絕／歸檔」會將此公告移出活躍警示，並將原因記錄於稽核軌跡。",
        "Tolak / arsipkan menyimpan pengumuman ke arsip dan mencatat alasannya di jejak audit.",
    ),
    "ui.rv.filter_semua": ("All reasons", "全部原因", "Semua sebab"),
    "ui.rv.angka_ditarik": ("Extracted figures & quotes", "擷取數字與原始引文", "Angka yang ditarik & kutipan"),
    "ui.amb.lede_1": (
        "A triage threshold (0.40 to 0.90) decides how confident the agent must be before a filing passes screening.",
        "分流門檻（0.40 至 0.90）決定代理在放行某條款公告前所需的最低信心分數。",
        "Ambang triase (0,40 sampai 0,90) menentukan batas skor keyakinan minimum agar pengumuman lolos penyaringan.",
    ),
    "ui.amb.lede_2": (
        "Voting 👍 on an alert lowers that clause's threshold by 0.02 (more sensitive); voting 👎 raises it by 0.05 (stricter).",
        "在警示頁點擊 👍 會將該條款門檻調降 0.02（更靈敏）；點擊 👎 則調升 0.05（更嚴格）。",
        "Tombol 👍 pada peringatan menurunkan ambang pasal 0,02 (lebih peka), sedangkan 👎 menaikkan 0,05 (lebih ketat).",
    ),
    "ui.amb.profil_judul": ("Risk profile for signal severity", "訊號嚴重度之風險屬性", "Profil risiko tingkat sinyal"),
    "ui.amb.profil_konservatif": (
        "Conservative: flags smaller guarantees, debt ratios, and capital changes early.",
        "保守型：對較小比例的背書保證、負債比與資本變動提早發出提醒。",
        "Konservatif: menandai penjaminan, rasio utang, dan perubahan modal lebih dini.",
    ),
    "ui.amb.profil_moderat": (
        "Moderate: balanced thresholds suited for general fundamental monitoring.",
        "穩健型：採用平衡門檻，適合一般基本面監控。",
        "Moderat: ambang seimbang untuk pemantauan fundamental umum.",
    ),
    "ui.amb.profil_agresif": (
        "Aggressive: highlights only large transactions or severe governance events.",
        "積極型：僅在重大交易金額或嚴重治理事件時標示高風險。",
        "Agresif: hanya menyorot transaksi besar atau peristiwa tata kelola serius.",
    ),
    "ui.amb.nama_pasal": ("Filing topic", "公告條款主題", "Topik pasal"),

    # --- U7: Watchlist, Valuasi, Jejak audit ---
    "ui.wl.lede": (
        "Monitor your selected Taiwan stocks for material MOPS filings and automatic DCF valuation updates.",
        "追蹤您選擇的台灣上市櫃股票，自動監控重大訊息並更新 DCF 評價。",
        "Pantau saham pilihan Anda di bursa Taiwan untuk pengumuman material MOPS dan pembaruan valuasi DCF otomatis.",
    ),
    "ui.wl.label_cari": ("Stock code or company name", "股票代號或公司名稱", "Kode atau nama saham"),
    "ui.wl.placeholder": ("e.g. 2330, TSMC, 台積電, MediaTek", "例：2330、TSMC、台積電、聯發科", "mis. 2330, TSMC, 台積電, MediaTek"),
    "ui.wl.k_harga": ("Price (NTD)", "股價 (NTD)", "Harga (NTD)"),
    "ui.wl.k_ubah": ("Change", "漲跌幅", "Perubahan"),
    "ui.wl.konfirmasi_hapus": (
        "Remove {kode} from your watchlist?",
        "確定要從自選股移除 {kode} 嗎？",
        "Hapus {kode} dari watchlist Anda?",
    ),
    "ui.wl.contoh_judul": ("Popular Taiwan stocks to try:", "常見台灣代表性個股：", "Contoh saham populer untuk dicoba:"),
    "ui.jj.ringkasan_polos": (
        "The agent completed {langkah} steps in {detik} s, called the language model {panggilan} time(s), and ended as {status}: {alasan}",
        "代理於 {detik} 秒內完成 {langkah} 個步驟，呼叫語言模型 {panggilan} 次，最終狀態為「{status}」：{alasan}",
        "Agent menyelesaikan {langkah} langkah dalam {detik} detik, memanggil model {panggilan} kali, dan berakhir {status}: {alasan}",
    ),
    "ui.jj.meta_teknis": (
        "Technical metrics (tokens, cost, retries, raw file)",
        "技術指標（Token 數、費用、重試次數與原始檔）",
        "Metrik teknis (token, biaya, percobaan ulang, berkas mentah)",
    ),
}
