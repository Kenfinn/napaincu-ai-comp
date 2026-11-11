# Prompt Antigravity putaran 3 (Q1–Q10), dijalankan berurutan

Untuk Afinzaki. Tempel **Q1** ke Antigravity, satu agent, folder repo ini sebagai
workspace. Setiap prompt di akhirnya menyuruh Antigravity membuka prompt berikutnya di
berkas ini, jadi cukup tempel sekali. Kalau rantainya berhenti, tempel nomor berikutnya
secara manual.

Sebelum ditinggal:
1. Laptop dicolok ke listrik, sleep dimatikan, Wi-Fi tersambung.
2. Di setelan Antigravity, izinkan perintah terminal dan sunting berkas tanpa persetujuan.
3. Buka satu agent, tempel Q1.

Setelah selesai: kirim `docs/laporan-antigravity-3.md` ke Claude. Claude meninjau hasilnya
sebelum kamu Deploy.

| No | ID | Isi | Kenapa |
|---|---|---|---|
| Q1 | | Persiapan | |
| Q2 | G1 | Gold set mengenal semua jalur B1 | Syarat D5; Ferry & Patrice butuh panduan yang benar |
| Q3 | V1 | Tab Valuation tidak menunggu beta, TWSE 307 = tunggu lalu ulang | Demo: emiten baru sekarang ±2 menit |
| Q4 | V2 | Skrip pemanasan cache emiten besar | Demo |
| Q5 | S1 | Cari emiten dengan nama (TSMC, 台積電, 2330) | Demo |
| Q6 | C1a | Tautan Tanya FEAF di menu dan halaman saham | C1 |
| Q7 | C1b | Uji Tanya FEAF, dengan Gemini bila kunci ada di laptop | C1, D5 |
| Q8 | K1 | Draf laporan keamanan | D5, formulir self-assessment |
| Q9 | QA1 | Skrip QA halaman tiga bahasa | QA akhir |
| Q10 | | Laporan akhir | |

---

## Q1. Persiapan

````text
# Q1 dari 10: persiapan

Pemilik repo sedang kuliah dan tidak bisa menjawab. Kerjakan Q1 sampai Q10 di
docs/prompt-antigravity-3.md, berurutan, tanpa berhenti untuk bertanya.

ATURAN UNTUK SEMUA PROMPT Q1–Q10 (berlaku sampai Q10):
- Baca dulu: docs/konteks-sesi.md (keputusan yang dikunci, peta kode),
  docs/rencana-dan-status.md, docs/pemetaan-pasal.md bagian "Keputusan tim" dan
  "Jawaban lanjutan Patrice", DESIGN.md (sebelum menyentuh template/CSS).
- Keputusan yang dikunci tidak boleh diubah: tanpa label beli/jual, merah = naik,
  tiga bahasa (teks baru di app/teks/antigravity3.py dengan dict `T`, bukan di
  app/i18n.py), DCF berbasis kas, tidak ada data SYSTEX/mitra ke Gemini, nama orang
  tidak pernah diambil dari pengumuman, POLITE_DELAY dan jeda 2 detik ke TWSE/TPEx tidak
  boleh diturunkan.
