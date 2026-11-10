# FEAF: rencana dan status

Berkas ini dipakai tim untuk memantau pekerjaan. Isinya rencana awal, apa yang sudah
selesai, apa yang dikerjakan berikutnya, dan backlog. Diperbarui setiap kali ada item
yang selesai. Terakhir diperbarui: 10 Nov 2026 malam.

Tenggat paket finalis: Jumat 13 Nov, 23:59. Demo final: 21 Nov.

Kode status: ✅ selesai · 🔄 sedang dikerjakan · ⏳ menunggu orang lain · ⬜ belum mulai

## 1. Rencana awal (disusun 10 Nov)

Daftar ini berasal dari masukan tim setelah lolos finalis. Rinciannya ada di
[`rencana-finalis.md`](./rencana-finalis.md).

| ID | Pekerjaan | Status |
|---|---|---|
| 0 | Gemini memakai model pengganti bila nama model ditolak (404) | ✅ kode, ⏳ cek di server |
| A1 | Nama state sesuai brief hal. 7, antrean review manusia | ✅ |
| A2 | Skor keyakinan triase, 👍/👎 menyetel ambang | ✅ |
| B1 | Pemetaan pasal dari data asli | ✅ draf, ⏳ jawaban Ferry & Patrice |
| B2 | DCF otomatis untuk semua emiten non-keuangan | ✅ (Antigravity) |
| B3 | Sitasi angka laporan keuangan ke MOPS | ⬜ |
| C1 | Chatbot "Tanya FEAF" versi awal di atas data asli | Claude | Angka di jawaban selalu ada di hasil tool, bersumber, tanpa kata beli/jual | ✅ versi awal di `/tanya` (18 tes). Tautan di menu menunggu Antigravity selesai dengan `base.html` |
| D1 | Kandidat gold set dari arsip server | ✅ |
| D2 | Gold set 30–50 pengumuman + baseline menit manual | ⏳ Ferry & Patrice |
| D3 | Set uji serangan otomatis | ✅ (Antigravity) |
| D4 | Skrip evaluasi lengkap dengan data asli | Claude | Latensi, biaya, retry, intervensi manusia, kategori error terisi angka asli | ✅ `--operasional` dan `--chat` (`eval/hasil/operasional-*`, `chat-*`). Akurasi menunggu gold set |
| D5 | Laporan evaluasi, laporan keamanan, jejak audit asli | ⬜ |
| E1 | README finalis | ⬜ dikerjakan paling akhir |
| E2 | Deck, video, formulir | ⏳ Afinzaki |

## 2. Sudah selesai

| Tanggal | Apa | Bukti |
|---|---|---|
| 10 Nov | State brief (FETCHED sampai PUBLISHED/HELD/ARCHIVED) dan halaman `/review` | commit `bbbbdad` |
| 10 Nov | Model pengganti saat Gemini 404 | commit `1869173` |
| 10 Nov | Pengurai pengumuman asli: satuan di label, sub-butir (1)(2)(3) | commit `975bf2a` |
| 10 Nov | Triase keyakinan dan ambang dari 👍/👎, halaman `/ambang` | commit `e4572d6` |
| 10 Nov | Penyari mengambil total transaksi pasal 20, satuan 萬/億, kode mata uang | commit `e4572d6` |
| 10 Nov | Profil TPEx tidak lagi menyimpan nama pejabat dan email | commit `e4572d6` |
| 10 Nov | DCF otomatis dari FinMind, harga bursa, dan beta Yahoo | commit `047185f` |
| 10 Nov | 72 skenario serangan, 0 angka penyerang terbit | commit `f5d1b3d`, `eval/hasil/serangan-2026-11-10.md` |
| 10 Nov | Pemeriksa menolak satuan yang tidak tertulis di sumber | commit `de5b363` |
| 10 Nov | PDF pertanyaan pasal 11 dan 22 untuk Ferry & Patrice | `docs/untuk-tim/` |

Tes otomatis: 131, semua lulus (11 Nov dini hari).

## 3. Dikerjakan berikutnya

