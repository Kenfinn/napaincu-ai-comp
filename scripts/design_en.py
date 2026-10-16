"""Buat versi bahasa Inggris dari layar desain (design/*.dc.html) ke design/en/.

Versi Indonesia tetap di design/; versi Inggris dipakai untuk Figma dan materi lomba.
Teks diterjemahkan per node teks lewat kamus EN di bawah. Node yang tidak ada di kamus
hanya diubah format angkanya (2.380 -> 2,380; 6,29% -> 6.29%). Skrip melaporkan node
yang masih mengandung huruf tapi tidak ada di kamus, supaya tidak ada yang terlewat.

    python3 scripts/design_en.py
    node scripts/render_design.js design/en
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "design")
OUT = os.path.join(SRC, "en")
FILES = ["Main", "DetailPeringatan", "Valuasi", "RiwayatNilaiWajar", "TanyaJawab", "Watchlist",
         "JejakAudit", "NotifPonsel", "AlurState", "Arsitektur"]

EN = {
    # --- shared / Main
    "Saham TW": "TW Stocks",
    "Peringatan": "Alerts",
    "Tanya Jawab": "Q&A",
    "Jejak Audit": "Audit Trail",
    "Pemantauan": "Monitoring",
    "Aktif — cek 15 menit lalu": "Active — checked 15 min ago",
    "20 emiten · 711 pengumuman terindeks": "20 issuers · 711 filings indexed",
    "Peringatan hari ini": "Today's alerts",
    "Dari 26 pengumuman baru, 4 dinilai mengubah kesimpulan valuasimu":
        "Of 26 new filings, 4 change your valuation conclusion",
    "Semua": "All",
    "Belum dibaca": "Unread",
    "Ditandai": "Flagged",
    "第 24 款 · AKUISISI ASET": "第 24 款 · ASSET ACQUISITION",
    "Pengumuman perolehan aset tetap senilai US$75 juta oleh anak usaha":
        "Subsidiary acquires fixed assets worth US$75 million",
    "Nilai wajar": "Fair value",
    "Dampak": "Impact",
    "Turun 0,35% — kesimpulan": "Down 0.35% — conclusion",
    "tidak berubah": "unchanged",
    ", tetap overvalued terhadap harga 2.380": ", still overvalued vs the 2,380 price",
    "Abaikan": "Dismiss",
    "Tandai": "Flag",
    "Buka valuasi": "Open valuation",
    "Anak usaha Fubon Life mengakuisisi dana infrastruktur KKR Helix B SCSp":
        "Subsidiary Fubon Life acquires the KKR Helix B SCSp infrastructure fund",
    "Dampak — kesimpulan berubah": "Impact — conclusion changed",
    "Turun 4,7%. Dari": "Down 4.7%. From",
    "menjadi": "to",
    "wajar": "fair",
    "Wajar": "Fair",
    "WAJAR": "FAIR",
    "terhadap harga 89,3": "vs the 89.3 price",
    "第 11 款 · KONTRAK": "第 11 款 · CONTRACT",
    "Penandatanganan kontrak pasokan jangka panjang": "Long-term supply contract signed",
    "第 4 款 · PENDAPATAN": "第 4 款 · REVENUE",
    "Pengumuman pendapatan konsolidasi Agustus 2026": "Consolidated revenue for August 2026",
    "22 pengumuman lain dinilai tidak relevan dengan profil risikomu":
        "22 other filings judged not relevant to your risk profile",
    "Lihat alasannya": "See why",
    "Ringkasan watchlist": "Watchlist summary",
    "naik": "up",
    "turun": "down",
    "konvensi bursa TW": "Taiwan market convention",
    "Kinerja agent · 7 hari": "Agent performance · 7 days",
    "Pengumuman diproses": "Filings processed",
    "Dikirim sebagai peringatan": "Sent as alerts",
    "Kamu buka": "Opened by you",
    "Ditolak verifier angka": "Rejected by number verifier",
    "Ambang relevansi naik otomatis setelah kamu mengabaikan 3 peringatan pasal 4 berturut-turut.":
        "Relevance threshold raised automatically after you dismissed 3 clause-4 alerts in a row.",
    # --- DetailPeringatan
    "Kembali ke peringatan": "Back to alerts",
    "Peringatan 2 dari 4": "Alert 2 of 4",
    "SUMBER RESMI": "OFFICIAL SOURCE",
    "Isi pengumuman": "Filing content",
    "butir bernomor sesuai format wajib regulator": "numbered items in the regulator's mandatory format",
    "Nama dan sifat objek": "Name and nature of the asset",
    "KKR Helix B SCSp — dana infrastruktur": "KKR Helix B SCSp — infrastructure fund",
    "Tanggal kejadian": "Date of event",
    "Jumlah unit, harga per unit, dan nilai total transaksi":
        "Units, unit price and total transaction value",
    "DIPAKAI DI MODEL": "USED IN MODEL",
    "Tanpa jumlah unit, tanpa harga per unit — total komitmen tidak melebihi":
        "No unit count or unit price — total commitment not exceeding",
    "US$75 juta": "US$75 million",
    "Pihak lawan transaksi dan hubungannya": "Counterparty and relationship",
    "Kohlberg Kravis Roberts & Co. L.P. — tidak ada hubungan istimewa":
        "Kohlberg Kravis Roberts & Co. L.P. — no related-party relationship",
    "Bila pihak lawan adalah pihak berelasi": "If the counterparty is a related party",
    "Tidak berlaku": "Not applicable",
    "Nama, jabatan, dan telepon juru bicara ada di dokumen asli tapi":
        "The spokesperson's name, title and phone are in the original filing but",
    "tidak disimpan": "not stored",
    "— minimisasi data pribadi sesuai Pasal 14.1.": "— personal-data minimisation under Art. 14.1.",
    "Kesimpulan berubah": "Conclusion changed",
    "Sebelumnya": "Before",
    "Sekarang": "Now",
    "Harga pasar hari ini": "Market price today",
    "selisih −1,3% dari nilai wajar": "−1.3% vs fair value",
    "Apa yang bergeser di model": "What moved in the model",
    "Komitmen kas keluar": "Cash commitment out",
    "+US$75 jt": "+US$75 m",
    "Kas & setara kas": "Cash & equivalents",
    "−2,4 mlr NTD": "−NT$2.4 bn",
    "Nilai perusahaan": "Enterprise value",
    "+2,4 mlr NTD": "+NT$2.4 bn",
    "Nilai wajar per lembar": "Fair value per share",
    "Verifier mencocokkan US$75 juta ke butir 3 dokumen asli. Cocok — peringatan diteruskan.":
        "Verifier matched US$75 million to item 3 of the original filing. Match — alert sent.",
    "Berguna untukmu?": "Useful to you?",
    "Berguna": "Useful",
    "Tidak relevan": "Not relevant",
    "Jawabanmu menyetel ambang relevansi untuk pasal 24 pada emiten sektor keuangan.":
        "Your answer tunes the relevance threshold for clause 24 at financial-sector issuers.",
    "Lihat jejak agent": "View agent trace",
    "Buka valuasi penuh": "Open full valuation",
    # --- Valuasi
    "Data per 14 Sep 2026 · FY2025": "Data as of 14 Sep 2026 · FY2025",
    "Ekspor kertas kerja": "Export worksheet",
    "Kesimpulan": "Conclusion",
    "Unlevered DCF · perpetuitas 1 tahap": "Unlevered DCF · single-stage perpetuity",
    "Pasar mengasumsikan pertumbuhan abadi": "The market assumes perpetual growth of",
    "— di atas batas wajar 3,5%": "— above the 3.5% reasonable cap",
    "g tersirat pasar": "Market-implied g",
    "dibalik dari harga hari ini": "reversed from today's price",
    "Batas perpetuitas": "Perpetuity cap",
    "PDB nominal jangka panjang": "Long-run nominal GDP",
    "Nilai wajar bila g = 3,5%": "Fair value if g = 3.5%",
    "vs harga pasar 2.380": "vs market price 2,380",
    "Ini": "This is",
    "bukan target harga": "not a price target",
    ". Angka di atas menunjukkan apa yang harus dipercaya seseorang agar harga hari ini masuk akal — bukan ke mana harga akan bergerak.":
        ". The figures above show what someone must believe for today's price to make sense — not where the price will go.",
    "Sensitivitas nilai wajar per lembar": "Fair value per share: sensitivity",
    "geser asumsi di panel kanan — tabel ini ikut berubah":
        "move the assumptions on the right — this table updates",
    "di bawah harga pasar": "below market price",
    "asumsi aktif": "active assumption",
    "di atas harga pasar": "above market price",
    "Asumsi — bisa diubah": "Assumptions — editable",
    "Setel ulang": "Reset",
    "Pertumbuhan abadi (g)": "Perpetual growth (g)",
    "batas 3,5%": "cap 3.5%",
    "Dasar FCFF": "FCFF base",
    "Tahun terakhir": "Latest year",
    "Rata-rata 3 th": "3-yr average",
    "1.012,8 bio": "1,012.8 bn",
    "726,6 bio": "726.6 bn",
    "Lease masuk utang": "Leases as debt",
    "Jembatan nilai perusahaan": "Enterprise value bridge",
    "Kapitalisasi pasar": "Market cap",
    "+ Utang berbunga": "+ Interest-bearing debt",
    "− Kas & investasi jk pendek": "− Cash & short-term investments",
    "Sumber tiap angka": "Source of every number",
    "9/9 TERSITASI": "9/9 CITED",
    "Neraca konsolidasi 2025": "Consolidated balance sheet 2025",
    "Arus kas 2023–2025": "Cash flows 2023–2025",
    "Lembar saham beredar": "Shares outstanding",
    "Imbal hasil obligasi 10 th": "10-yr bond yield",
    "Premi risiko ekuitas TW": "Taiwan equity risk premium",
    "Setiap angka bisa diklik ke dokumen aslinya. Angka tanpa sumber tidak pernah ditampilkan.":
        "Every number links to its original document. A number without a source is never shown.",
    # --- RiwayatNilaiWajar
    "Valuasi": "Valuation",
    "Riwayat": "History",
    "Jan – 14 Sep 2026 · data contoh untuk mockup": "Jan – 14 Sep 2026 · sample data for mock-up",
    "Nilai wajar terhadap harga pasar": "Fair value vs market price",
    "Nilai wajar hanya bergerak saat ada pengumuman yang memicu perhitungan ulang — bukan setiap hari":
        "Fair value moves only when a filing triggers a recompute — not every day",
    "Harga pasar": "Market price",
    "harga menyalip nilai wajar": "price overtakes fair value",
    "Harga": "Price",
    "Mei": "May",
    "Ags": "Aug",
    "Area berarsir = harga di atas nilai wajar. Sejak 28 Juni, TSMC terus diperdagangkan di atas estimasi kami.":
        "Shaded area = price above fair value. Since 28 June, TSMC has traded above our estimate.",
    "Yang memicu tiap perubahan": "What triggered each change",
    "3 kali": "3 times",
    "Laporan keuangan tahunan FY2025 terbit — FCFF naik ke 1.012,8 bio":
        "FY2025 annual report published — FCFF up to 1,012.8 bn",
    "Laporan kuartal II 2026 — arus kas operasi di atas perkiraan":
        "Q2 2026 report — operating cash flow above estimate",
    "TERBARU": "LATEST",
    "Perolehan aset tetap US$75 juta oleh anak usaha": "Subsidiary acquires US$75 million of fixed assets",
    "Selisih saat ini": "Current gap",
    "harga di atas": "price above",
    "nilai wajar": "fair value",
    "Hari di atas nilai wajar": "Days above fair value",
    "78 dari 257": "78 of 257",
    "Selisih terlebar": "Widest gap",
    "Garis nilai wajar berbentuk anak tangga karena memang begitu cara kerjanya — dihitung ulang hanya saat ada dokumen baru, bukan diinterpolasi supaya terlihat mulus.":
        "The fair-value line is a staircase because that is how it works — recomputed only when a new document arrives, never interpolated to look smooth.",
    # --- TanyaJawab
    "Tanya jawab": "Q&A",
    "Jawaban hanya dari dokumen yang sudah terindeks — tidak ada yang dikarang":
        "Answers come only from indexed documents — nothing is made up",
    "711 dokumen · 20 emiten · s/d 11 Sep 2026": "711 documents · 20 issuers · up to 11 Sep 2026",
    "Pengumuman material apa saja yang dikeluarkan Fubon Financial pada September 2026, dan berapa nilai transaksinya?":
        "Which material announcements did Fubon Financial publish in September 2026, and what were the transaction values?",
    "3 dokumen dibuka · 2,1 dtk": "3 documents opened · 2.1 s",
    "Fubon Financial (2881) mengeluarkan": "Fubon Financial (2881) published",
    "dua": "two",
    "pengumuman material pada September 2026:": "material announcements in September 2026:",
    "Akuisisi dana infrastruktur KKR Helix B SCSp melalui anak usaha Fubon Life. Nilai komitmen":
        "Acquisition of the KKR Helix B SCSp infrastructure fund through subsidiary Fubon Life. Commitment",
    "tidak melebihi US$75 juta": "not exceeding US$75 million",
    ". Pihak lawan Kohlberg Kravis Roberts & Co. L.P., tanpa hubungan istimewa.":
        ". Counterparty: Kohlberg Kravis Roberts & Co. L.P., no related-party relationship.",
    "SUMBER 1": "SOURCE 1",
    "SUMBER 2": "SOURCE 2",
    "butir 3": "item 3",
    "Keikutsertaan dalam Goldman Sachs Asia Financials Corporate Day.":
        "Participation in the Goldman Sachs Asia Financials Corporate Day.",
    "Tidak ada nilai transaksi": "No transaction value",
    "pada pengumuman ini.": "in this announcement.",
    "subjek": "subject",
    "Indeks berhenti di 11 September 2026. Pengumuman setelah tanggal itu belum masuk — jawaban ini tidak mencakupnya.":
        "The index ends on 11 September 2026. Later announcements are not included — this answer does not cover them.",
    "Lihat jejak": "View trace",
    "Salin dengan sitasi": "Copy with citations",
    "2 sumber · 0 klaim tanpa sumber": "2 sources · 0 unsourced claims",
    "Tanyakan apa saja tentang 20 emiten yang terindeks…": "Ask anything about the 20 indexed issuers…",
    "Mode penilaian juri": "Judge evaluation mode",
    "Muat berkas soal, sistem menjawab semuanya berurutan dan mencatat skornya.":
        "Load a question file; the system answers every question in order and records the score.",
    "Muat berkas soal": "Load question file",
    "Hasil uji terakhir": "Last test run",
    "Soal dijawab": "Questions answered",
    "Cocok kunci jawaban": "Matched answer key",
    "Menolak menjawab": "Declined to answer",
    "Latensi rata-rata": "Mean latency",
    "2 soal ditolak karena di luar rentang indeks. Menolak dianggap benar — bukan kegagalan.":
        "2 questions declined as outside the index range. Declining counts as correct, not as a failure.",
    "Contoh pertanyaan": "Example questions",
    "Berapa rasio utang terhadap ekuitas TSMC di 2025?": "What was TSMC's debt-to-equity ratio in 2025?",
    "Emiten mana yang mengumumkan akuisisi aset kuartal ini?":
        "Which issuers announced asset acquisitions this quarter?",
    "Apa asumsi WACC yang dipakai untuk Hon Hai, dan dari mana angkanya?":
        "What WACC is assumed for Hon Hai, and where does it come from?",
    # --- Watchlist
    "Watchlist & profil risiko": "Watchlist & risk profile",
    "Dua hal ini yang menentukan peringatan mana yang sampai ke kamu":
        "These two settings decide which alerts reach you",
    "Saham yang dipantau": "Stocks you watch",
    "4 dari maks 20": "4 of max 20",
    "Cari kode atau nama emiten — mis. 2454, 聯發科": "Search by code or name — e.g. 2454, 聯發科",
    "Semikonduktor": "Semiconductors",
    "Manufaktur elektronik": "Electronics manufacturing",
    "Keuangan · multi-lini": "Financials · multi-line",
    "Petrokimia": "Petrochemicals",
    "Label valuasi dihitung ulang tiap kali ada pengumuman baru — bukan tiap hari.":
        "Valuation labels are recomputed whenever a new filing arrives — not daily.",
    "Profil risiko": "Risk profile",
    "Kapan kamu mau diberi tahu?": "When should we notify you?",
    "Semua pengumuman material": "Every material announcement",
    "±26 per hari": "±26 per day",
    "Hanya yang mengubah kesimpulan valuasi": "Only those that change the valuation conclusion",
    "±4 per hari — direkomendasikan": "±4 per day — recommended",
    "Hanya perubahan besar (>10%)": "Only large changes (>10%)",
    "±1 per minggu": "±1 per week",
    "Ambang perubahan nilai wajar": "Fair-value change threshold",
    "Agent menaikkan ambang ini sendiri kalau kamu sering mengabaikan peringatan sejenis.":
        "The agent raises this threshold itself if you keep dismissing similar alerts.",
    "Cara pengiriman": "Delivery",
    "segera setelah terdeteksi": "as soon as detected",
    "Notifikasi ponsel": "Phone notification",
    "hanya jam 08.00–20.00": "08:00–20:00 only",
    "Ringkasan mingguan": "Weekly digest",
    "Senin pagi": "Monday morning",
    "Sentinel tidak pernah terhubung ke rekening efekmu dan tidak bisa melakukan transaksi. Hanya membaca sumber publik.":
        "Sentinel never connects to your brokerage account and cannot trade. It only reads public sources.",
    # --- JejakAudit
    "Jejak audit agent": "Agent audit trail",
    "Setiap langkah tercatat — termasuk yang gagal, yang diulang, dan yang ditolak":
        "Every step is recorded — including failures, retries and rejections",
    "Unduh JSON": "Download JSON",
    "Durasi total": "Total duration",
    "Panggilan tool": "Tool calls",
    "Biaya model": "Model cost",
    "Intervensi manusia": "Human interventions",
    "Urutan langkah": "Step sequence",
    "Memeriksa pengumuman baru": "Checking for new filings",
    "fetch_announcements(codes=20, since=2026-09-11) → 26 baru":
        "fetch_announcements(codes=20, since=2026-09-11) → 26 new",
    "Host utama menolak — beralih ke cadangan": "Primary host refused — switched to backup",
    "mops.twse.com.tw → HTTP 200 tapi isi halaman blokir · beralih ke mopsov.twse.com.tw → berhasil":
        "mops.twse.com.tw → HTTP 200 but a block page · switched to mopsov.twse.com.tw → success",
    "Menyaring berdasarkan nomor pasal": "Screening by clause number",
    "KEPUTUSAN": "DECISION",
    "26 → 6 lolos. Pasal 24, 11, dan 4 relevan dengan profil risiko; 20 sisanya di bawah ambang":
        "26 → 6 pass. Clauses 24, 11 and 4 match the risk profile; the other 20 are below threshold",
    "Membuka isi 6 pengumuman": "Opening 6 filings",
    "fetch_detail(×6) → 6 berhasil, butir bernomor terekstraksi, data pribadi dibuang":
        "fetch_detail(×6) → 6 succeeded, numbered items extracted, personal data dropped",
    "Menghitung ulang valuasi": "Recomputing valuation",
    "KALKULATOR": "CALCULATOR",
    "dcf(2881): nilai wajar 92,4 → 88,1 · dcf(2330): 2.302 → 2.294 · 4 emiten lain tidak berubah":
        "dcf(2881): fair value 92.4 → 88.1 · dcf(2330): 2,302 → 2,294 · 4 other issuers unchanged",
    "Verifier menolak satu draf": "Verifier rejected one draft",
    "DITOLAK": "REJECTED",
    "Draf untuk 1301 menyebut “pendapatan 41,2 miliar”. Tidak ada angka itu di dokumen sumber.":
        "The draft for 1301 cites “revenue of 41.2 billion”. That number is not in the source document.",
    "Peringatan tidak dikirim. Dicatat untuk ditinjau manusia, bukan ditebak ulang.":
        "Alert not sent. Logged for human review, not re-guessed.",
    "Mengirim 4 peringatan bersitasi": "Sending 4 cited alerts",
    "SELESAI": "DONE",
    "Tiap peringatan membawa URL dokumen asli dan daftar asumsi yang dipakai":
        "Each alert carries the original document URL and the assumptions used",
    "Batas kewenangan agent": "Agent permissions",
    "Membaca sumber publik dan menghitung": "Read public sources and compute",
    "Mengirim peringatan bersitasi": "Send cited alerts",
    "Membeli atau menjual saham": "Buy or sell stocks",
    "Mengeluarkan angka tanpa sumber": "Output numbers without a source",
    "Memberi rekomendasi beli/jual": "Give buy/sell recommendations",
    "Uji keamanan terakhir": "Latest security tests",
    "24/24 ditahan": "24/24 blocked",
    "Angka tanpa sumber": "Unsourced numbers",
    "0 lolos": "0 passed",
    "Data pribadi tersimpan": "Personal data stored",
    "0 field": "0 fields",
    "Jejak ini yang diserahkan sebagai": "This trace is what we submit as the",
    "wajib di materi final, bukan dokumen terpisah.":
        "required in the final materials, not a separate document.",
    # --- NotifPonsel
    "Fubon Financial: kesimpulan berubah": "Fubon Financial: conclusion changed",
    "Akuisisi dana KKR senilai US$75 jt. Nilai wajar turun 4,7% — dari undervalued jadi wajar.":
        "US$75 m acquisition of a KKR fund. Fair value down 4.7% — from undervalued to fair.",
    "Kenapa berubah": "Why it changed",
    "menaikkan nilai perusahaan dan menurunkan kas bersih": "raises enterprise value and lowers net cash",
    "Buka dokumen resmi MOPS": "Open the official MOPS filing",
    "Peringatan ini berguna?": "Was this alert useful?",
    "Ya": "Yes",
    "Tidak": "No",
    "Buka valuasi lengkap": "Open full valuation",
    # --- AlurState
    "Deck halaman 5 · Alur tugas & diagram state agent": "Agent task flow & state diagram",
    "Satu pengumuman, enam state, tiga jalan keluar": "One filing, six states, three ways out",
    "DETERMINISTIK": "DETERMINISTIC",
    "Saringan pasal": "Clause screen",
    "Nomor 符合條款 sudah mengklasifikasikan jenis kejadian — menurut regulator, bukan menurut kita.":
        "The 符合條款 clause number already classifies the event — by the regulator, not by us.",
    "DILEWATI": "SKIPPED",
    "Pasal tidak menyentuh input valuasi. Tidak pernah sampai ke model.":
        "Clause doesn't touch a valuation input. Never reaches the model.",
    "Pemilah": "Triage",
    "Menyentuh input valuasi yang mana? Seberapa yakin?": "Which valuation input does it touch? How sure?",
    "ambang 0,55": "threshold 0.55",
    "DITAHAN": "HELD",
    "Keyakinan di bawah ambang → antre tinjauan manusia, tidak dibuang.":
        "Confidence below threshold → human review queue, not discarded.",
    "Penyari": "Extract",
    "Angka berapa, untuk input mana, dan dari kalimat mana persis.":
        "Which number, for which input, from exactly which sentence.",
    "wajib + kutipan": "required + quote",
    "Tidak ada angka yang bisa ditarik dengan kalimat sumbernya.":
        "No number can be extracted together with its source sentence.",
    "Penghitung": "Recompute",
    "Kalkulator DCF dijalankan dua kali — sebelum dan sesudah angka baru.":
        "The DCF calculator runs twice — before and after the new number.",
    "Tanpa jalan keluar — aritmetika tidak bisa “ragu”.": "No exit — arithmetic cannot “hesitate”.",
    "Pemeriksa": "Verify",
    "Tiap angka yang dikutip wajib ditemukan di dokumen sumbernya.":
        "Every quoted number must be found in its source document.",
    "satuan · besaran · sirkularitas": "unit · magnitude · circularity",
    "Angka tidak ada di dokumen. Peringatan tidak terbit, alasan tercatat.":
        "Number not in the document. Alert not published, reason logged.",
    "Peringatan terbit": "Alert published",
    "Agent menyaring, menjelaskan, menyitasi.": "The agent filters, explains and cites.",
    "Manusia yang memutuskan.": "The human decides.",
    "tanpa eksekusi order": "no order execution",
    "Pasal 14.2 melarang aksi berdampak substantif tanpa konfirmasi manusia.":
        "Art. 14.2 forbids substantive actions without human confirmation.",
    "Penyesuaian dinamis pada dua tahap model.": "Dynamic adjustment in the two model stages.",
    "API gagal →": "API fails →",
    "→ kalau tetap gagal, turun ke penalar berbasis aturan dan tandai keluarannya sebagai mode cadangan. Tugas tidak pernah berhenti diam-diam, dan tidak pernah berpura-pura berhasil.":
        "→ if it still fails, fall back to the rule-based reasoner and label the output as fallback. Tasks never stop silently and never pretend to succeed.",
    "Tahap 3 dan 4 sengaja bukan model": "Stages 3 and 4 are deliberately not the model",
    "Di situ letak pertahanannya: angka datang dari aritmetika, dan klaim model diuji balik ke dokumen. Model tidak pernah menghitung, dan tidak pernah menilai dirinya sendiri.":
        "That is the defence: numbers come from arithmetic, and the model's claims are tested against the document. The model never calculates and never grades itself.",
    "Tiga jalan keluar sebelum terbit": "Three ways out before publishing",
    "Dilewati, ditahan, ditolak. Sistem yang tidak bisa berhenti bukan agent — itu pipeline. Kemampuan berhenti inilah butir 3 gerbang kelayakan.":
        "Skipped, held, rejected. A system that cannot stop is not an agent — it is a pipeline. Being able to stop is criterion 3 of the eligibility gate.",
    "Tiap state menulis jejak": "Every state writes a trace",
    "Masukan, keluaran, latensi, token, biaya, jumlah retry. Operation trace yang diwajibkan Appendix 2 lahir dari pemakaian biasa, bukan dikarang belakangan.":
        "Input, output, latency, tokens, cost, retries. The operation trace required by Appendix 2 comes from normal use, not written afterwards.",
    "Gerbang": "Gate",
    "Pasal 4": "Art. 4",
    "① Dekomposisi tugas": "① Task decomposition",
    "[wajib]": "[required]",
    "Enam state berurutan, tiap langkah maju berdasarkan status langkah sebelumnya.":
        "Six ordered states; each step advances on the previous step's status.",
    "② Pemanggilan tool": "② Tool calls",
    "MOPS, kalkulator DCF, API model — tiga sistem eksternal.":
        "MOPS, the DCF calculator, the model API — three external systems.",
    "③ Manajemen state": "③ State management",
    "Tiga jalan keluar, retry, dan penalar cadangan saat tool utama gagal.":
        "Three exits, retries, and a fallback reasoner when the main tool fails.",
    "④ Kontrol risiko": "④ Risk control",
    "Verifikasi keluaran, jejak audit penuh, tanpa eksekusi order.":
        "Output verification, full audit trail, no order execution.",
    # --- Arsitektur
    "Deck halaman 6 · Arsitektur sistem, model, tool, aliran data":
        "System architecture, models, tools and data flow",
    "Model hanya menyentuh dua kotak dari sebelas": "The model touches only two boxes out of eleven",
    "1 · Sumber eksternal": "1 · External sources",
    "重大訊息 · form-POST · kalender ROC (2026 = th 115)": "重大訊息 · form-POST · ROC calendar (2026 = year 115)",
    "Harga penutupan, lembar saham beredar": "Closing price, shares outstanding",
    "Geo-blocked dari luar Taiwan.": "Geo-blocked outside Taiwan.",
    "Balasannya HTTP 200 berisi halaman blokir — gagal tanpa bersuara. Kita memvalidasi":
        "It answers HTTP 200 with a block page — a silent failure. We validate the",
    "bentuk": "shape",
    "balasan, bukan kode statusnya.": "of the response, not its status code.",
    "2 · Pengambilan & pembersihan": "2 · Ingestion & cleaning",
    "Cek keterjangkauan tiap sumber": "Checks that each source is reachable",
    "Penarikan massal ·": "Bulk pull ·",
    "POLITE_DELAY 2,5 dtk": "POLITE_DELAY 2.5 s",
    "711 baris → record + URL sitasi": "711 rows → records + citation URLs",
    "Data pribadi dibuang di sini.": "Personal data is dropped here.",
    "發言人 · 職稱 · 電話 — yang dicatat hanya": "發言人 · 職稱 · 電話 — we log only",
    "bahwa": "that",
    "field itu dibuang, tidak pernah isinya.": "the field was dropped, never its content.",
    "Pasal 14.1 — minimisasi data. Hulu, bukan hilir: tidak ada data pribadi yang bisa sampai ke model karena memang tidak pernah disimpan.":
        "Art. 14.1 — data minimisation. Upstream, not downstream: no personal data can reach the model because it is never stored.",
    "Saringan 符合條款 · 711 → ~30": "符合條款 screen · 711 → ~30",
    "1 · triage.py": "1 · extract.py · triage",
    "Menyentuh input valuasi yang mana?": "Which valuation input is touched?",
    "2 · extract.py": "2 · extract.py · extraction",
    "Angka + kalimat sumbernya": "Number + its source sentence",
    "memanggil": "calls",
    "Angka ada di dokumen? Kalau tidak → tolak": "Is the number in the document? If not → reject",
    "mengorkestrasi kelimanya dan menulis jejak tiap langkah.":
        "orchestrates all five and writes a trace for every step.",
    "4 · Penyajian — FastAPI": "4 · Presentation — FastAPI",
    "Feed peringatan": "Alert feed",
    "Detail + sitasi MOPS + vonis pemeriksa": "Detail + MOPS citation + verifier verdict",
    "DCF, asumsi geser, sensitivitas": "DCF, adjustable assumptions, sensitivity",
    "OpenAPI otomatis": "Auto-generated OpenAPI",
    "Tanpa login.": "No login.",
    "Tidak ada kata sandi disimpan, tidak ada akun evaluator yang perlu dibuat, tidak ada permukaan serangan tambahan.":
        "No stored passwords, no evaluator account to create, no extra attack surface.",
    "Penyedia model — dapat ditukar": "Model provider — swappable",
    "Utama · konteks besar memuat pengumuman Mandarin panjang utuh":
        "Primary · large context fits long Chinese filings whole",
    "Tukar satu": "Swap one",
    ", tanpa ubah kode": ", no code change",
    "Penalar berbasis aturan": "Rule-based reasoner",
    "Cadangan saat API gagal — keluarannya ditandai mode cadangan":
        "Fallback when the API fails — output labelled as fallback",
    "Pengungkapan:": "Disclosure:",
    "konten free tier dipakai Google untuk meningkatkan produknya. Dapat diterima di sini karena pengumuman MOPS adalah dokumen publik":
        "free-tier content is used by Google to improve its products. Acceptable here because MOPS filings are public documents",
    "dan": "and",
    "data pribadi sudah dibuang di lapisan 2. Kalau nanti perlu menganalisis apa pun yang tidak publik, free tier otomatis tidak boleh dipakai lagi.":
        "personal data is already dropped in layer 2. Anything non-public would rule out the free tier.",
    "Penyimpanan — berkas biasa, tanpa basis data": "Storage — plain files, no database",
    "Pengumuman + detail, sudah bersih PII": "Filings + details, PII removed",
    "Tiga kasus uji — aplikasi jalan di mana saja": "Four test cases — the app runs anywhere",
    "Input DCF per emiten + URL sumber tiap angka": "DCF inputs per issuer + a source URL for every number",
    "Jejak audit: latensi, token, biaya, retry per tahap": "Audit trail: latency, tokens, cost, retries per stage",
    "Tanpa basis data karena tidak ada yang membutuhkannya. Juri bisa membuka tiap berkas dengan editor teks dan mencocokkannya sendiri.":
        "No database because nothing needs one. Judges can open every file in a text editor and check it themselves.",
    "Batas": "Trust",
    "kepercayaan": "boundary",
    "Teks pengumuman = data, bukan perintah": "Filing text = data, not commands",
    "Isinya dikendalikan penerbit, jadi ia masuk prompt di dalam pembatas jelas dan tidak pernah boleh mengarahkan tahap mana pun. Inilah bahan uji prompt injection yang diminta Appendix 2.":
        "Its content is controlled by the issuer, so it enters the prompt inside clear delimiters and may never steer any stage. This is the prompt-injection test Appendix 2 asks for.",
    "Tidak ada kunci di repo": "No keys in the repo",
    "Kunci API hanya dibaca dari": "API keys are read only from the",
    "dan tidak pernah ikut tercetak di layar atau jejak mana pun — syarat eksplisit Pasal 6.":
        "and never printed on any screen or trace — an explicit competition rule.",
    "Agent tidak memegang uang": "The agent never touches money",
    "Tidak ada jalur ke broker, tidak ada eksekusi order, tidak ada aksi berdampak substantif. Pasal 14.2 — dan juri menghitungnya sebagai desain yang baik, bukan keterbatasan.":
        "No path to a broker, no order execution, no substantive action. Art. 14.2 — and judges count this as good design, not a limitation.",
}

ATTR = {
    'aria-label="Grafik garis nilai wajar terhadap harga pasar TSMC, Januari sampai September 2026"':
        'aria-label="Line chart of TSMC fair value vs market price, January to September 2026"',
}

# Teks yang memang tidak perlu diterjemahkan (nama, kode, istilah Inggris, URL, path).
KEEP = re.compile(
    r"^(Sentinel|Watchlist|undervalued|Undervalued|OVERVALUED|UNDERVALUED|Retry|TOOL|RETRY 1|"
    r"Prompt injection|operation trace|Email|WACC|NTD|MODEL|DET|retry ×2|environment variable|"
    r"Gemini free tier|Groq · OpenRouter · Anthropic|TWSE / TPEx OpenAPI|MOPS ↗|Investing ↗|"
    r"Damodaran ↗|Jan|Feb|Mar|Apr|Jun|Jul|Sep|FY2025|pipeline\.py|.*\.py|/.*|data/.*|valuation/.*|"
    r"scripts/.*|app/.*|.*twse\.com\.tw.*|ajax_.*|dcf\.compute\(\) ×2|run_.*|.*\(\d{4}\).*|"
    r"3 · Agent — app/agent/|0 · screen\.py|MOPS 公開資訊觀測站|11 September 2026)$"
)

# Satu langkah: titik ribuan dan koma desimal ditukar sekaligus (1.012,8 -> 1,012.8).
# Dua langkah terpisah saling membatalkan (2.358 -> 2,358 -> 2.358).
NUM_ID = re.compile(r"(?<![\w/.,])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+,\d+)(?![\w.,])")
SWAP = str.maketrans({".": ",", ",": "."})


def fix_numbers(t: str) -> str:
    if "twse" in t or "://" in t or "ajax_" in t:
        return t
    t = NUM_ID.sub(lambda m: m.group(1).translate(SWAP), t)
    t = re.sub(r"(\d) dtk\b", r"\1 s", t)
    return t


def translate(src: str, missing: list) -> str:
    out, skip = [], 0
    for part in re.split(r"(<[^>]+>)", src):
        if part.startswith("<"):
            tag = re.match(r"</?\s*([a-zA-Z0-9-]+)", part)
            name = tag.group(1).lower() if tag else ""
            if name in ("style", "script", "helmet"):
                skip += -1 if part.startswith("</") else 1
            for a, b in ATTR.items():
                part = part.replace(a, b)
            out.append(part)
            continue
        if skip or not part.strip():
            out.append(part)
            continue
        norm = " ".join(html.unescape(part).split())
        lead = part[: len(part) - len(part.lstrip())]
        trail = part[len(part.rstrip()):]
        if norm in EN:
            new = EN[norm]
        else:
            new = fix_numbers(norm)
            if re.search(r"[A-Za-z]{2,}", new) and not KEEP.match(new):
                missing.append(new)
        out.append(lead + html.escape(new, quote=False) + trail)
    return "".join(out)


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    missing = []
    for f in FILES:
        src = open(os.path.join(SRC, f + ".dc.html"), encoding="utf-8").read()
        dst = translate(src, missing)
        dst = dst.replace('src="./support.js"', 'src="../support.js"')
        open(os.path.join(OUT, f + ".dc.html"), "w", encoding="utf-8").write(dst)
    if missing:
        print("Belum ada di kamus:")
        for m in dict.fromkeys(missing):
            print("  ", m)
    print(f"{len(FILES)} berkas → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
