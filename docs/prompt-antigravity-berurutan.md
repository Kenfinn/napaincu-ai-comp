# Prompt Antigravity berurutan (P1–P10), dijalankan setelah prompt baca dokumen

Untuk Afinzaki. Prompt baca dokumen sudah dijalankan. Berkas ini berisi satu prompt per
task. Setiap prompt di akhirnya menyuruh Antigravity membuka prompt berikutnya di berkas
ini dan langsung mengerjakannya, jadi cukup tempel **P1** sebelum tidur. Kalau rantainya
berhenti di tengah, tempel prompt nomor berikutnya secara manual.

Berkas ini menggantikan `prompt-antigravity-malam.md` (yang menggabungkan baca dokumen dan
putaran 2 dalam satu prompt).

Sebelum tidur:
1. Laptop dicolok ke listrik, sleep dimatikan, Wi-Fi tersambung.
2. Di setelan Antigravity, izinkan menjalankan perintah terminal dan menyunting berkas
   tanpa persetujuan (auto-execute / always proceed). Tanpa ini agent berhenti di perintah
   pertama.
3. Buka satu agent di workspace repo ini, tempel P1.

Pagi hari: buka `docs/laporan-antigravity-2.md` dan kirim ke Claude.

---

## P1. Persiapan

````text
# P1 dari 10: persiapan kerja semalam

Pemilik repo tidur sampai pagi dan tidak bisa menjawab. Kamu mengerjakan P1 sampai P10 di
docs/prompt-antigravity-berurutan.md, berurutan, tanpa berhenti untuk bertanya.

ATURAN UNTUK SEMUA PROMPT P1–P10 (baca sekali, berlaku sampai P10):
- Ikuti docs/prompt-antigravity-2.md bagian 0, 1, dan 2 (aturan kerja dan kepemilikan
  berkas). Spesifikasi rinci tiap item ada di bagian 3 berkas itu.
- Claude bekerja di repo yang sama malam ini dan push ke main. Berkas milik Claude, jangan
  disentuh: app/chat.py, app/templates/chat.html, tests/test_chat.py, scripts/evaluasi.py,
  docs/diagram*, README.md, dan baris include_router di akhir app/main.py.
- Jangan bertanya lalu menunggu. Ragu? Pilih yang paling hati-hati (tidak menerbitkan,
  tidak menghapus, tidak mengubah keputusan tim), catat di laporan bagian "Keputusan yang
  saya ambil sendiri", lanjut.
- Dilarang: deploy, menyentuh Dokploy, membaca atau mengubah kunci API, mengirim pesan ke
  siapa pun, push --force, git add -A, menghapus tes, skip tes, melonggarkan assert.
- Commit hanya berkas yang kamu ubah: git add <path> ...
- Sebelum setiap push: git pull --rebase origin main, jalankan semua tes, lalu push.
  Rebase bentrok di berkas milik Claude: git rebase --abort, tunggu 3 menit, ulangi.
- Tes gagal di berkas milik Claude: catat, jangan diperbaiki, lanjut.
- Satu item gagal pemeriksa dua kali setelah diperbaiki, atau lebih dari 90 menit: tandai ❌
  dengan sebab, lanjut ke prompt berikutnya.
- Setiap item yang selesai, tambahkan satu bagian ke docs/laporan-antigravity-2.md
  (buat berkasnya bila belum ada) dengan isi: ID, status, commit, tes yang ditambah dan
  hasilnya, angka QA manual, berkas yang diubah, jam mulai dan selesai. Bagian akhir
  laporan ditulis di P10.
- Tulis semua .md dengan skill /humanizer.

Langkah P1:
1. git pull --rebase origin main
2. python3 -m unittest discover -s tests → catat jumlah dan hasil (harus OK).
3. Pastikan docs/pemahaman-antigravity.md ada (hasil prompt baca dokumen), lalu baca bagian
   "E. Koreksi dari Claude" di berkas itu. Koreksi itu mengalahkan jawabanmu sebelumnya.
