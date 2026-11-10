# Konteks kerja — BACA INI DULU

Pegangan untuk melanjutkan tanpa riwayat percakapan (untuk sesi Claude berikutnya,
Antigravity, dan tim). Per **10 Nov 2026 malam** (diperbarui setelah A2). Berkas ini menggantikan `rekap.md` sebagai status
terbaru; daftar kerja rinci ada di [`rencana-finalis.md`](./rencana-finalis.md).

---

## 1. Produk, tim, tenggat

- **FEAF · Agentic AI Investment Assistant**, NAPAI AAIC 2026, track SYSTEX (Investment
  Intelligence & AI-Powered Stock Selection Agent). **Lolos finalis.**
- Agent memantau pengumuman material (重大訊息) emiten di watchlist, mengekstrak angka
  beserta kalimat sumbernya, memverifikasinya secara deterministik, menghitung ulang
  valuasi, lalu menerbitkan peringatan, atau berhenti dan menyerahkan ke manusia.
- Tim: **Afinzaki** (teknis, pemilik server), **Ferry** dan **Patrice** (keuangan &
  lapangan; di dokumen lama disebut "PDK"). Patrice & Ferry menyusun proposal brief
  10 halaman (berkas PDF dari tim, tidak di repo).
- **Paket finalis: Jumat 13 Nov 23:59.** Final demo langsung: 21 Nov.
- Penilaian final: Task completion & stability 25% (tie-break), Field impact 20%,
  Agentic depth 20%, Safety 15%, Innovation 10%, Demo & Q&A 10%. Aturan lengkap:
  [`aaic-2026-ringkasan.md`](./aaic-2026-ringkasan.md).

## 2. Keputusan yang sudah dikunci (jangan diubah tanpa tanya)

| Hal | Keputusan |
|---|---|
| Branch | **Kerja langsung di `main`** sampai pengguna meminta branch baru |
| Bahasa | **Tiga bahasa: English (bawaan), 繁體中文, Bahasa Indonesia.** Semua teks lewat `app/i18n.py`; tes gagal bila ada kunci kurang satu bahasa |
| Warna | **Merah = naik, hijau = turun** (konvensi Taiwan) |
| Kesimpulan analisis | Hasil analisis + kesimpulan beralasan (permintaan PDK), **tanpa label beli/jual** (brief hal. 9: saran otomatis di Taiwan wajib berizin FSC) |
| State | Nama state brief hal. 7. Verifier gagal → **HELD FOR REVIEW** |
| Review manusia | Setujui **hanya kasus ragu** (mata uang asing, besaran di luar pita, belum ada model valuasi, keyakinan rendah). Kutipan/angka karangan **hanya bisa diarsipkan** |
| Umpan balik 👍/👎 | Satu ambang **untuk seluruh server** |
| Beta DCF otomatis | **Dihitung dari harga** (return mingguan 2 tahun vs TAIEX); data kurang → 1,0 dan ditandai |
| Chatbot "Tanya FEAF" | Versi awal 13 Nov, lengkap 21 Nov |
| Bentuk prototipe | Web FastAPI + Jinja2, tanpa login, satu worker |
| Data asli di repo | Hanya sampel kecil untuk tes (tanpa data pribadi). `data/` tidak di-commit |
| Gaya kerja | Jawaban ke pengguna berbahasa Indonesia; tanya dulu untuk keputusan penting; QA sendiri sebelum melapor |

## 3. Lingkungan

| Hal | Isi |
|---|---|
| Repo | `Kenfinn/napaincu-ai-comp`, branch `main` |
| Server | Dokploy milik Afinzaki, domain **https://feaf.afinzaki.my.id**, container port **8000**, volume **`/data`** |
| Env server | `SENTINEL_KODE_AKSES`, `SENTINEL_TARIK_OTOMATIS_DETIK=600`, `SENTINEL_SERTAKAN_CONTOH=1`, `GEMINI_API_KEY`, `FINMIND_TOKEN` (opsional). Awalan `SENTINEL_` sengaja dipertahankan walau nama produk FEAF |
| Deploy | Push ke `main` lalu tekan **Deploy** di Dokploy. Panduan: [`deploy-dokploy.md`](./deploy-dokploy.md) |
| Tes | `python3 -m unittest discover -s tests` → **107 tes, semua lulus**, ±3 detik, **tanpa jaringan** (tes yang menyentuh pasar/penarik memutus jaringan) |
| Sesi cloud Claude | Bisa: OpenAPI TWSE/TPEx, FinMind, Yahoo. **Tidak bisa: MOPS** (diblokir di luar Taiwan). Build Docker butuh CA proxy sesi (lihat `/root/.ccr/README.md`); Dockerfile di repo tidak perlu diubah |
| Laptop Taiwan | Satu-satunya jalan ke MOPS: riwayat pengumuman ([`tarik-riwayat.md`](./tarik-riwayat.md)), uji tautan MOPS |

