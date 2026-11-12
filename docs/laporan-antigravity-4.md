# Laporan Antigravity putaran 4: overhaul UI/UX

Pelaksana: Antigravity. Mulai Kamis 12 Nov 2026, 21:11 (waktu Taiwan).
Spesifikasi: `docs/prompt-antigravity-4-ui.md` (U1–U8).

## U1. Kondisi awal

- `git pull`: sudah di `bea7b04`.
- `python3 -m unittest discover -s tests`: 246 tes, OK.
- `python3 scripts/qa_halaman.py`: 78/78 lolos. Dua peringatan bocor kata Indonesia di `/sehat` (en, zh).
- Foto layar "sebelum": 78 berkas di `docs/ui/sebelum/` (13 halaman × 3 bahasa × lebar 1440 dan 390).
  Diambil dengan Playwright memakai Chrome sistem (`channel="chrome"`), karena Chromium bawaan
  Playwright belum diunduh di laptop ini.

## Temuan awal

Dilihat dari foto layar, dari sudut pengguna awam yang baru pertama membuka aplikasi.

### Semua halaman (kerangka)

1. Di lebar 390 px aplikasi tidak bisa dipakai. Menu samping tetap 224 px, isi tinggal ±130 px,
   judul Tionghoa pecah satu huruf per baris, tabel terpotong.
2. Pita "data contoh" dan penafian makan dua blok kuning di atas setiap halaman. Pengguna harus
   melewati ±6 baris teks sebelum sampai ke isi.
3. Label kecil berhuruf kapital mono (`MOPS FILINGS · PROCESSED BY THE AGENT`, `REASONING ENGINE`)
   ada di mana-mana. Sulit dibaca dan tidak menambah arti.
4. Kotak status di menu memakai istilah mesin: "rule-based reasoner", "Data source: sample",
   "Last fetch: never". Di bahasa Indonesia tertulis "Sumber data: fixture".
5. Menu tidak dikelompokkan. Watchlist di atas Peringatan, padahal feed adalah halaman utama.

### Feed (`/`)

1. Angka ringkasan (2 · 1 · 1) tidak menjelaskan apa yang harus dilakukan. "Held for review"
   hanya angka bergaris bawah.
2. Kalimat "Why three numbers, not one" menjawab pertanyaan juri, bukan pertanyaan pengguna.
3. Baris tidak menyebut nama emiten, hanya kode. Lencana `PUBLISHED`, `SCENARIO`, dan delta
   `g 4.85% → 5.25%` berwarna merah yang mudah dikira harga naik.
4. Tidak ada filter jenis, tidak ada pengelompokan tanggal.
5. Baris ditahan tidak menunjukkan tindakan berikutnya.

### Detail peringatan (`/peringatan/<id>`)

1. Tidak ada satu kalimat "artinya untuk saya". Setelah judul langsung tabel sumber dan PII.
2. Triase (0.85 vs 0.55, komponen +0.55/+0.10/+0.20) muncul sebelum hasil. Istilah teknis.
3. Daftar 8 pemeriksaan selalu terbuka dan panjang. Ringkasannya hanya di judul.
4. Untuk kasus ditahan, sebabnya satu paragraf merah panjang yang menyambung empat cek dengan "—".
5. Tidak ada tombol aksi yang jelas (jejak, saham, antrean review) di satu tempat.

### Halaman saham (`/saham/2330`)

1. Kepala ramai: harga, tombol "Ask about", lencana watchlist, semuanya rata kanan berdesakan.
2. Tab tidak lengket. Di ponsel hanya satu tab yang terlihat dan tidak ada tanda bisa digeser.
3. Tab Financials di ponsel: tiga segmen terpotong, tabel tidak bisa dibaca.
4. Tab Valuation dibuka dengan lencana `AUTOMATIC + TEAM ASSUMPTIONS` dan daftar nama field
   (`wacc_inputs.risk_free_rate`). Istilah WACC, g tersirat tanpa penjelasan.
5. Keadaan "beta sedang dihitung" ditulis di tiga tempat sekaligus.

### Review (`/review`)

1. Tombol "Archive" kecil merah, tombol setujui besar. Konsekuensi tiap tombol tidak dijelaskan.
2. Sebab penahanan satu kalimat panjang; nama jenis sebab tampil seperti kode (mono, rata kanan).
3. Tidak ada filter jenis sebab.

### Ambang (`/ambang`)

1. Kolom "Clause 11" tanpa nama pasal. Pengguna tidak tahu pasal 11 itu apa.
2. Nilai ambang hanya angka 0.55; tidak ada gambaran posisinya di rentang 0.40–0.90.
3. Penjelasan cara kerja 👍/👎 satu paragraf kecil abu-abu.
4. Tidak ada pemilih profil risiko di halaman ini.

### Watchlist (`/watchlist`)

1. Isian hanya menerima kode (maksimal 6 karakter), padahal pencarian nama sudah ada.
2. Tabel tidak menampilkan harga dan perubahan.
3. Tombol "Remove" langsung menghapus tanpa konfirmasi.
4. Catatan sumber data di bawah tabel penuh nama endpoint (`t187ap04_L`).

### Valuasi (`/valuasi/2330`)

1. Halaman dibuka dengan angka "jembatan EV", bukan dengan kesimpulan.
2. Sumber input berupa URL panjang yang membungkus berbaris-baris.
3. Tabel sensitivitas tanpa penjelasan cara membacanya di dekat tabel.

### Jejak audit (`/jejak/<id>`)

1. Sembilan angka kecil (token, biaya, retry) di atas, tanpa kalimat ringkasan.
2. Langkah tampil sebagai daftar datar; status lolos/ditolak hanya teks kecil di kanan.
3. Teks "fallback: tidak ada kunci API" tampil dalam bahasa Indonesia di halaman EN
   (datang dari Python, lihat "Butuh dari Claude").