4. Pasang skill: anti-slop (`agy plugin install https://github.com/miqdadbadjuber/anti-slop`,
   mode "during") dan humanizer (`npx skills add blader/humanizer`, atau salin SKILL.md
   dari https://github.com/blader/humanizer ke folder skill). Gagal? Catat, lanjut tanpa.
5. Buat docs/laporan-antigravity-2.md dengan judul, jam mulai, hasil tes langkah 2, dan
   status pemasangan skill. Commit, push.

Selesai P1 → buka docs/prompt-antigravity-berurutan.md, cari "## P2", kerjakan sekarang.
````

## P2. R1: beta dari harga resmi

````text
# P2 dari 10: R1 beta dari harga harian resmi TWSE/TPEx

Kerjakan item R1 persis sesuai docs/prompt-antigravity-2.md bagian 3 "R1". Aturan dari P1
berlaku.

Ringkasan yang wajib terpenuhi:
- app/harga_resmi.py baru: harian(kode, bursa, bulan), taiex(bulan), cache per bulan
  (bulan lalu permanen, bulan berjalan 12 jam), jeda 2 detik antar-permintaan jaringan.
- Beta di app/valuasi_otomatis.py dari return mingguan 2 tahun vs TAIEX; < 52 minggu →
  1,0 dan beta_cadangan true. Semua pemakaian Yahoo dihapus.
- Sampel tests/data/harga_resmi_sampel.json.
Pemeriksa (semua wajib lulus): test_r1_urai_twse_tpex_taiex, test_r1_beta_dari_deret_buatan,
test_r1_beta_cadangan_bila_kurang_52_minggu, test_r1_cache_bulan_lalu_tidak_diambil_ulang,
test_r1_tanpa_yahoo; semua tes lama lulus; QA: `python3 scripts/valuasi_otomatis.py 2330
--banding` beta bukan cadangan dengan ≥ 100 minggu, dan 6488 bukan cadangan.
Catat nilai beta 2330, jumlah minggu, dan beta 6488 di laporan.
Commit "R1: beta dari harga resmi TWSE/TPEx", push, tambahkan bagian R1 di laporan.

Selesai P2 → kerjakan "## P3" di berkas ini sekarang.
````

## P3. R2: penafian

````text
# P3 dari 10: R2 penafian di semua halaman analisis

Kerjakan item R2 persis sesuai docs/prompt-antigravity-2.md bagian 3 "R2". Aturan P1 berlaku.

Ringkasan: buat app/templates/_penafian.html; sertakan di saham.html (semua tab, satu
kali, hapus yang lama di tab Ringkasan), peringatan.html, valuasi.html, feed.html; ganti
teks rk.p.hati dan rk.p.aman di app/i18n.py dengan teks persis yang ada di spesifikasi.
Pemeriksa: test_r2_penafian_di_semua_halaman_analisis (tiga bahasa, tepat satu kali,
tanpa "⟦"), test_r2_tanpa_kata_kesesuaian; semua tes lama lulus; QA: buka /saham/2330
tiap tab di tiga bahasa, pastikan penafian tampil sekali.
Commit "R2: penafian di semua halaman analisis", push, bagian R2 di laporan.

Selesai P3 → kerjakan "## P4" sekarang.
````

## P4. R3: kunci baca

````text
# P4 dari 10: R3 kunci akses untuk halaman baca

Kerjakan item R3 persis sesuai docs/prompt-antigravity-2.md bagian 3 "R3". Aturan P1 berlaku.

Ringkasan: config.KUNCI_BACA dari SENTINEL_KUNCI_BACA (bawaan mati, hanya aktif bila
KODE_AKSES terisi); middleware di app/main.py; halaman app/templates/kunci.html (401);
jalur terbuka: /akses, /sehat, /static/*, /bahasa/*, /api/impor; /api/* lain → JSON 401;
/akses berhasil → ke "/"; catatan di docs/deploy-dokploy.md.
Pemeriksa: test_r3_mati_secara_bawaan, test_r3_terkunci_tanpa_kode,
test_r3_terbuka_dengan_kode, test_r3_abaikan_bila_kode_kosong,
test_r3_halaman_kunci_tiga_bahasa; semua tes lama lulus (terutama TestDeploy dan
TestStateDanReview yang memakai /akses); QA: jalankan server dengan
SENTINEL_KUNCI_BACA=1 SENTINEL_KODE_AKSES=uji, cek / (401), /sehat (200),
/akses?kode=uji lalu / (200).
Commit "R3: kunci akses halaman baca", push, bagian R3 di laporan.

Selesai P4 → kerjakan "## P5" sekarang.
````

## P5. D-a: semua emiten

````text
# P5 dari 10: D-a proses pengumuman semua emiten

Kerjakan item D-a persis sesuai docs/prompt-antigravity-2.md bagian 3 "D-a". Aturan P1
berlaku. Ini item paling berisiko; baca app/main.py fungsi hasil(), app/tarik.py
periksa_sekarang(), dan app/agent/llm.py tanya() sebelum mengubah.

Ringkasan: config PROSES_SEMUA (bawaan 1) dan MODEL_MAKS_PER_JALAN (bawaan 40);
periksa_sekarang() tanpa argumen menyimpan semua emiten, dengan argumen eksplisit tetap
hanya watchlist; scripts/impor_arsip.py; llm.mulai_jalan(maks) + pengecekan jatah di
tanya() (cache tidak mengurangi jatah, bawaan tanpa batas); hasil(segarkan=True) dihitung
di luar _kunci_cache dengan lock terpisah; feed dan review: bawaan watchlist,
?lingkup=semua untuk semua (feed dibatasi 300 terbaru).
Pemeriksa: test_da_semua_emiten_disimpan, test_da_argumen_eksplisit_tetap_watchlist,
test_da_jatah_model, test_da_halaman_lingkup; TestPenarikDinamis lama lulus TANPA diubah;
semua tes lama lulus; QA: python3 scripts/impor_arsip.py lalu jalankan server, catat
jumlah pengumuman, jumlah per state, dan detik satu kali proses ulang.
Commit "D-a: proses pengumuman semua emiten", push, bagian D-a di laporan.

Selesai P5 → kerjakan "## P6" sekarang.
````

## P6. D-c: utang lancar

````text
# P6 dari 10: D-c utang jangka panjang yang jatuh tempo setahun

Kerjakan item D-c persis sesuai docs/prompt-antigravity-2.md bagian 3 "D-c". Aturan P1
berlaku.

Ringkasan: field neraca short_term_borrowings dari ShorttermBorrowings FinMind (0 bila
tidak ada); ubah SATU baris net_debt di scripts/dcf.py menjadi
`debt = bs["current_portion_lt_debt"] + bs["long_term_debt"] + bs.get("short_term_borrowings", 0.0)`;
current_portion_lt_debt yang tidak tersedia ditandai di "tidak_tersedia" dengan peringatan
tiga bahasa di tab Valuation; paragraf penjelasan di docs/valuasi-otomatis.md.
Pemeriksa: test_dc_pinjaman_jangka_pendek_masuk_utang, test_dc_tanda_tidak_tersedia;
TestParitasKalkulator lama lulus (berkas manual tanpa field baru = angka sama); semua tes
lama lulus. (test_dc_manual_mengisi_yang_kosong dikerjakan di P7 setelah D-b.)
Commit "D-c: pinjaman jangka pendek dan tanda utang lancar", push, bagian D-c di laporan.

Selesai P6 → kerjakan "## P7" sekarang.
````

## P7. D-b: 2330 otomatis

````text
# P7 dari 10: D-b 2330 memakai valuasi otomatis, berkas manual hanya asumsi

Kerjakan item D-b persis sesuai docs/prompt-antigravity-2.md bagian 3 "D-b", lalu tes
test_dc_manual_mengisi_yang_kosong dari D-c. Aturan P1 berlaku.

Ringkasan: store.muat_valuasi: cache otomatis layak + berkas manual → data otomatis,
ditimpa hanya assumptions, risk_free_rate, equity_risk_premium, dan field yang
"tidak_tersedia"; tandai asumsi_dari dan ditimpa_manual; tanpa cache → berkas manual apa
adanya. Lencana di tab Valuation dan /valuasi/{kode}. Teks sources.cash_flow 2330.json
diperjujur (angka tidak diubah). Blok setUpModule/tearDownModule "# D-b (Antigravity)" di
awal tests/test_agent.py yang mengarahkan cache valuasi otomatis ke folder sementara;
itu satu-satunya perubahan di berkas itu.
Pemeriksa: test_db_otomatis_menang_asumsi_manual, test_db_tanpa_cache_pakai_manual,
test_dc_manual_mengisi_yang_kosong (utang total 2330 selisih < 1% dari manual); semua tes
lama lulus; QA: /saham/2330?tab=valuasi tiga bahasa; catat WACC dan g tersirat 2330
sebelum dan sesudah D-b, dan tempel tabel `python3 scripts/valuasi_otomatis.py 2330
--banding` di laporan.
Commit "D-b: 2330 memakai valuasi otomatis dengan asumsi tim", push, bagian D-b (dan
lengkapi D-c) di laporan.

Selesai P7 → kerjakan "## P8" sekarang.
````

## P8. B3: sitasi MOPS

````text
# P8 dari 10: B3 sitasi MOPS untuk angka laporan keuangan

Kerjakan item B3 persis sesuai docs/prompt-antigravity-2.md bagian 3 "B3". Aturan P1
berlaku.

Ringkasan: fungsi mops_laporan(kode, tahun_iso, kuartal, jenis) di app/sitasi.py (neraca
t164sb03, lr t164sb04, arus t164sb05; tahun ROC; season 01–04; URL mopsov ajax seperti
di spesifikasi + cadangan halaman pencarian); tautan "MOPS ↗" di setiap kolom periode tab
Financials; catatan sumber di bawah tabel; sources valuasi otomatis memuat URL MOPS;
scripts/cek_finmind_resmi.py membandingkan FinMind dengan OpenAPI resmi t187ap06_L_ci dan
t187ap07_L_ci (ingat t187ap06 kumulatif sejak awal tahun).
Pemeriksa: test_b3_url_mops, test_b3_tautan_di_tab_keuangan, test_b3_cek_resmi_kumulatif;
semua tes lama lulus; QA: `python3 scripts/cek_finmind_resmi.py --acak 10 --seed 7
--simpan`, minimal 10 angka dibandingkan, catat berapa yang selisih ≤ 0,5% dan jelaskan
sisanya; uji 3 tautan MOPS (2330 neraca 2025Q4, 2317 laba rugi 2026Q2, 6488 arus kas
2025Q4) bila laptop di jaringan Taiwan, kalau tidak tulis "belum diuji".
Commit "B3: sitasi MOPS dan cek FinMind vs sumber resmi", push, bagian B3 di laporan.

Selesai P8 → kerjakan "## P9" sekarang.
````

## P9. R4: pengungkapan pihak ketiga

````text
# P9 dari 10: R4 draf pengungkapan pihak ketiga dan alat AI

Kerjakan item R4 persis sesuai docs/prompt-antigravity-2.md bagian 3 "R4". Aturan P1
berlaku.

Ringkasan: docs/pengungkapan-pihak-ketiga.md (pakai /humanizer) dengan tabel Nama · Jenis ·
Untuk apa · Lingkup data · Lisensi/syarat (tautan + kutipan) · Diverifikasi?; isi minimal
seperti daftar di spesifikasi, ditambah situs harga resmi TWSE/TPEx dari R1 dan OpenAPI
t187ap06/07 dari B3; Yahoo ditulis "tidak dipakai lagi sejak R1"; bagian "Pembagian kerja
tim" berupa tabel KOSONG; bagian "Catatan data pribadi" (cache profil TPEx, commit e4572d6).
Jangan menebak lisensi: tidak ketemu → "belum diverifikasi".
Pemeriksa: test_r4_semua_pustaka_tercantum, test_r4_tabel_tim_kosong; semua tes lama lulus.
Commit "R4: draf pengungkapan pihak ketiga dan alat AI", push, bagian R4 di laporan.

Selesai P9 → kerjakan "## P10" sekarang.
````

## P10. Pemeriksaan akhir dan laporan

````text
# P10 dari 10: pemeriksaan akhir dan laporan

Aturan P1 berlaku.
1. Jalankan pemeriksaan akhir docs/prompt-antigravity-2.md bagian 4, semua langkahnya:
   tes penuh, tes dengan Wi-Fi mati, git grep kunci/data pribadi/yahoo, semua halaman di
   tiga bahasa, kunci baca. Catat hasil tiap langkah.
2. Lengkapi docs/laporan-antigravity-2.md sesuai bagian 5 berkas itu (urutan bagian 1–8),
   memakai bagian per item yang sudah kamu tulis di P2–P9, ditambah:
   - "Keputusan yang saya ambil sendiri" (apa, kenapa, berkas);
   - "Linimasa" (jam mulai dan selesai tiap prompt P1–P10).
   Jangan menulis "semua lulus" bila ada pemeriksa yang gagal atau dilewati.
3. Jalankan /humanizer pada laporan.
4. Perbarui baris status R1, R2, R3, D-a, D-b, D-c, B3, R4 di docs/rencana-dan-status.md.
5. git add docs/laporan-antigravity-2.md docs/rencana-dan-status.md, commit "Laporan
   putaran 2", git pull --rebase origin main, tes, push.
6. Berhenti. Jangan memulai pekerjaan lain.
````

---

## Pagi hari: cara mengecek

1. `git pull origin main`, lalu `python3 -m unittest discover -s tests`. Hasilnya harus OK,
   dengan jumlah tes lebih dari 131.
2. Buka `docs/laporan-antigravity-2.md`. Lihat tabel item dan bagian "Keputusan yang saya
   ambil sendiri".
3. Kalau rantai berhenti di tengah (laporan tidak punya bagian P10), lihat item terakhir
   di laporan, lalu tempel prompt nomor berikutnya.
4. Kirim laporan ke Claude sebelum deploy.
