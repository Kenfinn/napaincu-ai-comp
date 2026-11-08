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
    # --- umum / menu -----------------------------------------------------------
    "merek.sub": ("Taiwan stocks", "台股", "Saham TW"),
    "nav.watchlist": ("Watchlist", "自選股", "Watchlist"),
    "nav.feed": ("Alerts", "警示", "Peringatan"),
    "nav.valuasi": ("Valuation {kode}", "評價 {kode}", "Valuasi {kode}"),
    "nav.api": ("API", "API", "API"),
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
    "st.terbit": ("published", "已發布", "terbit"),
    "st.ditolak": ("rejected", "已拒絕", "ditolak"),
    "st.ditahan": ("held", "暫緩", "ditahan"),
    "st.dilewati": ("skipped", "已略過", "dilewati"),

    # --- feed --------------------------------------------------------------------
    "feed.kicker": ("MOPS filings · processed by the agent", "MOPS 重大訊息 · 由代理處理",
                    "Pengumuman MOPS · diproses agent"),
    "feed.judul": ("Alerts", "警示", "Peringatan"),
    "feed.kenapa": ("Why four numbers, not one", "為何是四個數字而非一個", "Kenapa empat angka, bukan satu"),
    "feed.kenapa_isi": (
        "Three of the four endings are not “published”. A system that cannot stop is not an agent; it is a pipeline.",
        "四種結果中有三種不是「發布」。不會停下來的系統不是代理，而只是流水線。",
        "Tiga dari empat akhir bukan “terbit”. Sistem yang tidak bisa berhenti bukan agent — itu pipeline."),
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
    "msg.dihapus": ("{kode} removed from the watchlist.", "已將 {kode} 從自選股移除。",
                    "{kode} dihapus dari watchlist."),
    "msg.tarik_ok": ("Checked: {n} filings from watchlisted issuers in this fetch, {baru} new.",
                     "檢查完成：本次擷取中有 {n} 則自選股公告，其中 {baru} 則為新公告。",
                     "Diperiksa: {n} pengumuman emiten watchlist di tarikan ini, {baru} baru."),
    "msg.tarik_gagal": ("Fetch failed ({sebab}). The last stored data is still used.",
                        "擷取失敗（{sebab}），仍使用最近儲存的資料。",
                        "Penarikan gagal ({sebab}). Data terakhir yang tersimpan tetap dipakai."),

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
}


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
