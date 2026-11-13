# Tugas A — Agent & Data (28 Sep – 8 Okt)

Turunan dari [`rekap.md`](./rekap.md) untuk jalur A (ketua tim). Rencana awal ada di
[`rencana-kerja.md`](./rencana-kerja.md), catatan teknis sumber data di
[`akses-data.md`](./akses-data.md). **Kalau berkas ini dan `rekap.md` berbeda, ikuti `rekap.md`.**

**Definisi selesai 8 Okt:** alur Sentinel Saham jalan ujung ke ujung di **data asli** dengan
**model aktif** (`panggilan_model > 0` di jejak audit), bisa dijalankan ulang di depan orang
lain, dan sudah direkam untuk video.

**Status per 28 Sep:** status mahasiswa ✅ · pendaftaran tim ✅ · briefing ditinjau ✅ ·
uji akses data ✅ (14 Sep, lihat di bawah) · agent + web + 14 tes ✅ · model belum pernah
dipanggil ⏳ · data asli belum dicoba di aplikasi ⏳

## Cara bagi kerja

- **Kamu** = yang butuh jaringan kampus Taiwan, keputusan, penilaian manusia, kunci API, dan
  rekaman. Claude tidak bisa mengakses MOPS/TWSE dari cloud (terblokir di luar Taiwan).
- **Claude** = menulis kode, tes, dan dokumentasi, memakai data contoh di `data/fixtures/`.
  Data asli di `data/` tidak di-commit; kalau Claude perlu contoh nyata, pilih beberapa
  pengumuman dan simpan sebagai fixture baru.

**Aturan minggu ini dari `rekap.md`: jangan tambah fitur.** Jalur kritis tim adalah wawancara
(B), bukan kode.

---

## Keputusan uji 72 jam — GO

Sudah dijalankan dari jaringan kampus pada 14 September 2026: 5 emiten (2330, 2317, 2881,
1301, 2412), 711 pengumuman, 100% bersitasi. Host yang melayani adalah `mopsov.twse.com.tw`,
bukan `mops.twse.com.tw`. Rincian di [`akses-data.md`](./akses-data.md).

Skrip yang dulu direncanakan di sini sudah ada: `scripts/spike_mops.py`,
`scripts/parse_mops.py`, `scripts/fetch_details.py`.

## Yang sudah jadi (jangan dibangun ulang)

| Rencana awal | Wujudnya sekarang |
|---|---|
| Evidence layer + validasi bentuk respons + retry | `scripts/spike_mops.py`, `fetch_details.py`, `app/store.py` (JSON, bukan SQLite) |
| Penyusun alert bersitasi via LLM | `app/agent/extract.py` + `llm.py` (Gemini), dengan penalar aturan sebagai cadangan |
| Verifier angka + kasus gagal sengaja | `app/agent/verify.py` (7 pemeriksaan) + 4 fixture, termasuk prompt injection dan USD |
| Operation trace | `app/agent/pipeline.py` → `data/traces/`, tampil di halaman jejak audit |
| Runner + README | `uvicorn app.main:app`, `README.md`, `rekap.md` Bagian 6 |

---

## ▶️ Sekarang (28 Sep – 1 Okt)

| # | Siapa | Tugas | Selesai kalau |
|---|---|---|---|
| 1 | Kamu | Tahap 1 `rekap.md`: jalankan apa adanya di laptop | 14 tes OK, 4 peringatan tampil dengan pita "Data contoh." |
| 2 | Kamu | Tahap 2: buat kunci Gemini, pasang lewat `read -rs` (**jangan di-commit**) | Panel bertuliskan "Model aktif.", jejak audit `panggilan_model > 0` |
| 3 | Kamu | Tahap 3 dari jaringan kampus: tarik data asli 2330 | Pita "Data contoh." hilang, panel "Sumber data: nyata." |
| 4 | Kamu | Rekam layar tahap 3 sekalian | File rekaman ada, untuk bahan video C |

## Setelah model & data asli jalan (1 – 8 Okt)

| Tanggal | Claude kerjakan | Kamu kerjakan |
|---|---|---|
| 1 – 3 Okt | Perbaiki apa pun yang rusak saat model asli atau data asli pertama kali dipakai | Laporkan pesan error / jejak yang aneh |
| 3 – 5 Okt | Skrip pembanding Appendix 2: penalar aturan vs model pada kasus yang sama | Review 3–5 peringatan yang terbit: jelas, tidak berbau saran beli/jual? |
| 5 – 6 Okt | — | Coba "rusak" sendiri: apakah pemeriksa menangkapnya? |
| 6 – 7 Okt | Draf deck hal. 1 dan 4–12 (yang tidak bergantung wawancara) | — |
| 7 – 8 Okt | — | Jalankan ujung ke ujung ≥3 kali, **rekam**, serahkan ke C |

## Serahan ke tim (tanggung jawabmu)

| Kapan | Ke | Apa |
|---|---|---|
| 1 Okt | Semua | Kabar: model aktif & data asli jalan, atau apa yang menghambat |
| 6 Okt | C | Diagram arsitektur & state (sudah ada di `design/export/`) + contoh peringatan asli |
| 8 Okt | C | Rekaman demo kasar |
| 8 Okt | B | Format gold set yang bisa langsung dijalankan di Fase 3 |

## Jangan dikerjakan sekarang

Banyak emiten · valuasi Fubon (2881) · antarmuka tanya-jawab · penyetelan ambang dari reaksi
👍/👎 (ambang masih tetap 0,55). Semuanya ditulis jujur di deck sebagai rencana final, lihat
`rekap.md` Bagian 5.