## 4. Peta kode

| Berkas | Isi |
|---|---|
| `app/main.py` | Rute web + API, pemantau otomatis (thread), kode akses, `/sehat`, `/review`, `/saham/{kode}`, `/api/impor`, `/ekspor/kandidat-gold.csv` |
| `app/tarik.py` | Penarik OpenAPI (`t187ap04_L`, `mopsfin_t187ap04_O`), watchlist, pengurai butir (**satuan dari label, sub-butir**), dedup, impor riwayat |
| `app/agent/pipeline.py` | Orkestrasi + jejak; `STATE` brief; penerapan keputusan review |
| `app/agent/screen.py` | Saringan pasal (`KLAUSA_RELEVAN`) — **masih daftar lama, menunggu verifikasi** |
| `app/agent/extract.py` | Penyari (model / penalar aturan), `LABEL_SAH` (**masih label lama**), `label_sah()` ternormalisasi |
| `app/agent/verify.py` | 7 cek pra-hitung + cek sirkularitas; `sumber_terbukti()` untuk triase |
| `app/agent/triase.py` | Skor keyakinan 0–1 dari komponen (pasal, angka, materialitas vs kapitalisasi) + putusan lanjut/ragu/arsip |
| `app/umpan_balik.py` | 👍/👎 → ambang per pasal (dasar 0,55; +0,05/👎, −0,02/👍; 0,40–0,90), reset, kunci, riwayat |
| `app/agent/llm.py` | Gemini REST, retry, **cache jawaban** (`DATA_DIR/cache_model`), **model pengganti saat 404** |
| `app/agent/recompute.py`, `scripts/dcf.py` | Hitung ulang DCF (berkas manual hanya `valuation/inputs/2330.json`) |
| `app/review.py` | Keputusan review (`DATA_DIR/keputusan_review.json`), aturan "hanya ragu" |
| `app/pasar.py` | Harga/PER/profil (OpenAPI), laporan keuangan (FinMind) + cache, tabel Financials, statistik, median PER industri, `emiten_dikenal()` |
| `app/ringkasan.py` | Tab Ringkasan: penilaian per aspek (`AMBANG`), narasi Gemini yang diperiksa |
| `app/gold.py` | Kandidat gold set dari arsip mentah server |
| `app/i18n.py` | Kamus tiga bahasa, format angka per bahasa |
| `scripts/evaluasi.py` | Evaluasi Appendix 2 (`--arsip`, `--menit-manual`, `--simpan`) |
| `scripts/statistik_pasal.py` | Statistik pasal dari arsip — bukti untuk verifikasi pasal |
| `scripts/kirim_riwayat.py` + `spike_mops.py` → `parse_mops.py` → `fetch_details.py` | Riwayat MOPS dari laptop Taiwan ke server |
| `docs/diagram-alur.md`, `docs/diagram/` | Diagram alur, flowchart agent, flowchart pengecekan (**perlu diperbarui ke state baru**) |

## 5. Temuan penting (dari data dan server asli)

1. **Gemini belum pernah jalan di server.** Kunci terbaca, tapi `gemini-2.5-flash`
   → HTTP 404. Sudah ditambal (pilih model flash yang tersedia), **belum diverifikasi
   setelah deploy**.
2. **OpenAPI pengumuman tertunda ±1 hari** (berisi pengumuman hari sebelumnya). Untuk
   real-time perlu relay laptop Taiwan → `/api/impor` (rencana setelah 13 Nov).
3. **Satuan (仟元) hanya ada di label** dan **sub-butir (1)(2)(3)** menyimpan angka
   penting. Pengurai sudah diperbaiki (10 Nov).
4. **Label di `LABEL_SAH` tidak cocok dengan pengumuman asli** (mis. `交易金額` tidak
   ada; aslinya `交易單位數量、每單位價格及交易總金額`, `迄事實發生日止背書保證餘額(仟元)`).
5. **Daftar pasal salah sasaran:** pasal 31 (laporan kuartal, ±31% pengumuman) dilewati;
   pasal 11 ternyata perubahan modal; pasal 22/23 bukan utang perusahaan; pasal 2 tidak
   pernah muncul. Draf: [`pemetaan-pasal.md`](./pemetaan-pasal.md).
6. **FinMind:** laba rugi per kuartal tunggal, **arus kas kumulatif sejak awal tahun**,
   neraca posisi. Dicek: EPS TTM × PER cocok dengan PER bursa; CFO 2025 = berkas 2330.
