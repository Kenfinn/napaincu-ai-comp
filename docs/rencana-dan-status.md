# FEAF: rencana dan status

Berkas ini dipakai tim untuk memantau pekerjaan: rencana awal, yang sudah selesai, yang
berikutnya, yang menunggu orang lain, dan backlog. Terakhir diperbarui: **11 Nov 2026 pagi**.

Tenggat paket finalis: **Jumat 13 Nov, 23:59**. Demo final: 21 Nov.

Kode status: ✅ selesai · 🔄 sedang dikerjakan · ⏳ menunggu orang lain · ⬜ belum mulai

## 1. Rencana awal (10 Nov) dan statusnya

Rincian dan kriteria QA tiap item ada di [`rencana-finalis.md`](./rencana-finalis.md).

| ID | Pekerjaan | Status |
|---|---|---|
| 0 | Gemini jalan di server | ✅ kode (model 404 dicoret, cadangan saat 503, pemutus). ⏳ cek `panggilan_model > 0` setelah deploy dengan `SENTINEL_MODEL=gemini-3.6-flash` |
| A1 | State brief hal. 7 + antrean review manusia | ✅ |
| A2 | Triase keyakinan, 👍/👎 menyetel ambang | ✅ |
| B1 | Pemetaan pasal dari jawaban Patrice | ✅ terpasang (`472727e`). ⏳ cek ambang profil konservatif/agresif oleh tim |
| B2 | DCF otomatis semua emiten non-keuangan | ✅ (Antigravity) |
| B3 | Sitasi MOPS untuk angka laporan keuangan | ✅ (Antigravity). ⏳ uji tautan dari laptop Taiwan |
| C1 | Chatbot "Tanya FEAF" | ✅ versi awal di `/tanya`. ⬜ tautan di menu, versi lengkap untuk 21 Nov |
| D1 | Kandidat gold set dari arsip server | ✅ |
| D2 | Gold set 30–50 + baseline menit manual | ⏳ Ferry & Patrice |
| D3 | Set uji serangan | ✅ (Antigravity), 0 angka penyerang terbit |
| D4 | Skrip evaluasi lengkap | ✅ `--operasional`, `--chat`. Akurasi menunggu gold set |
| D5 | Laporan evaluasi + keamanan + jejak asli dengan model | ⬜ butuh Gemini jalan di server dan gold set |
| E1 | README finalis | ⬜ paling akhir |
| E2 | Deck, video, formulir | ⏳ Afinzaki |

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
| 11 Nov | Pasal 7 (auditor) dan 8 (pejabat kunci) jadi sinyal tata kelola, tanpa nama orang (jawaban Patrice) | lihat git log |

Tes otomatis: 178, semua lulus, tanpa jaringan.

Hasil evaluasi operasional terbaru (`eval/hasil/operasional-20261111T024832Z.md`, 581
pengumuman asli 10 Nov, tanpa model): **241 terbit**, 58 ditahan untuk manusia (40 belum ada
valuasi, 8 tanpa angka, 6 risiko serius, 4 kejadian berat), 282 diarsipkan dengan alasan.
Sebelum B1 (10 Nov malam): 0 terbit.

## 3. Berikutnya (Claude)

Putaran 3 Antigravity (11 Nov siang) mengerjakan urutan 1 dan 1b, uji C1, draf laporan keamanan, dan skrip QA: [`prompt-antigravity-3.md`](./prompt-antigravity-3.md), laporan di `docs/laporan-antigravity-3.md`. Claude meninjau hasilnya sebelum Deploy.

| Urutan | Pekerjaan | Selesai bila |
|---|---|---|
| 1 | Kesiapan demo: tab Valuation tidak menunggu beta (beta dihitung di latar), balasan 307 TWSE = tunggu lalu ulang, skrip pemanasan cache untuk emiten besar, cari emiten berdasarkan nama, tautan Tanya FEAF di menu dan di halaman saham | Emiten yang belum pernah dibuka tampil < 10 detik; "TSMC"/"台積電" ketemu |
| 1b | Panduan gold set dan `evaluasi.py` mode gold diperbarui untuk jalur B1 (modal, laporan, berat), karena panduan lama hanya mengenal capex/debt/cash/risiko | Ferry & Patrice bisa melabeli semua jenis peringatan |
| 2 | Cek server setelah deploy: Gemini jalan, "All Issuers" berisi data asli, valuasi otomatis tersimpan | `panggilan_model > 0`, folder `/data/valuasi_otomatis` ada |
| 3 | D5: evaluasi akhir dengan model dan gold set, laporan keamanan, satu jejak audit asli dengan model | Semua metrik Appendix 2 terisi angka asli |
| 4 | E1: README finalis | Bagian wajib lomba lengkap (arsitektur, instalasi, model & versi, env, lisensi, aliran data, izin, keterbatasan) |
| 5 | QA akhir di server, tiga bahasa | Daftar cek di `docs/diagram-alur.md` bagian 3 lolos |

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
| Ferry & Patrice | Label gold set + baseline menit kerja manual | D2, D5 |
| Ferry & Patrice | Cek `AMBANG` di `app/ringkasan.py` dan terjemahan 中文 | Ringkasan |
| Belum dijawab | Format test case resmi panitia, cara menyerahkan repo privat ke juri, field liaison | E2 |

## 5. Keputusan yang dikunci

Kerja langsung di `main`. Tiga bahasa (English bawaan, 繁體中文, Indonesia). Merah naik, hijau
turun. Tanpa label beli/jual. Review manusia hanya menyetujui kasus ragu. Satu ambang 👍/👎
per server. Beta dari harga resmi bursa. Tidak ada data SYSTEX atau mitra ke Gemini. DCF
berbasis kas: pengumuman tanpa pergerakan kas = sinyal atau skenario. Ambang sinyal ikut
profil risiko; antrean review memakai moderat. README diperbarui paling akhir.

## 6. Backlog (setelah 13 Nov atau bila sempat)

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

- Chatbot versi lengkap untuk demo 21 Nov.
- Relay real-time dari laptop Taiwan ke `/api/impor`. OpenAPI bursa tertinggal sekitar satu hari.
- Pasal 51/53 (lain-lain) diserahkan ke triase model (sekarang dilewati).
- 👍/👎 untuk peringatan sinyal (sekarang hanya peringatan yang lewat triase).
- Perbandingan laporan pasal 31 dengan periode yang sama tahun lalu.
- Emiten keuangan TPEx ditandai benar di `pasar.profil` (B2 sudah menangani untuk valuasi).
- Uji serangan dengan Gemini sungguhan (`scripts/uji_serangan.py --model`).
- Latihan demo minimal 5 kali dan latihan Q&A.

## 6. Keputusan yang dikunci

Kerja langsung di `main`. Tiga bahasa (English bawaan, 繁體中文, Indonesia). Merah naik,
hijau turun. Tanpa label beli/jual. Review manusia hanya boleh menyetujui kasus ragu.
Satu ambang 👍/👎 untuk satu server. Beta dari harga resmi bursa. Tidak ada data
SYSTEX atau mitra yang dikirim ke Gemini. README diperbarui paling akhir.