Kolom "Siapa" menunjukkan pembagian kerja. Antigravity dan Claude bekerja di `main`
bersamaan, dengan berkas yang dibagi supaya tidak saling menimpa. Spesifikasi untuk
Antigravity ada di [`prompt-antigravity-2.md`](./prompt-antigravity-2.md). Versi tiga agent
paralel (DATA, WEB, QA) ada di [`prompt-antigravity-multiagen.md`](./prompt-antigravity-multiagen.md);
koordinasinya di `docs/papan-agen.md`. Untuk kerja semalam tanpa pengawasan dipakai
[`prompt-antigravity-berurutan.md`](./prompt-antigravity-berurutan.md) (P1–P10).

### Rabu 11 Nov

| ID | Pekerjaan | Siapa | Selesai bila | Status |
|---|---|---|---|---|
| R1 | Beta dihitung dari harga harian resmi TWSE/TPEx dan indeks TAIEX. Yahoo tidak dipakai lagi | Antigravity | Beta 2330 dari sekitar 100 minggu data; data kurang memberi 1,0 bertanda | ✅ Selesai (`88e5770`, beta 2330 = 1,03 dari 104 pekan, Yahoo bersih) |
| R2 | Penafian "bukan rekomendasi" di semua halaman analisis; kalimat profil risiko dilunakkan | Antigravity | Penafian tampil di tiga bahasa di setiap halaman analisis | ✅ Selesai (`0849027`, `_penafian.html` tepat 1x per halaman) |
| R3 | Pilihan kunci akses untuk halaman baca (`SENTINEL_KUNCI_BACA`) | Antigravity | Tanpa kode muncul halaman kode; `/sehat` tetap terbuka | ✅ Selesai (`e0b2c0d`, middleware 401 + halaman kunci) |
| D-a | Agent memproses pengumuman semua emiten, tidak hanya watchlist | Antigravity | Server memproses ratusan pengumuman asli; halaman tetap cepat saat memproses | ✅ Selesai (`6e731fc`, lock terpisah, `?lingkup=semua`) |
| D-b | 2330 memakai valuasi otomatis; berkas manual hanya menyimpan asumsi tim | Antigravity | Angka keuangan 2330 sama dengan FinMind | ✅ Selesai (`c04ddee` & `c70f432`, panaskan semua emiten) |
| D-c | Utang jangka panjang yang jatuh tempo setahun terbaca di valuasi otomatis | Antigravity | Utang 2330 otomatis selisih kurang dari 1% dari manual | ✅ Selesai (`fb49d77`, utang total 2330 selisih 0,00%) |
| C1 | Chatbot "Tanya FEAF" versi awal di atas data asli | Claude | Angka di jawaban selalu ada di hasil tool, bersumber, tanpa kata beli/jual | ⬜ |

### Kamis 12 Nov

| ID | Pekerjaan | Siapa | Selesai bila | Status |
|---|---|---|---|---|
| B3 | Tautan MOPS untuk angka laporan keuangan dan valuasi | Antigravity | Setiap kolom periode di tab Financials punya tautan MOPS | ✅ Selesai (`c5c9404`, sitasi MOPS + cek FinMind 100% cocok) |
| R4 | Draf pengungkapan pihak ketiga dan alat AI untuk formulir panitia | Antigravity | Daftar lengkap: nama, tujuan, lingkup, lisensi | ✅ Selesai (`b9fa8fd`, `docs/pengungkapan-pihak-ketiga.md`) |
| D4 | Skrip evaluasi lengkap dengan data asli | Claude | Latensi, biaya, retry, intervensi manusia, kategori error terisi angka asli | ⬜ |
| — | Diagram alur diperbarui (triase, ambang, review, valuasi otomatis) | Claude | PNG baru di `docs/diagram/` | ✅ `docs/diagram-alur.md` + PNG/SVG |

### Jumat 13 Nov

| ID | Pekerjaan | Siapa | Status |
|---|---|---|---|
| B1 | Pasang jawaban Ferry & Patrice: label pasal 11, 22, 23, 31, jalur sinyal risiko, pasal 31 memicu hitung ulang DCF | Claude | ⏳ |
| D5 | Evaluasi akhir (dengan gold set) dan laporan | Claude | ⏳ |
| E1 | README finalis | Claude | ⬜ |
| QA | Uji akhir di server, tiga bahasa | Claude + Afinzaki | ⬜ |
| E2 | Kirim paket | Afinzaki | ⬜ |

