# FEAF: rencana dan status

Berkas ini dipakai tim untuk memantau pekerjaan: rencana awal, yang sudah selesai, yang
berikutnya, yang menunggu orang lain, dan backlog. Terakhir diperbarui: **14 Nov 2026**.

Paket finalis: tenggat Jumat 13 Nov, 23:59 (lewat). Demo final: **Sabtu 21 Nov** (9 menit, tanpa perangkat sendiri).

Kode status: ✅ selesai · 🔄 sedang dikerjakan · ⏳ menunggu orang lain · ⬜ belum mulai

## 1. Rencana awal (10 Nov) dan statusnya

Rincian dan kriteria QA tiap item ada di [`rencana-finalis.md`](./rencana-finalis.md).

| ID | Pekerjaan | Status |
|---|---|---|
| 0 | Gemini jalan di server | ✅ 11 Nov sore: 402 saldo prabayar diatasi, `panggilan_model` 12 di jalan pertama, tanpa galat |
| A1 | State brief hal. 7 + antrean review manusia | ✅ |
| A2 | Triase keyakinan, 👍/👎 menyetel ambang | ✅ |
| B1 | Pemetaan pasal dari jawaban Patrice | ✅ terpasang, ditambah pasal 7/8 dan kalibrasi gold set. ⏳ cek ambang profil konservatif/agresif oleh tim |
| B2 | DCF otomatis semua emiten non-keuangan | ✅ (Antigravity) |
| B3 | Sitasi MOPS untuk angka laporan keuangan | ✅ (Antigravity). ⏳ uji tautan dari laptop Taiwan |
| C1 | Chatbot "Tanya FEAF" | ✅ versi awal 11 Nov; versi lengkap C1–C7 12 Nov (panel di setiap halaman, percakapan bertingkat HMAC, Recap, alat menu). Chat Gemini 50/52 di server; tanpa model `--chat` 52/52, `--chat-percakapan` 36/36 (13 Nov) |
| D1 | Kandidat gold set dari arsip server | ✅ |
| D2 | Gold set 30–50 + baseline menit manual | ✅ 46 baris (Patrice), baseline 20–30 menit per pengumuman. Hasil: [`hasil-gold-set.md`](./hasil-gold-set.md) |
| D3 | Set uji serangan | ✅ (Antigravity), 0 angka penyerang terbit |
| D4 | Skrip evaluasi lengkap | ✅ `--operasional`, `--chat`. Akurasi menunggu gold set |
| D5 | Laporan evaluasi + keamanan + jejak asli dengan model | ✅ 11 Nov: `laporan-evaluasi.md` (Gemini 3.6 di server, biaya, latensi, kategori error, jejak contoh), `laporan-keamanan.md` |
| E1 | README finalis | ✅ 11 Nov (v1.0.0), diperbarui 14 Nov ke v1.1.0: 293 tes, URL repo netral, tautan system design |
| E2 | Deck, video, formulir | ⏳ Afinzaki. Deck 9 menit dan naskah ada di disk (`slides/Agentic_AI_Investment_Assistant_9min.pptx`, `docs/naskah-presentasi-9-menit.md`), belum di git |

## 2. Sudah selesai

