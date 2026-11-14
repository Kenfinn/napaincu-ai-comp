# Prompt lanjut setelah compact (13 Nov pagi)

Tempel kotak ini sebagai pesan pertama setelah `/compact`:

```text
Lanjutkan proyek FEAF. Kuota Claude mingguan tinggal sedikit: hemat panggilan alat, kerjakan sendiri hanya
yang kecil; pekerjaan besar ditulis sebagai action plan di docs/backlog-qa-manual.md untuk Antigravity.

Sebelum apa pun:
1. git pull --rebase origin main; python3 -m unittest discover -s tests (13 Nov pagi: 4 gagal karena tes
   bergantung data lokal, lihat QA-5); python3 scripts/qa_halaman.py (81/81).
2. Baca: docs/prompt-lanjut-setelah-compact.md bagian "Kondisi 13 Nov" (berkas ini), lalu
   docs/backlog-qa-manual.md (tabel status), docs/konteks-sesi.md (keputusan dikunci),
   docs/laporan-evaluasi.md (angka resmi).
3. git log --oneline 15eaf3c..HEAD untuk melihat yang dikerjakan Antigravity sejak itu.

Tenggat paket finalis: HARI INI Jumat 13 Nov 23:59 (Asia/Taipei). Demo final 21 Nov (9 menit: 5 presentasi
+ 4 tanya jawab, tanpa perangkat sendiri). Angka evaluasi resmi = angka SEBELUM kalibrasi.
Balas dalam Bahasa Indonesia, singkat. Tanya saya hanya untuk keputusan yang mengubah perilaku produk.
```

## Kondisi 13 Nov

**Rilis.** v1.0.0 di `main` (commit "Rilis 1.0.0"); tag `v1.0.0` belum ada (push tag ditolak 403 dari
sesi cloud; Afinzaki membuat tag dari laptop/GitHub). `/sehat` memuat `versi` dan `versi_kode`.

**v1.1 (dikerjakan Antigravity, sudah di `main`).**
- Overhaul UI U1–U8 (`docs/prompt-antigravity-4-ui.md`, laporan `docs/laporan-antigravity-4.md`).
- Panel Tanya FEAF di setiap halaman, percakapan bertingkat dengan riwayat bertanda tangan HMAC,
  Recap, alat menu hanya-baca (feed, peringatan, jejak, review, ambang, watchlist), C1–C7
  (`docs/prompt-antigravity-5-chat.md`, laporan `docs/laporan-antigravity-5.md`).
- Backlog QA manual selesai: QA-1 feed, QA-2 pemutus model per thread (narasi AI semua profil),
  QA-3 alasan ditahan dalam bahasa polos.
- Belum ditinjau Claude secara menyeluruh. Server sudah menjalankan versi ini (2437 pengumuman,
  Gemini 3.6 jalan, tanpa galat, 13 Nov 03:23 UTC).

**Backlog terbuka** (`docs/backlog-qa-manual.md`): QA-4 de-identifikasi nama anggota tim
(aturan final: "all materials must be de-identified"), QA-5 isolasi tes dari data lokal,
QA-6 menu lebih lebar + tampilan ponsel. Prompt untuk Antigravity ada di kepala berkas backlog.

**Kesesuaian dengan aturan lomba** (dicek 12 Nov dari situs resmi): syarat kelayakan terpenuhi.
Celah untuk skor final: validasi pengguna baru Level 2 (perlu Level 3: 2–3 pengguna memakai
prototipe + umpan balik + perbandingan waktu), alur SYSTEX "pengiriman proaktif" belum ada
(notifikasi/ringkasan harian), video cadangan demo.

## Yang kurang untuk pengumpulan hari ini

Status diperbarui 14 Nov. No.3–9 dikerjakan di luar repo; statusnya belum dicatat di sini.

| No | Item | Siapa | Status |
|---|---|---|---|
| 1 | QA-4 de-identifikasi, QA-5 tes lulus semua, QA-6 menu/ponsel | Antigravity | Selesai (`ddd5d2d`, `4dbc425`, `3179254`) |
| 2 | Tinjauan Claude atas v1.1 + ulang `evaluasi.py --chat` (52/52) dan `--chat-percakapan` | Claude | Selesai: `docs/laporan-qa.md`, `--chat` 52/52, `--chat-percakapan` 36/36, perbaikan di `6a0d36f` |
| 3 | Putuskan versi yang diserahkan: v1.1 bila no.1–2 lulus ±18:00, selain itu v1.0 | Afinzaki | Belum |
| 4 | Link prototipe netral (domain kedua, mis. `feaf.<IP>.sslip.io` di Dokploy) — domain sekarang memuat nama anggota | Afinzaki | Belum |
| 5 | Kunci akses: `SENTINEL_KODE_AKSES` + `SENTINEL_KUNCI_BACA=1`, kode juri lewat formulir saja | Afinzaki | Belum |
| 6 | Saldo prabayar Gemini cukup sampai 21 Nov | Afinzaki | Belum |
| 7 | Repo untuk juri: akses repo privat atau ZIP sumber (nama pengguna GitHub ikut terlihat di link) | Afinzaki | Belum |
| 8 | Satu PDF gabungan "Field Requirements & Validation Data" + "Agent Evaluation Data & Operation Traces" (FAQ A4), nama berkas pola penyisihan; bahan: `docs/laporan-evaluasi.md`, `docs/hasil-gold-set.md`, `eval/hasil/jejak-contoh-*.json` | Antigravity/Afinzaki | Belum |
| 9 | Deck terbaru + kebutuhan demo, formulir pihak ketiga (`docs/pengungkapan-pihak-ketiga.md`: Gemini 3.6/3.5, alat bantu AI), self-assessment | Afinzaki | Belum |
| 10 | Tag `v1.0.0` (atau `v1.1.0`) di GitHub | Afinzaki | `v1.0.0` ada tetapi menunjuk `4ab476c` (sebelum riwayat ditulis ulang, bukan di `main`); `v1.1.0` belum |
