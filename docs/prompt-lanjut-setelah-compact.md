# Prompt untuk melanjutkan setelah compact

Untuk Afinzaki: setelah menjalankan `/compact`, tempel isi kotak di bawah sebagai pesan
pertama. Isinya menyuruh Claude memuat ulang konteks dari repo, bukan dari ingatan.

````text
Lanjutkan proyek FEAF. Sebelum menjawab atau mengubah apa pun:

1. git pull --rebase origin main, lalu jalankan python3 -m unittest discover -s tests
   (per 11 Nov pagi: 178 tes lulus).
2. Baca urut: docs/konteks-sesi.md (keputusan dikunci, lingkungan, peta kode),
   docs/rencana-dan-status.md (selesai, berikutnya, menunggu, backlog),
   docs/pemetaan-pasal.md bagian "Keputusan tim" dan "Status implementasi",
   docs/laporan-antigravity-2.md bagian "Tinjauan Claude".
3. Cek commit sejak 472727e (git log --oneline 472727e..HEAD) untuk perubahan dari
   Antigravity atau saya sendiri yang belum kamu ketahui.

Lalu kerjakan "## 3. Berikutnya (Claude)" di docs/rencana-dan-status.md mulai urutan 1
(kesiapan demo: tab Valuation tidak menunggu beta, 307 TWSE = tunggu lalu ulang, skrip
pemanasan cache, cari emiten berdasarkan nama, tautan Tanya FEAF di menu dan halaman saham).
Setiap item: kerjakan, uji (tes tanpa jaringan + cek nyata bila bisa), commit ke main,
perbarui baris statusnya di docs/rencana-dan-status.md, lalu lapor singkat dalam Bahasa
Indonesia. Tanya saya hanya untuk keputusan yang mengubah perilaku produk.
````

## Yang sudah tersimpan di repo (tidak hilang saat compact)

- Keputusan, lingkungan server, env Gemini, peta kode, temuan: `docs/konteks-sesi.md`
- Status per item, angka evaluasi terbaru, daftar tunggu, backlog: `docs/rencana-dan-status.md`
- Keputusan pasal dan ambang per profil: `docs/pemetaan-pasal.md`
- Hasil dan tinjauan putaran 2 Antigravity: `docs/laporan-antigravity-2.md`
- Prompt Antigravity: `docs/prompt-antigravity-2.md`, `docs/prompt-antigravity-berurutan.md`
- Hasil evaluasi: `eval/hasil/`