| Tanggal | Apa | Bukti |
|---|---|---|
| 10 Nov | State brief dan halaman `/review` | `bbbbdad` |
| 10 Nov | Pengurai pengumuman asli: satuan di label, sub-butir | `975bf2a` |
| 10 Nov | Triase keyakinan, ambang dari 👍/👎, halaman `/ambang`; penyari total transaksi pasal 20; profil TPEx tanpa data pribadi | `e4572d6` |
| 10 Nov | DCF otomatis (Antigravity) | `047185f` |
| 10 Nov | 72 skenario serangan, 0 angka penyerang terbit (Antigravity) | `f5d1b3d` |
| 10 Nov | Pemeriksa menolak satuan yang tidak tertulis di sumber | `de5b363` |
| 10 Nov | PDF pertanyaan pasal 11 dan 22 | `docs/untuk-tim/` |
| 11 Nov | Tanya FEAF versi awal, pemeriksa angka jawaban | `4c6222b` |
| 11 Nov | Evaluasi operasional dan chatbot | `de2a62f` |
| 11 Nov | Diagram alur diperbarui | `073e06f` |
| 11 Nov | Putaran 2 Antigravity: beta resmi, penafian, kunci baca, semua emiten, 2330 otomatis, utang lancar, sitasi MOPS, pengungkapan pihak ketiga | `docs/laporan-antigravity-2.md` |
| 11 Nov | Gemini: model 404 dicoret, cadangan saat sibuk, pemutus per jalan, halaman tidak menggantung | `685164e`, `e59a7ef`, `92855b8` |
| 11 Nov | Pengumuman diproses sebelum valuasi; Check now tidak menunggu | `9ae517a` |
| 11 Nov | Versi skema cache valuasi otomatis | `ee737b0` |
| 11 Nov | B1: jalur sinyal 22/23/11/35/31/1/3/40, ambang per profil, pasal 20 jadi skenario | `472727e` |
| 11 Nov | Server: volume `/data` permanen (`feaf-data`) | dicek Afinzaki |
| 11 Nov | Daftar "Source of each input": kolom tidak tertimpa, URL dibungkus, teks Inggris | `8bc177c` |
| 11 Nov | Deploy dengan env model Gemini | dicek Afinzaki |
| 11 Nov | `/sehat` menampilkan mesin, panggilan model, galat model terakhir, sebab cadangan | `ae226ce`, `217e625` |
| 11 Nov | Putaran 3 Antigravity: gold set B1, Valuation cepat (beta latar, 307 diulang), pemanasan cache, cari nama, tautan Tanya FEAF, draf laporan keamanan, skrip QA. Ditinjau dan diperbaiki Claude | `cc373a6`..`0a9f8f0` |
| 11 Nov | Gold set Patrice masuk; bug rugi dalam kurung dan satuan 仟股 diperbaiki; kalibrasi a–d | lihat `hasil-gold-set.md` |
| 11 Nov | Tanya FEAF: filter jenis pengumuman, injeksi ditolak di gerbang; evaluasi chat menilai alat | `f5003cd` |
| 11 Nov | Gemini 402 ditangani; model bawaan 3.6 dengan cadangan 3.5; LICENSE; panduan lokal tiga bahasa | `6720fa0`, `2ba944a` |
| 11 Nov | Pasal 7 (auditor) dan 8 (pejabat kunci) jadi sinyal tata kelola, tanpa nama orang (jawaban Patrice) | lihat git log |
| 12 Nov | Rilis 1.0.0: versi di `/sehat` dan `/docs`, CHANGELOG | `81b2bf2` |
| 12 Nov | Overhaul UI U1–U8 (Antigravity) | `a9221f0`..`6db4d99`, `docs/laporan-antigravity-4.md` |
| 12 Nov | Tanya FEAF C1–C7: panel di setiap halaman, riwayat HMAC, Recap, alat menu, tes keamanan, evaluasi percakapan | `ab9f5c1`..`cd2709c`, `docs/laporan-antigravity-5.md` |
| 13 Nov | Backlog QA-1..QA-6 (feed, pemutus model per thread, alasan ditahan polos, de-identifikasi, isolasi tes, menu dan ponsel) | lihat `backlog-qa-manual.md` |
| 13 Nov | DCF, strengths, watch-outs ikut profil risiko; DCF cache di watchlist, on-demand di `/valuasi` | `a1575d5`, `63cd07d` |
| 14 Nov | QA menyeluruh v1.1.0: K-1, T-1, T-2, M-1..M-6, de-identifikasi `eval/gold.csv`, versi 1.1.0 | `6a0d36f`, `docs/laporan-qa.md` |

Tes otomatis: 293, semua lulus, tanpa jaringan (14 Nov; juga lulus dengan `SENTINEL_DATA_DIR` kosong). QA halaman 84/84.

Hasil evaluasi operasional terbaru (`eval/hasil/operasional-20261111T024832Z.md`, 581
pengumuman asli 10 Nov, tanpa model): **241 terbit**, 58 ditahan untuk manusia (40 belum ada
valuasi, 8 tanpa angka, 6 risiko serius, 4 kejadian berat), 282 diarsipkan dengan alasan.
Sebelum B1 (10 Nov malam): 0 terbit.

## 3. Berikutnya (menuju demo 21 Nov)

Pekerjaan 10–11 Nov di bagian ini (deploy, D5, E1, QA akhir) sudah selesai; rinciannya di git log
dan bagian 2.