Temuan evaluasi operasional 10 Nov (578 pengumuman asli, penalar aturan): 0 terbit,
96 ditahan (56 tanpa angka bersumber, 40 tanpa model valuasi), 7 diarsipkan triase,
478 dilewati saringan pasal. Artinya pada data asli agent belum menerbitkan apa pun
sampai B1 (pemetaan pasal) dan B2/D-b (valuasi otomatis di server) terpasang.

## 4. Menunggu orang lain

| Siapa | Apa | Untuk |
|---|---|---|
| Ferry & Patrice | Jawaban PDF pasal 11/22 (Q1–Q9) dan 7 pertanyaan di `pemetaan-pasal.md`. Target Rabu siang | B1 |
| Ferry & Patrice | Label gold set dan baseline menit kerja manual. Target Kamis siang | D2, D5 |
| Ferry & Patrice | Cek ambang penilaian di `app/ringkasan.py` dan terjemahan 中文 | Ringkasan |
| Afinzaki | Deploy ulang setiap ada batch baru, lalu cek jejak audit `panggilan_model` lebih dari 0. Per 10 Nov malam masih 0 | 0 |
| Afinzaki | Tarik riwayat MOPS dari laptop Taiwan | data sebelum 8 Nov |
| Afinzaki | Uji tautan MOPS dari laptop Taiwan setelah B3 | B3 |
| Afinzaki | Putuskan kapan `SENTINEL_KUNCI_BACA=1` dinyalakan | R3 |
| Afinzaki | Isi formulir pihak ketiga dan self-assessment, termasuk catatan cache profil TPEx yang sempat menyimpan nama | E2 |
| Belum dijawab | Format test case resmi panitia, cara menyerahkan repo privat ke juri, field liaison | E2 |

Catatan tinjauan Claude untuk putaran 2 (11 Nov dini hari): `tests/test_putaran2.py`
`test_dc_manual_mengisi_yang_kosong` memakai cache valuasi otomatis asli di `data/` dan
gagal bila ada cache 2330 yang dibuat sebelum D-c. Masalah yang sama terjadi di server:
cache lama tidak punya tanda `tidak_tersedia`, dan pipeline menerima cache basi, jadi utang
2330 tetap kurang 13% sampai cache dibangun ulang. Perlu versi skema di cache (cache tanpa
versi terbaru dianggap tidak ada) dan tes yang memakai folder cache sementara.
Temuan kedua: `valuasi_otomatis.panaskan` melewati emiten yang punya berkas manual, jadi
cache otomatis 2330 tidak pernah dibangun di server dan D-b (2330 otomatis + asumsi tim)
tidak pernah aktif di sana. Perlu: panaskan tetap membangun cache untuk emiten berkas manual.

## 5. Backlog (setelah 13 Nov atau bila sempat)

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
- Pasal 51/53 (lain-lain) diserahkan ke triase model.
- Sinyal tata kelola dari pasal 6/7/8 (ganti direksi, auditor).
- Transaksi tunggal pasal 20 ditambahkan ke capex, bukan mengganti. Menunggu jawaban Q8 di `pemetaan-pasal.md`.
- Emiten keuangan TPEx ditandai benar di `pasar.profil` (B2 sudah menangani untuk valuasi).
- Uji serangan dengan Gemini sungguhan (`scripts/uji_serangan.py --model`).
- Latihan demo minimal 5 kali dan latihan Q&A.

## 6. Keputusan yang dikunci

Kerja langsung di `main`. Tiga bahasa (English bawaan, 繁體中文, Indonesia). Merah naik,
hijau turun. Tanpa label beli/jual. Review manusia hanya boleh menyetujui kasus ragu.
Satu ambang 👍/👎 untuk satu server. Beta dari harga resmi bursa. Tidak ada data
SYSTEX atau mitra yang dikirim ke Gemini. README diperbarui paling akhir.
