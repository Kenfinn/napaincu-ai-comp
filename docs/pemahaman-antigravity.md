# Pemahaman Dokumentasi FEAF Sebelum Putaran 2

Dokumen ini mencatat pemahaman arsitektur, batasan lomba, peta kode, serta keselarasan dokumen sebelum memulai putaran 2. Ditulis dengan kalimat ringkas dan berdasar langsung pada isi repositori.

---

## A. Jawaban Pemahaman Inti

### 1. Apa yang dikerjakan FEAF, dan apa yang sengaja TIDAK dikerjakannya?
FEAF memantau pengumuman material emiten bursa Taiwan (TWSE/TPEx), mengekstrak data keuangan penting, memeriksa kebenarannya secara deterministik, menghitung ulang valuasi DCF, dan menyajikan peringatan terverifikasi untuk investor.
FEAF sengaja tidak memberikan rekomendasi beli atau jual serta tidak mengeksekusi order transaksi.
Saran otomatis di Taiwan wajib memiliki izin FSC, dan aturan lomba melarang tindakan berisiko tanpa otorisasi manusia.
*(Sumber: `docs/konteks-sesi.md` baris 15–17, 33; `docs/aaic-2026-ringkasan.md` baris 248; `DESIGN.md` baris 33)*

### 2. Sebutkan urutan state sebuah pengumuman dari ditarik sampai berakhir, dan tiga kemungkinan akhirnya.
Urutan status berjalan dari `FETCHED` (ditarik), `VALIDATED` (validasi bentuk butir), `SCREENED` (lolos filter pasal), `TRIAGED` (triase keyakinan vs ambang), `VALUED` (penghitungan ulang DCF), hingga `VERIFIED` (pemeriksaan pra dan pasca hitung).
Bila memerlukan verifikasi manusia, alur singgah di `HUMAN REVIEW`.
Tiga status akhirnya adalah `PUBLISHED` (diterbitkan), `HELD` (ditahan untuk diputuskan manusia), atau `ARCHIVED` (diarsipkan).
*(Sumber: `app/agent/pipeline.py` baris 31–41, 82–245; `docs/konteks-sesi.md` baris 34; `DESIGN.md` baris 28)*

### 3. Kapan pengumuman berakhir HELD, dan kasus HELD mana yang boleh disetujui manusia?
Pengumuman berstatus HELD saat gagal dalam pemeriksaan pemeriksa, skor triase jatuh di zona ragu, emiten belum memiliki model valuasi, atau pengumuman tidak memiliki angka terurai.
Manusia hanya boleh menyetujui kasus keraguan wajar, seperti mata uang asing tanpa kurs, besaran di luar pita wajar 0,2–3,0x, ketiadaan model valuasi, atau keyakinan rendah.
Kasus halusinasi angka atau kutipan karangan yang tidak ada di dokumen sumber haram disetujui dan wajib diarsipkan.
*(Sumber: `app/review.py` baris 25–48; `app/agent/pipeline.py` baris 234–240, 280–306; `docs/konteks-sesi.md` baris 35)*

### 4. Bagaimana skor triase dihitung, dan bagaimana 👍/👎 mengubah ambang?
Skor triase dihitung oleh kode dari skor dasar pasal (0,55 untuk pasal dikenal atau 0,45 tanpa pasal), bonus angka terkonversi (+0,10), dan rasio transaksi terhadap kapitalisasi pasar (+0,20 jika $\ge 2\%$, +0,10 jika $\ge 0,5\%$, $-0,05$ jika $\ge 0,05\%$, $-0,20$ jika $< 0,05\%$).
Setiap suara pengguna menggeser ambang per pasal dari nilai dasar 0,55.
Tombol 👎 menaikkan ambang sebesar $+0,05$ untuk meredam derau, sedangkan tombol 👍 menurunkannya sebesar $-0,02$, dalam rentang batas 0,40 hingga 0,90.
*(Sumber: `app/agent/triase.py` baris 14–29, 62–89; `app/umpan_balik.py` baris 7–13, 80–98)*

### 5. Kenapa angka valuasi dihitung oleh kode, bukan model? Di berkas mana?
Model bahasa rentan mengalami halusinasi dan tidak dapat diandalkan untuk perhitungan aritmetika finansial.
Penghitungan lewat kode memastikan auditabilitas, konsistensi matematis, dan transparansi skenario tanpa tebakan model.
Logika perhitungan berada di `scripts/dcf.py` (fungsi `compute`), `app/agent/recompute.py` (fungsi `hitung_ulang`), dan `app/valuasi_otomatis.py`.
*(Sumber: `docs/konteks-sesi.md` baris 68, 140; `docs/rencana-finalis.md` baris 77–79)*

### 6. Data apa yang asli dan dari mana sumbernya; apa yang masih perkiraan?
Data asli mencakup pengumuman resmi dari OpenAPI TWSE/TPEx, harga penutupan dan profil bursa, data keuangan kuartalan FinMind, serta harga harian historis bursa resmi untuk beta.
Data perkiraan mencakup arus kas tahun 2023–2024 pada berkas manual `valuation/inputs/2330.json`, asumsi batas pertumbuhan terminal (`terminal_growth_ceiling`), dan nilai beta cadangan 1,0 jika data mingguan kurang dari 52 pekan.
*(Sumber: `docs/konteks-sesi.md` baris 91–94; `docs/valuasi-otomatis.md` baris 45–60; `docs/prompt-antigravity-2.md` baris 268–270)*