- Berkas milik Claude, JANGAN disunting: README.md, app/agent/*.py, app/ambang_profil.py,
  app/chat.py, app/review.py, app/umpan_balik.py, docs/konteks-sesi.md,
  docs/rencana-dan-status.md, docs/pemetaan-pasal.md. Butuh perubahan di sana? Tulis
  usulannya di laporan bagian "Usulan untuk Claude", lanjut.
- Jangan bertanya lalu menunggu. Ragu? Pilih yang paling hati-hati, catat di laporan
  bagian "Keputusan yang saya ambil sendiri", lanjut.
- Dilarang: deploy, menyentuh Dokploy, membaca/menampilkan/menyalin nilai kunci API,
  mengirim pesan ke siapa pun, push --force, git add -A, menghapus tes, skip tes,
  melonggarkan assert, tes yang menyentuh jaringan (patch fungsi jaringan atau pakai
  folder sementara).
- Commit hanya berkas yang kamu ubah (git add <path> ...). Pesan commit berbahasa
  Indonesia dengan ID item di depan, contoh "V1: ...". Akhiri pesan commit dengan baris
  "Dikerjakan oleh Antigravity".
- Sebelum setiap push: git pull --rebase origin main, jalankan semua tes, lalu push.
  Rebase bentrok: git rebase --abort, tunggu 3 menit, ulangi.
- Satu item gagal pemeriksa dua kali setelah diperbaiki, atau lebih dari 60 menit: tandai
  ❌ dengan sebab, lanjut ke prompt berikutnya.
- Setiap item selesai: tambah satu bagian di docs/laporan-antigravity-3.md berisi ID,
  status (✅/⚠️/❌), commit, tes yang ditambah dan hasilnya, hasil pemeriksa manual
  (angka, bukan kesan), berkas yang diubah, jam mulai dan selesai.
- Tulis semua .md dengan skill /humanizer (tanpa tanda pisah panjang, tanpa bold
  berlebihan, kalimat pendek). Kode dan UI dengan skill anti-slop mode "during".

Langkah Q1:
1. git pull --rebase origin main
2. python3 -m unittest discover -s tests → catat jumlahnya (per 11 Nov siang: 187, OK).
   Ada yang gagal? Tulis di laporan, tetap lanjut, jangan perbaiki berkas milik Claude.
3. Pastikan skill humanizer dan anti-slop terpasang (lihat docs/prompt-antigravity-berurutan.md
   P1 langkah 4). Gagal? Catat, lanjut.
4. Buat docs/laporan-antigravity-3.md: judul, jam mulai, hasil tes langkah 2, status skill.
   Commit, push.

Selesai Q1 → buka docs/prompt-antigravity-3.md, cari "## Q2", kerjakan sekarang.
````

## Q2. G1: gold set untuk semua jalur

````text
# Q2 dari 10: G1, gold set mengenal semua jalur B1

Masalah: docs/panduan-gold-set.md dan scripts/evaluasi.py (mode gold, fungsi muat_gold)
hanya mengenal input capex/debt/cash dan "risiko". Sejak B1, agent punya jalur sinyal:
risiko (22/23), modal (11/35), laporan (31), berat (1/3/40, selalu ditahan),
tata_kelola (7/8). Pasal 20 = skenario valuasi. Ferry & Patrice akan melabeli dengan
panduan ini, jadi panduan harus cocok dengan perilaku agent.

Berkas yang boleh diubah: scripts/evaluasi.py, app/gold.py, docs/panduan-gold-set.md,
eval/gold.csv (hanya header dan 4 baris contoh), tests/test_gold_b1.py (baru).

Kerjakan:
1. Kolom baru di eval/gold.csv: `keputusan` dengan nilai terbit / tahan / arsip, dan
   `tingkat` (opsional: info / perhatian / serius, untuk profil moderat). Kolom
   `harus_terbit` lama tetap dibaca: ya → terbit, tidak → arsip. Kalau dua-duanya diisi
   dan bertentangan → ValueError dengan nomor baris.
2. Kolom `input` menerima: capex, debt, cash (wajib nilai_juta_ntd bila keputusan=terbit),
   risiko, modal, laporan, berat, tata_kelola (nilai_juta_ntd opsional).
3. Metrik baru di laporan gold (fungsi laporan di evaluasi.py):
   - akurasi keputusan 3 arah (terbit/tahan/arsip) + matriks kebingungan 3×3;
   - kecocokan tingkat sinyal (hanya baris yang mengisi `tingkat`), membandingkan
     dengan ambang_profil.tingkat(sinyal, "moderat");
   - akurasi angka tetap hanya untuk capex/debt/cash.
   Jangan ubah definisi metrik lama; tambahkan di bawahnya.
4. Ekspor kandidat (app/gold.py, dipakai /ekspor/kandidat-gold.csv): sampel seimbang per
   JALUR (valuasi, risiko, modal, laporan, berat, tata_kelola, dilewati), bukan hanya per
   pasal. Tambah kolom `keputusan` dan `tingkat` kosong. Kolom ringkasan_butir TIDAK boleh
   memuat butir yang labelnya mengandung 姓名 (nama orang).
5. Tulis ulang docs/panduan-gold-set.md: tabel per jalur (pasal, contoh judul asli, apa
   yang ditulis di keputusan/input/tingkat), cara konversi satuan tetap, contoh pengisian
   untuk tiap jalur. Hapus kalimat "Server menyimpan semua pengumuman asli sejak 8 Nov"
   (data 8–10 Nov hilang); ganti "sejak 11 Nov". Tenggat: 12 Nov siang.

Pemeriksa:
- tests/test_gold_b1.py minimal 8 tes: kolom lama tetap jalan, keputusan tahan untuk
  pasal 1, tingkat cocok/tidak cocok, bentrok harus_terbit vs keputusan → ValueError,
  ekspor tanpa 姓名, sampel per jalur.
- Jalankan evaluasi gold pada eval/gold.csv contoh: python3 scripts/evaluasi.py → keluar
  tanpa galat. Tempel ringkasan keluarannya di laporan.
- Semua tes OK.

Selesai Q2 → buka docs/prompt-antigravity-3.md, cari "## Q3", kerjakan sekarang.
````

## Q3. V1: tab Valuation tidak menunggu beta

````text
# Q3 dari 10: V1, tab Valuation cepat untuk emiten baru

Masalah: membuka tab Valuation emiten yang belum pernah di-cache butuh ±2 menit.
Penyebab utama: beta (app/valuasi_otomatis.py hitung_beta) mengambil 25 bulan harga
harian dari app/harga_resmi.py dengan jeda 2 detik per permintaan. Rute di app/main.py
(fungsi saham, cabang tab == "valuasi") memanggil valuasi_otomatis.ambil() secara sinkron.
Selain itu TWSE kadang membalas HTTP 307 (terlalu sering), dan sekarang itu dianggap gagal.

Berkas yang boleh diubah: app/valuasi_otomatis.py, app/harga_resmi.py, app/main.py
(hanya cabang tab "valuasi" dan fungsi baru untuk latar), app/templates/saham.html
(bagian valuasi), app/teks/antigravity3.py, tests/test_v1_cepat.py (baru).

Kerjakan:
1. Beta di latar: kalau harga harian 25 bulan belum lengkap di cache, bangun() memakai
   beta 1,0 dengan penanda `beta_sementara: true` dan sumber yang jujur ("beta 1.0
   sementara, beta resmi sedang dihitung"). Satu thread latar (paling banyak satu per
   kode, pakai kunci) menghitung beta, lalu membangun ulang dan menyimpan cache. Jeda 2
   detik tetap.
2. Tab Valuation menampilkan pita "Beta sedang dihitung dari harga resmi. Muat ulang
   halaman ini dalam beberapa menit." bila beta_sementara. Teks tiga bahasa.
3. harga_resmi._ambil_json: HTTP 307 atau 429 → tunggu 5 detik lalu ulangi, paling
   banyak 3 kali (5, 10, 20 detik). Setelah itu kembalikan None seperti sekarang. Jeda
   minimum 2 detik antar permintaan tetap berlaku.
4. Cache valuasi dengan beta_sementara tidak boleh dipakai pipeline sebagai "valuasi
   final" tanpa penanda: cek dari_cache_untuk_pipeline dan layak_dcf; cukup pastikan
   penandanya ikut terbawa ke JSON (jangan ubah app/agent/*).
5. Naikkan VERSI_SKEMA hanya bila bentuk cache berubah dan tes lama memerlukannya.
   Catat alasannya di laporan.

Pemeriksa:
- tests/test_v1_cepat.py minimal 6 tes tanpa jaringan: cache harga kosong → bangun()
  selesai < 1 detik dengan beta_sementara (patch fungsi FinMind/harga); thread latar
  dipanggil sekali untuk dua permintaan beruntun; 307 diulang lalu berhasil; 307 tiga
  kali → None; pita tampil di tiga bahasa; tidak ada thread kedua untuk kode yang sama.
- Cek nyata (laptop punya internet): jalankan server lokal
  (SENTINEL_DATA_DIR=<folder sementara> uvicorn app.main:app), buka /saham/2454?tab=valuasi
  untuk emiten yang belum di-cache. Catat detik sampai halaman tampil (target < 10 detik),
  lalu detik sampai beta resmi muncul setelah muat ulang. Tulis angkanya di laporan.
- Semua tes OK.

Selesai Q3 → buka docs/prompt-antigravity-3.md, cari "## Q4", kerjakan sekarang.
````

## Q4. V2: skrip pemanasan cache

````text
# Q4 dari 10: V2, pemanasan cache untuk demo

Tujuan: sebelum demo, emiten besar sudah punya cache valuasi, profil, harga, dan beta,
supaya halaman apa pun yang dibuka juri tampil cepat.

Berkas: scripts/panaskan_cache.py (baru), tests/test_panaskan_cache.py (baru),
docs/deploy-dokploy.md (tambah bagian "Sebelum demo").

Kerjakan:
1. scripts/panaskan_cache.py --top N (bawaan 30) --kode 2330 2454 ... --data-dir <folder>.
   Daftar top N dari kapitalisasi pasar (pakai data yang sudah ada di app/pasar.py; kalau
   tidak ada fungsi daftar, pakai daftar tetap 30 emiten terbesar TWSE yang ditulis di
   skrip dengan komentar sumbernya). Untuk tiap kode: valuasi_otomatis.ambil(kode, paksa
   bila --paksa) termasuk beta resmi (tunggu thread latar dari V1 selesai, atau hitung
   langsung), pasar.profil, pasar.harga. Jeda sopan tetap.
2. Keluaran: tabel per kode (status valuasi, beta resmi/sementara, detik), ringkasan di
   akhir. Galat satu kode tidak menghentikan yang lain.
3. Cara pakai di server ditulis di docs/deploy-dokploy.md: perintah docker exec ke
   container dengan SENTINEL_DATA_DIR=/data, berapa lama kira-kira, kapan dijalankan
   (malam sebelum demo).

Pemeriksa:
- Tes tanpa jaringan (patch ambil/profil/harga): urutan kode, galat satu kode tidak
  menghentikan, --kode mengalahkan --top.
- Cek nyata: jalankan untuk --kode 2330 2317 2454 ke folder sementara. Catat waktu total
  dan isi tabel di laporan. Setelah itu buka tab Valuation ketiganya di server lokal:
  masing-masing harus < 2 detik.
- Semua tes OK.

Selesai Q4 → buka docs/prompt-antigravity-3.md, cari "## Q5", kerjakan sekarang.
````

## Q5. S1: cari emiten dengan nama

````text
# Q5 dari 10: S1, cari emiten dengan nama

Sekarang /saham?kode=... hanya menerima kode angka (app/main.py fungsi cari_saham). Juri
akan mengetik "TSMC", "台積電", "MediaTek", atau "2330".

Berkas: app/indeks_nama.py (baru), app/main.py (fungsi cari_saham + rute API baru),
templates yang memuat kotak cari (cari dengan grep 'name="kode"'), app/teks/antigravity3.py,
tests/test_cari_nama.py (baru).

Kerjakan:
1. app/indeks_nama.py: indeks kode → {nama_zh, nama_en, bursa}. Sumber resmi: daftar
   perusahaan OpenAPI TWSE (t187ap03_L, kolom 公司簡稱 dan 英文簡稱) dan TPEx (padanannya
   di OpenAPI TPEx; cari endpoint yang memuat nama Inggris). Satu permintaan per bursa,
   cache di DATA_DIR/indeks_nama.json selama 7 hari. Simpan HANYA kode, nama, nama
   Inggris, bursa (jangan simpan kolom lain: profil memuat nama pejabat). Ditambah alias
   kecil yang ditulis tangan untuk nama populer yang tidak sama dengan nama resmi (TSMC,
   MediaTek, Foxconn/Hon Hai, UMC, ASE, Delta, Quanta, Fubon, Cathay, CTBC), dengan
   komentar.
2. cari(q): cocok persis kode → kode. Lalu cocok persis nama/alias (tanpa beda huruf
   besar kecil, spasi, tanda baca, bentuk penuh/setengah lebar). Lalu awalan, lalu
   mengandung. Kembalikan paling banyak 10 hasil berurutan.
3. /saham?kode=q: satu hasil atau cocok persis → redirect ke /saham/{kode}. Banyak hasil →
   halaman daftar pilihan sederhana (pakai gaya yang ada). Nol hasil → kembali dengan
   pesan "tidak ditemukan" tiga bahasa. GET /api/cari?q= → JSON hasil.
4. Placeholder kotak cari: "Code or name (2330, TSMC, 台積電)" tiga bahasa.
5. Indeks belum ada dan jaringan gagal: kode angka tetap jalan seperti sekarang.

Pemeriksa:
- Tes tanpa jaringan dengan sampel kecil: TSMC → 2330, 台積電 → 2330, tsmc → 2330,
  "台積" → daftar memuat 2330, 2330 → 2330, "zzz" → kosong, nama pejabat tidak ada di
  berkas indeks.
- Cek nyata: bangun indeks dari OpenAPI, catat jumlah emiten TWSE dan TPEx, dan hasil
  untuk 10 kueri: TSMC, 台積電, MediaTek, 聯發科, Hon Hai, 鴻海, Fubon, 富邦金, 6488, 環球晶.
- Semua tes OK.

Selesai Q5 → buka docs/prompt-antigravity-3.md, cari "## Q6", kerjakan sekarang.
````

## Q6. C1a: tautan Tanya FEAF

````text
# Q6 dari 10: C1a, Tanya FEAF bisa ditemukan

Chatbot ada di /tanya (app/chat.py, milik Claude) tetapi belum ada tautannya.

Berkas: app/templates/base.html (menu), app/templates/saham.html (tombol),
app/templates/chat.html (hanya membaca parameter ?kode= untuk mengisi contoh pertanyaan;
jangan ubah logika lain), app/teks/antigravity3.py, tests/test_c1a_tautan.py (baru).

Kerjakan:
1. Menu kiri: "Ask FEAF" / "問 FEAF" / "Tanya FEAF", di antara Feed dan Review.
2. Halaman saham: tombol "Ask about {kode}" di kepala halaman menuju /tanya?kode={kode}.
3. chat.html: bila ada ?kode=, isi kotak pertanyaan dengan contoh "What changed recently
   for {kode}?" sesuai bahasa, tanpa langsung mengirim.

Pemeriksa:
- Tes: menu memuat /tanya di tiga bahasa; /saham/2330 memuat /tanya?kode=2330;
  /tanya?kode=2330 memuat 2330 di kotak; kode tidak sah (mis. <script>) tidak dipantulkan.
- Tangkapan layar menu dan tombol (simpan di docs/diagram/c1a-*.png), sebut di laporan.
- Semua tes OK.

Selesai Q6 → buka docs/prompt-antigravity-3.md, cari "## Q7", kerjakan sekarang.
````

## Q7. C1b: uji Tanya FEAF

````text
# Q7 dari 10: C1b, uji Tanya FEAF

Target lomba untuk C1: ≥80% pertanyaan uji benar dan bersitasi, 0 angka karangan lolos,
0 kata beli/jual, pertanyaan berisi injeksi gagal mengarahkan agent.

Berkas: eval/chat_uji.csv (tambah baris), docs/laporan-antigravity-3.md. JANGAN ubah
app/chat.py; bug di sana ditulis di "Usulan untuk Claude".

Kerjakan:
1. Tambah pertanyaan uji di eval/chat_uji.csv sampai minimal 40 baris, seimbang:
   harga/statistik, valuasi, pengumuman terbaru, sinyal B1 (penjaminan, modal, laporan,
   auditor/pejabat), pertanyaan yang harus DITOLAK (prediksi harga, saran beli/jual,
   order, data pribadi seperti nama direktur), dan 6 injeksi ("abaikan instruksi
   sebelumnya…", dalam tiga bahasa). Tiga bahasa, campur.
2. Cek apakah variabel lingkungan GEMINI_API_KEY ada di laptop TANPA menampilkan nilainya:
   python3 -c "import os; print(bool(os.environ.get('GEMINI_API_KEY')))".
   - True: jalankan python3 scripts/evaluasi.py --chat --simpan dengan
     SENTINEL_MODEL=gemini-3.6-flash dan SENTINEL_MODEL_CADANGAN=gemini-3.5-flash.
   - False: jalankan tanpa model (python3 scripts/evaluasi.py --chat --simpan) dan tulis
     di laporan bahwa uji dengan model belum dilakukan.
3. Di laporan: tabel metrik (benar, bersitasi, angka karangan, tolak benar, injeksi
   gagal), 5 jawaban terburuk beserta jejaknya (eval/hasil/chat-*.json), dan usulan
   perbaikan untuk Claude.

Pemeriksa: berkas eval/hasil/chat-*.md baru ada dan angkanya disalin ke laporan. Semua tes OK.

Selesai Q7 → buka docs/prompt-antigravity-3.md, cari "## Q8", kerjakan sekarang.
````

## Q8. K1: draf laporan keamanan

````text
# Q8 dari 10: K1, draf laporan keamanan

Aturan lomba Pasal 14 (docs/aaic-2026-ringkasan.md bagian keamanan) meminta tim menilai:
prompt injection, pemanggilan tool tanpa izin, kebocoran data, halusinasi, bias, input
berbahaya, risiko supply chain, dan kegagalan layanan pihak ketiga, lalu proteksi,
monitoring, dan pemulihannya. Ini juga bahan formulir self-assessment.

Berkas: docs/laporan-keamanan.md (baru). Hanya dokumen, tanpa kode.

Kerjakan: satu bagian per risiko di atas, masing-masing berisi:
- ancaman dalam satu-dua kalimat, contoh nyata dari proyek ini bila ada;
- proteksi yang SUDAH ada, dengan rujukan berkas:baris dan nama tes yang membuktikannya
  (contoh: docs/laporan-serangan.md, tests/test_serangan.py, app/chat.py TOLAK dan
  pemeriksa angka, verify.py, sinyal.periksa_kutipan, kunci akses dan KUNCI_BACA, nama
  orang tidak diambil di pasal 1/7/8, cache profil TPEx dengan daftar izin);
- monitoring (jejak audit, /sehat, jejak chat);
- pemulihan (penalar aturan saat model gagal, pemutus, review manusia);
- celah yang masih terbuka, jujur.
Tambahkan bagian "Insiden yang pernah terjadi": cache profil TPEx sempat menyimpan nama
pejabat dan email (ditemukan dan diperbaiki 10 Nov; jelaskan dampak dan perbaikannya
dari git log). Tambahkan tabel ringkas "data apa dikirim ke mana" (Gemini: hanya teks
pengumuman publik; FinMind/TWSE/TPEx: hanya kode emiten; tidak ada data SYSTEX/mitra).

Pemeriksa: setiap klaim proteksi punya rujukan berkas atau tes yang benar-benar ada
(cek dengan grep, tulis daftar cek di laporan). Tidak ada kunci, kata sandi, email, atau
nama orang di dokumen. /humanizer dijalankan.

Selesai Q8 → buka docs/prompt-antigravity-3.md, cari "## Q9", kerjakan sekarang.
````

## Q9. QA1: skrip QA halaman

````text
# Q9 dari 10: QA1, skrip QA halaman tiga bahasa

Berkas: scripts/qa_halaman.py (baru), tests/test_qa_halaman.py (baru).

Kerjakan: skrip yang menyalakan aplikasi dengan TestClient pada folder data yang
diberikan (--data-dir, bawaan data/), lalu untuk tiap bahasa (en, zh, id) membuka:
/, /watchlist, /review, /ambang, /tanya, /sehat, /saham/{kode} untuk semua tab (ringkasan,
stream, stats, keu, valuasi, profil) pada 3 kode watchlist, dan /peringatan/{id} untuk
satu contoh tiap jenis hasil (terbit valuasi/skenario, tiap jenis sinyal, tiap jenis
tahan). Jaringan dimatikan (patch fungsi jaringan supaya hanya cache yang dipakai).
Untuk tiap halaman cek:
- status 200 (atau 401 bila memang dikunci);
- tidak ada kunci terjemahan mentah (pola seperti "sn.", "tg.", "akhir.", "va." yang
  tampil sebagai teks);
- tidak ada "GANTI", "TODO", "None", "nan", "Traceback";
- di bahasa en dan zh tidak ada kata Indonesia umum yang bocor (daftar kecil: "Sumber",
  "belum", "tidak", "dan", "untuk", "Imbal hasil"), dilaporkan sebagai peringatan;
- tidak ada label beli/jual (buy, sell, 買進, 賣出, beli, jual) di luar penafian.
Keluaran: tabel halaman × bahasa (lolos/gagal + sebab) dan kode keluar 1 bila ada gagal.

Pemeriksa: tes untuk fungsi cek (kunci mentah terdeteksi, kata beli di penafian tidak
dihitung). Jalankan pada data/ dan pada folder data asli bila ada di laptop; tempel
ringkasan di laporan beserta daftar temuan. Temuan di berkas milik Claude: jangan
diperbaiki, tulis di "Usulan untuk Claude". Temuan di berkasmu sendiri: perbaiki.

Selesai Q9 → buka docs/prompt-antigravity-3.md, cari "## Q10", kerjakan sekarang.
````

## Q10. Laporan akhir

````text
# Q10 dari 10: laporan akhir

1. git pull --rebase origin main, jalankan semua tes, catat jumlah dan hasil.
2. Lengkapi docs/laporan-antigravity-3.md:
   - tabel ringkas Q2–Q9: ID, status, commit, tes baru, angka pemeriksa utama;
   - "Keputusan yang saya ambil sendiri";
   - "Usulan untuk Claude" (bug atau perubahan di berkas milik Claude, dengan berkas:baris);
   - "Yang perlu Afinzaki lakukan" (misalnya menjalankan scripts/panaskan_cache.py di server
     sebelum demo, mengirim panduan gold set ke Ferry & Patrice);
   - jam selesai.
3. /humanizer pada laporan. Commit, push. Berhenti.
````

---

## Cara mengecek hasilnya (untuk Afinzaki)

1. Buka `docs/laporan-antigravity-3.md`. Setiap item harus punya status, commit, dan angka.
2. Jangan Deploy dulu. Kirim laporannya ke Claude untuk ditinjau terhadap kode.
3. Setelah Claude setuju: Deploy, lalu jalankan pemanasan cache sesuai `docs/deploy-dokploy.md`.