| Urutan | Pekerjaan | Selesai bila |
|---|---|---|
| 1 | Deploy `6a0d36f` (v1.1.0) ke server, lalu cek `/sehat`: `versi` = 1.1.0, `versi_kode` sama dengan `python3 -c "from app.main import VERSI_KODE; print(VERSI_KODE)"`, `sebab_cadangan` kosong | `versi_kode` cocok |
| 2 | Tag `v1.1.0` di commit rilis. Catatan: tag `v1.0.0` di GitHub menunjuk `4ab476c` (sebelum riwayat ditulis ulang), bukan `81b2bf2` di `main` | Tag ada dan menunjuk commit di `main` |
| 3 | Opsional dari `laporan-qa.md`: R-1 batasi `/api/tanya` saat ada kode akses, R-2 pemotongan riwayat 1500 karakter vs HMAC, R-3 favicon | Tes + QA halaman lulus |
| 4 | Latihan demo minimal 5 kali dan Q&A; siapkan video cadangan demo | Demo 9 menit lancar tanpa perangkat sendiri |

## 4. Menunggu orang lain

| Siapa | Apa | Untuk |
|---|---|---|
| Afinzaki | Cek Reasoning engine dan Model calls di `/sehat` setelah deploy (deploy sudah) | 0, D5 |
| Afinzaki | Uji data bertahan: catat `/sehat`, Deploy, cek lagi | server |
| Afinzaki | Tarik riwayat MOPS dari laptop Taiwan (data 8–10 Nov hilang sebelum volume dipasang) | data |
| Afinzaki | Uji tautan MOPS dari laptop Taiwan | B3 |
| Afinzaki | Putuskan kapan `SENTINEL_KUNCI_BACA=1`; nyalakan billing dengan kredit AI Pro menjelang demo (opsional) | demo |
| Afinzaki | Formulir pihak ketiga (draf: `docs/pengungkapan-pihak-ketiga.md`) dan self-assessment; deck dan video. Deck perlu menyebut prinsip DCF berbasis kas: pengumuman pasal 20 = skenario | E2 |
| Ferry & Patrice | Cek ambang profil konservatif/agresif dan tingkat sinyal pasal 7/8 (tabel di `pemetaan-pasal.md`), 現金減資, batas pasal 23 (±40% ekuitas?), pasal 51/53 | B1 |
| Ferry & Patrice | Cek `AMBANG` di `app/ringkasan.py` dan terjemahan 中文 | Ringkasan |
| Belum dijawab | Format test case resmi panitia, cara menyerahkan repo privat ke juri, field liaison | E2 |

## 5. Keputusan yang dikunci

Kerja langsung di `main`. Tiga bahasa (English bawaan, 繁體中文, Indonesia). Merah naik, hijau
turun. Tanpa label beli/jual. Review manusia hanya menyetujui kasus ragu. Satu ambang 👍/👎
per server. Beta dari harga resmi bursa. Tidak ada data SYSTEX atau mitra ke Gemini. DCF
berbasis kas: pengumuman tanpa pergerakan kas = sinyal atau skenario. Ambang sinyal ikut
profil risiko; antrean review memakai moderat. README diperbarui paling akhir.

## 6. Backlog (setelah 21 Nov atau bila sempat)

- Bahasa dasar sistem jadi Inggris. Tampilan bawaan sudah Inggris, tetapi bagian dalam
  masih Indonesia. Urutan yang diusulkan, dari dampak terbesar:
  1. Prompt ke model (`SISTEM` dan `INSTRUKSI` di `app/agent/llm.py`, `extract.py`,
     `ringkasan.py`). Model umumnya lebih konsisten dengan prompt Inggris. Perlu naikkan
     `VERSI_PROMPT` dan jalankan ulang evaluasi, karena jawaban cache lama tidak terpakai.
  2. Teks yang tersimpan di jejak audit dan JSON API (`alasan`, `nama`, `tahap`, dan teks
     cadangan di `i18n.pesan`). Juri membaca JSON mentah.
  3. Komentar dan docstring di kode.
  4. Nama fungsi, variabel, status internal (`terbit`, `ditahan`, `dilewati`), dan nama
     berkas. Ini refactor besar yang menyentuh semua tes, jadi dikerjakan setelah 21 Nov
     atau dalam satu putaran khusus dengan tes sebagai pengaman.
  Dokumen untuk tim (docs/) tetap boleh Indonesia.

- Relay real-time dari laptop Taiwan ke `/api/impor`. OpenAPI bursa tertinggal sekitar satu hari.
- Pasal 51/53 (lain-lain) diserahkan ke triase model (sekarang dilewati).
- 👍/👎 untuk peringatan sinyal (sekarang hanya peringatan yang lewat triase).
- Perbandingan laporan pasal 31 dengan periode yang sama tahun lalu.
- Emiten keuangan TPEx ditandai benar di `pasar.profil` (B2 sudah menangani untuk valuasi).
- Uji serangan dengan Gemini sungguhan (`scripts/uji_serangan.py --model`).
