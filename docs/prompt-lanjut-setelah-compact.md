# Prompt untuk melanjutkan setelah compact

Untuk Afinzaki: setelah menjalankan `/compact`, tempel isi kotak di bawah sebagai pesan
pertama. Isinya menyuruh Claude memuat ulang konteks dari repo, bukan dari ingatan.

````text
Lanjutkan proyek FEAF. Sebelum menjawab atau mengubah apa pun:

1. git pull --rebase origin main, lalu jalankan python3 -m unittest discover -s tests
   (per 11 Nov sore: 236 tes lulus).
2. Baca urut: docs/konteks-sesi.md (keputusan dikunci, lingkungan, peta kode),
   docs/rencana-dan-status.md (selesai, berikutnya, menunggu, backlog),
   docs/pemetaan-pasal.md bagian "Keputusan tim" dan "Jawaban lanjutan Patrice",
   docs/hasil-gold-set.md (angka resmi vs angka di dalam sampel),
   docs/laporan-antigravity-3.md bagian "Tinjauan Claude".
3. Cek commit sejak b3cc0ee (git log --oneline b3cc0ee..HEAD) untuk perubahan dari
   Antigravity atau saya sendiri yang belum kamu ketahui.

Lalu kerjakan "## 3. Berikutnya (Claude)" di docs/rencana-dan-status.md mulai urutan 1
(cek /sehat setelah deploy, lalu D5 dengan Gemini di server, README finalis, QA akhir).
Tenggat paket: Jumat 13 Nov 23:59. Angka evaluasi yang dilaporkan adalah angka SEBELUM
kalibrasi (lihat docs/hasil-gold-set.md).
Setiap item: kerjakan, uji (tes tanpa jaringan + cek nyata bila bisa), commit ke main,
perbarui baris statusnya di docs/rencana-dan-status.md, lalu lapor singkat dalam Bahasa
Indonesia. Tanya saya hanya untuk keputusan yang mengubah perilaku produk.
````

## Yang sudah tersimpan di repo (tidak hilang saat compact)

- Keputusan, lingkungan server, env Gemini, peta kode, temuan: `docs/konteks-sesi.md`
- Status per item, angka evaluasi terbaru, daftar tunggu, backlog: `docs/rencana-dan-status.md`
- Keputusan pasal dan ambang per profil: `docs/pemetaan-pasal.md`
- Hasil dan tinjauan putaran 2 dan 3 Antigravity: `docs/laporan-antigravity-2.md`, `docs/laporan-antigravity-3.md`
- Hasil gold set dan kalibrasi: `docs/hasil-gold-set.md`; laporan keamanan: `docs/laporan-keamanan.md`
- Prompt Antigravity: `docs/prompt-antigravity-2.md`, `docs/prompt-antigravity-berurutan.md`
- Hasil evaluasi: `eval/hasil/`