### 7. Data apa saja yang dikirim ke Gemini? Apa yang tidak boleh dikirim?
Data yang dikirim hanya teks pengumuman publik (judul dan butir penjelasan) yang sudah dibersihkan, serta daftar input valuasi target untuk ekstraksi angka.
Data yang dilarang dikirim meliputi data pribadi pengurus (nama direksi, juru bicara, akuntan, nomor kontak), kunci API atau token, serta data rahasia milik mitra lomba (SYSTEX).
*(Sumber: `docs/konteks-sesi.md` baris 132, 141–142; `app/agent/llm.py` baris 78–105; `docs/prompt-antigravity-2.md` baris 48–49, 382–384)*

### 8. Aturan tiga bahasa: di mana teks baru ditulis, dan kenapa tidak di app/i18n.py?
Teks baru ditulis pada modul terpisah di `app/teks/<nama>.py` dengan struktur `T = {"kunci": ("English", "中文", "Indonesia")}`.
Modul tersebut dimuat otomatis oleh `_muat_tambahan()` di `app/i18n.py`.
Teks baru tidak ditulis langsung di `app/i18n.py` agar pekerjaan paralel antara Claude dan Antigravity tidak memicu konflik merge pada git.
*(Sumber: `app/i18n.py` baris 835–849; `app/teks/__init__.py` baris 1–7; `docs/prompt-antigravity-2.md` baris 52–57)*

### 9. Aturan git di repo ini (branch, commit, push, yang dilarang).
Semua pekerjaan berjalan langsung di branch `main` dengan commit kecil, sering, dan pesan berbahasa Indonesia yang jelas.
Sebelum setiap push, wajib menjalankan `git pull --rebase origin main` dan memastikan seluruh unit test lulus.
Hal yang dilarang meliputi membuat Pull Request (PR), menjalankan `git push --force`, melakukan rebase ulang commit publik, `git add -A` sembarangan saat multi-agen, serta membocorkan kunci rahasia atau data pribadi.
*(Sumber: `docs/konteks-sesi.md` baris 30, 145; `docs/prompt-antigravity-2.md` baris 38–48; `docs/prompt-antigravity-multiagen.md` baris 57–60)*

### 10. Lima keputusan tim yang tidak boleh kamu ubah tanpa bertanya.
1. Bekerja langsung di branch `main` tanpa membuat branch baru atau PR.
2. Wajib mendukung tiga bahasa (English bawaan, 繁體中文, Bahasa Indonesia) dengan placeholder yang identik.
3. Konvensi warna Taiwan: merah untuk kenaikan, hijau untuk penurunan.
4. Tidak menyertakan label rekomendasi beli atau jual dalam bentuk apa pun.
5. Persetujuan review manusia dibatasi hanya untuk kasus keraguan wajar (ragu); angka karangan atau halusinasi wajib diarsipkan.
*(Sumber: `docs/konteks-sesi.md` baris 28–42; `docs/rencana-dan-status.md` baris 127–133)*

---

## B. Daftar Hal yang Bertentangan

1. **Jumlah pengujian unit saat ini:**
   - `docs/rencana-dan-status.md` (baris 48), `docs/konteks-sesi.md` (baris 51), dan `docs/prompt-antigravity-2.md` (baris 34) menyebutkan total 107 tes.
   - Kode aktual di `main` kini memiliki **108 tes lulus** karena penambahan `test_muat_tambahan_teks` di `tests/test_agent.py` pada commit `6beb5f5`.

2. **Aturan penempatan kunci terjemahan baru:**
   - `docs/konteks-sesi.md` (baris 122–123) pada putaran 1 mengatur Antigravity menulis di awal `_T` dan Claude di akhir `_T`.
   - `docs/prompt-antigravity-2.md` (baris 53–57) dan `app/teks/__init__.py` memperbarui aturan ini: kunci baru tidak boleh lagi ditulis di `app/i18n.py`, melainkan harus di modul terpisah `app/teks/<nama>.py`.

3. **Batasan penyuntingan berkas pendukung:**
   - Aturan awal di putaran 1 melarang menyentuh `scripts/dcf.py` dan `app/agent/llm.py`.
   - `docs/prompt-antigravity-2.md` (baris 64–67) memberikan izin khusus untuk menyunting satu baris di `scripts/dcf.py` (menambahkan `short_term_borrowings` untuk item D-c) dan fungsi pembatasan jatah panggilan di `app/agent/llm.py` (untuk item D-a).

---

## C. Pertanyaan Sebelum Memulai Putaran 2

1. **Pola eksekusi agen:**
   Apakah putaran 2 akan dijalankan sebagai satu agen tunggal berurutan sesuai `docs/prompt-antigravity-2.md` (R1 $\rightarrow$ R2 $\rightarrow$ R3 $\rightarrow$ D-a $\rightarrow$ D-b $\rightarrow$ D-c $\rightarrow$ B3 $\rightarrow$ R4), atau dipecah menjadi tiga subagen independen (Agent DATA, Agent WEB, Agent QA) menggunakan `docs/prompt-antigravity-multiagen.md`?

2. **Pengambilan data historis bursa resmi (R1):**
   Endpoint historis TWSE dan TPEx menerapkan pembatasan frekuensi dan membutuhkan jeda minimal 2 detik per permintaan. Apakah saat pengujian QA manual diperbolehkan mengambil 25 bulan hanya untuk dua emiten uji (2330 dan 6488) agar tidak membebani jaringan atau terkena pemblokiran IP?

---

## D. Hasil Pemeriksaan Langkah 1

- **Perintah:** `git pull --rebase origin main && python3 -m unittest discover -s tests`
- **Jumlah tes:** 108 tes
- **Hasil:** OK (seluruh 108 tes lulus dalam 4,43 detik tanpa galat)