7. Watchlist server sempat berisi kode `1000` (tidak ada); kini kode yang tidak
   diperdagangkan ditolak.

## 6. Status rencana (lihat ID di `rencana-finalis.md`)

| ID | Status |
|---|---|
| 0 Model pengganti 404 | ✅ Kode selesai · ⏳ verifikasi di server (`panggilan_model > 0`) |
| A1 State + review | ✅ Selesai, teruji |
| A2 Triase keyakinan + 👍/👎 → ambang | ✅ Selesai, teruji (halaman `/ambang`, kartu triase di peringatan) |
| B1 Draf pasal | ✅ Draf · ⏳ **verifikasi Ferry & Patrice**, lalu pasang ke `screen.py` + `LABEL_SAH` + jalur "laporan" (31) dan "sinyal risiko" (22/23/1/3/40) |
| B2 DCF otomatis semua emiten | ✅ Antigravity (`app/valuasi_otomatis.py`), ditinjau Claude 10 Nov. **Catatan:** `current_portion_lt_debt` = 0 di otomatis (FinMind menggabungkannya ke OtherCurrentLiabilities) → utang 2330 kurang 13%; beta jatuh ke 1,0 bila Yahoo menolak (HTTP 429 dari sesi cloud). Pasal 31 → hitung ulang: menunggu B1b |
| B3 Sitasi MOPS + uji dari laptop | ⬜ |
| C1 Chatbot | ⬜ (versi awal 13 Nov) |
| D1 Kandidat gold set | ✅ `/ekspor/kandidat-gold.csv` |
| D2 Gold set + baseline menit | ⏳ Ferry & Patrice |
| D3 Set uji serangan | ✅ Antigravity (`scripts/uji_serangan.py`, `docs/laporan-serangan.md`): 72 skenario, **0 angka penyerang terbit**; diulang Claude. Celah cek satuan yang dilaporkannya sudah ditutup (`cek.satuan.beda`) |
| D4–D5 Evaluasi lengkap + laporan | ⬜ |
| E1 README finalis | ⬜ |
| E2 Deck, video, formulir | ⏳ Afinzaki + tim |

Juga sudah ada sebelumnya: halaman saham ala Stockbit (Ringkasan, Stream, Key Stats,
Financials, Valuation, Profile), menu samping berisi watchlist, ringkasan analisis
dengan profil risiko, cache jawaban model, impor riwayat, Docker/Dokploy, tiga bahasa.

**Pembagian berkas Claude ↔ Antigravity** (keduanya di `main`): Antigravity memiliki
`app/valuasi_otomatis.py`, `scripts/valuasi_otomatis.py`, `scripts/uji_serangan.py`,
`tests/test_valuasi_otomatis.py`, `tests/test_serangan.py`, blok tab Valuation, dan
menambah kunci i18n di **awal** `_T`. Claude memegang `app/agent/`, `app/pasar.py`,
`app/umpan_balik.py`, `app/review.py`, `tests/test_agent.py`, dan menambah kunci i18n
di **akhir** `_T`. Rinciannya di `prompt-antigravity.md`.

## 7. Menunggu orang lain

- **Afinzaki:** deploy ulang; cek jejak audit `panggilan_model > 0`; kirim
  `pemetaan-pasal.md` + tautan kandidat gold ke Ferry & Patrice; tarik riwayat MOPS
  dari laptop; uji tautan MOPS (setelah B3); deck/video/formulir.
- **Ferry & Patrice:** jawab 7 pertanyaan di `pemetaan-pasal.md` (Rabu pagi); label
  gold set (Kamis siang); baseline menit manual; verifikasi `AMBANG` di
  `app/ringkasan.py`; cek terjemahan 中文 di `app/i18n.py`.
- **Belum dijawab pengguna:** format test case / gold answers resmi dari panitia; cara
  menyerahkan repo privat ke juri; field liaison.

## 8. Konvensi teknis

- Setiap teks tampil → kunci di `app/i18n.py` (3 bahasa, placeholder sama). Pesan agent
  disimpan sebagai kode + parameter (`i18n.pesan`), diterjemahkan saat tampil (`tr`).
- Model **tidak pernah** menghitung atau menilai dirinya sendiri: angka diperiksa kode.
- Tidak ada kunci API atau data pribadi di repo; `發言人` dkk. dibuang saat menarik
  dan sekali lagi saat impor.
- Tes tidak boleh menyentuh jaringan; patch `pasar._ambil_json`/`_finmind` atau
  arahkan `CACHE_DIR` ke folder sementara.
- Setiap commit diakhiri baris atribusi Claude seperti commit sebelumnya.
