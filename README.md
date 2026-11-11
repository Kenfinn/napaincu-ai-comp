# FEAF · Agentic AI Investment Assistant

Agent pemantau pengumuman resmi bursa Taiwan (MOPS 重大訊息) yang menghitung ulang
valuasi saat sebuah dokumen mengubah angka, dan **menolak menerbitkan peringatan**
ketika angkanya tidak bisa ditelusuri kembali ke dokumen sumbernya.

Dibangun untuk NAPAI Agentic AI Innovation Competition 2026, track SYSTEX —
*Investment Intelligence & AI-Powered Stock Selection Agent*.

> **Bukan alat perdagangan.** Tidak ada jalur ke broker dan tidak ada eksekusi order.
> Agent menyaring, menjelaskan, dan menyitasi; manusia yang memutuskan.

---

## Run locally · 本機執行 · Menjalankan di lokal

### English

Requirements: Python 3.12 or newer, Git, internet access (TWSE/TPEx OpenAPI). No database.

```bash
git clone https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. On the first run the feed shows clearly marked sample
filings. Press **Check now** (or add a stock on **Watchlist**) to pull today's real
filings from TWSE/TPEx. The interface defaults to English; switch to 中文 or ID in the left menu.

Optional settings, set before `uvicorn`:

```bash
export GEMINI_API_KEY=...                 # without it the rule-based reasoner is used
export SENTINEL_MODEL=gemini-3.6-flash    # default
export SENTINEL_TARIK_OTOMATIS_DETIK=600  # pull new filings every 10 minutes
export SENTINEL_KODE_AKSES=...            # require an access code for actions
```

On Windows PowerShell use `$env:GEMINI_API_KEY="..."` instead of `export`.
Run the tests with `python -m unittest discover -s tests` (no network needed).

### 繁體中文

需求：Python 3.12 以上、Git、可連線至證交所與櫃買中心 OpenAPI。不需要資料庫。

```bash
git clone https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
python3 -m venv .venv
source .venv/bin/activate          # Windows：.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

開啟 <http://127.0.0.1:8000>。第一次執行時，動態頁會顯示標示為「範例」的公告。按下
**立即檢查**（或在**自選股**加入股票）即可從證交所與櫃買中心取得今日的真實重大訊息。
介面預設為英文，可在左側選單切換為「中文」。

選用設定（在執行 `uvicorn` 前設定）：

```bash
export GEMINI_API_KEY=...                 # 未設定時改用規則推理
export SENTINEL_MODEL=gemini-3.6-flash    # 預設模型
export SENTINEL_TARIK_OTOMATIS_DETIK=600  # 每 10 分鐘自動抓取新公告
export SENTINEL_KODE_AKSES=...            # 操作需輸入存取碼
```

Windows PowerShell 請改用 `$env:GEMINI_API_KEY="..."`。
執行測試：`python -m unittest discover -s tests`（不需網路）。

### Bahasa Indonesia

Kebutuhan: Python 3.12 atau lebih baru, Git, akses internet ke OpenAPI TWSE/TPEx. Tanpa database.

```bash
git clone https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Buka <http://127.0.0.1:8000>. Saat pertama dijalankan, feed menampilkan pengumuman contoh
yang diberi tanda jelas. Tekan **Periksa sekarang** (atau tambah saham di **Watchlist**) untuk
menarik pengumuman asli hari ini dari TWSE/TPEx. Tampilan bawaan berbahasa Inggris; ganti
ke 中文 atau ID di menu kiri.

Pengaturan opsional, diisi sebelum `uvicorn`:

```bash
export GEMINI_API_KEY=...                 # tanpa ini dipakai penalar aturan
export SENTINEL_MODEL=gemini-3.6-flash    # bawaan
export SENTINEL_TARIK_OTOMATIS_DETIK=600  # tarik pengumuman baru tiap 10 menit
export SENTINEL_KODE_AKSES=...            # aksi butuh kode akses
```

Di Windows PowerShell pakai `$env:GEMINI_API_KEY="..."`, bukan `export`.
Tes: `python -m unittest discover -s tests` (tanpa jaringan).

### Menarik pengumuman asli (dari jaringan mana pun)

Buka halaman **Watchlist**, tambah kode saham, lalu tekan **Periksa sekarang**. Atau lewat terminal:

```bash
python3 scripts/tarik.py                 # tarik untuk watchlist di data/watchlist.json
python3 scripts/tarik.py --ulang 600     # periksa tiap 10 menit sampai Ctrl+C
```

Sumbernya OpenAPI resmi TWSE (`t187ap04_L`) dan TPEx (`mopsfin_t187ap04_O`), yang memuat
isi lengkap pengumuman material hari berjalan dan **tidak** diblokir di luar Taiwan.
Endpoint itu tidak menyimpan riwayat, jadi setiap tarikan digabung ke
`data/parsed/details.json` tanpa duplikat. Riwayat yang lebih lama hanya bisa ditarik
dari MOPS lewat jaringan Taiwan (`scripts/spike_mops.py` → `parse_mops.py` → `fetch_details.py`).

### Deploy (Docker / Dokploy)

```bash
docker build -t feaf .
docker run -p 8000:8000 -v feaf-data:/data -e SENTINEL_TARIK_OTOMATIS_DETIK=600 feaf
```

Langkah lengkap untuk Dokploy, termasuk kode akses dan daftar uji untuk tim, ada di
[`docs/deploy-dokploy.md`](docs/deploy-dokploy.md).

### Menjalankan tes

```bash
python3 -m unittest discover -s tests -v
```

### Menjalankan evaluasi (Appendix 2)

```bash
python3 scripts/evaluasi.py --menit-manual 6
```

Membandingkan pipeline lengkap dengan "LLM tanpa pemeriksa" pada gold set di
`eval/gold.csv`, lalu mencetak angka salah yang terbit, ketepatan keputusan, tingkat
intervensi manusia, panggilan model, token, retry, dan latensi. Mode `model` ikut
dijalankan kalau `GEMINI_API_KEY` terpasang. Cara mengisi gold set ada di
[`docs/panduan-gold-set.md`](docs/panduan-gold-set.md).

---

## Arsitektur

```
Pengumuman MOPS
        │
   [0] SARINGAN 符合條款 ── deterministik, gratis ── 711 → ~30
        │
   [1] PEMILAH      model   Menyentuh input valuasi yang mana? Seberapa yakin?
   [2] PENYARI      model   Angka berapa, dari kalimat mana persis?
        │
   [3] PENGHITUNG   deterministik — dcf.compute() dua kali, sebelum vs sesudah
        │
   [4] PEMERIKSA    deterministik — tiap angka wajib ada di dokumen sumber
        │
   lolos → terbit      gagal → ditolak, alasan tercatat
```

Empat akhir yang mungkin, dan tiga di antaranya **bukan** "terbit":

| Akhir | Artinya |
|---|---|
| `dilewati` | Nomor pasal tidak menyentuh input valuasi. Tidak pernah sampai ke model. |
| `ditahan` | Tidak ada angka yang bisa ditarik lengkap dengan kalimat sumbernya. Antre ke manusia. |
| `ditolak` | Pemeriksa menggagalkan klaim. Peringatan tidak terbit, alasannya tercatat. |
| `terbit` | Lolos seluruh pemeriksaan. |

**Tahap 3 dan 4 sengaja tidak memakai model.** Di situ letak pertahanannya: angka
datang dari aritmetika, dan klaim model diuji balik ke dokumen. Model tidak pernah
menghitung, dan tidak pernah menilai dirinya sendiri.

Diagram lengkapnya: `design/AlurState.dc.html` dan `design/Arsitektur.dc.html`
(PNG-nya di `design/export/`).

### Yang diperiksa tahap 4

| Pemeriksaan | Menangkap |
|---|---|
| Label butir sah untuk input | Kutipan dari butir catatan, tempat teks pengarah biasa diselipkan |
| Kutipan ada di dokumen | Kalimat sumber yang dikarang |
| Digit angka ada di dokumen | Angka halusinasi |
| Mata uang didukung | Jumlah USD yang dikonversi diam-diam tanpa kurs |
| Satuan dikenali | Kekeliruan 仟元 / 百萬元 / 億元 — selisihnya ribuan kali |
| Besaran dalam pita 0,2–3,0× | Salah tarik butir, atau angka yang disuntikkan |
| Sirkularitas utuh | Bug aritmetika di kalkulator |

---

## Aliran data dan privasi

```
MOPS / TWSE  →  scripts/  →  data/parsed/  →  app/agent/  →  app/ (web)
                    │                              │
           data pribadi dibuang            data/traces/
```

`scripts/fetch_details.py` membuang `發言人`, `發言人職稱`, dan `發言人電話` **sebelum
apa pun disimpan**. Yang dicatat hanya *bahwa* field itu dibuang, tidak pernah isinya.
Jadi tidak ada data pribadi yang bisa sampai ke model — secara konstruksi, bukan
secara kebijakan (Pasal 14.1, minimisasi data).

Teks pengumuman diperlakukan sebagai **data yang tidak dipercaya**: isinya dikendalikan
penerbit, jadi ia masuk prompt di dalam pembatas dan instruksi sistem menyatakan bahwa
apa pun di dalamnya tidak boleh dituruti. Percobaan pengarahan dicatat di jejak audit.

---

## Environment variable

| Nama | Wajib | Default | Guna |
|---|---|---|---|
| `GEMINI_API_KEY` atau `GOOGLE_API_KEY` | tidak | — | Kunci model. Tanpa ini, penalar aturan yang dipakai |
| `SENTINEL_MODEL` | tidak | `gemini-3.6-flash` | Nama model |
| `SENTINEL_MODEL_CADANGAN` | tidak | `gemini-3.5-flash` | Model cadangan saat model utama sibuk, dipisah koma |
| `SENTINEL_PENYEDIA` | tidak | `gemini` | Penyedia model |
| `SENTINEL_TRIAGE_THRESHOLD` | tidak | `0.55` | Ambang keyakinan pemilah |
| `SENTINEL_RETRY` | tidak | `2` | Percobaan ulang sebelum turun ke penalar aturan |
| `SENTINEL_TIMEOUT` | tidak | `45` | Batas waktu panggilan model (detik) |

**Kunci hanya dibaca dari environment.** Tidak pernah ditulis ke berkas, layar, log,
maupun jejak audit — dan ada tes yang memeriksanya.

### Model dan versinya

- Model: `gemini-2.5-flash` (free tier), suhu `0` supaya hasilnya bisa diulang
- Versi prompt: konstanta `VERSI_PROMPT` di `app/agent/llm.py`
- Baseline pembanding: penalar berbasis aturan di `screen.py` / `extract.py`

**Pengungkapan free tier:** konten free tier Gemini dipakai Google untuk meningkatkan
produknya. Dapat diterima di sini karena pengumuman MOPS adalah dokumen publik *dan*
data pribadi sudah dibuang di hulu. Kalau nanti perlu menganalisis apa pun yang tidak
publik, free tier tidak boleh dipakai lagi.

---

## API

`/docs` menyajikan OpenAPI otomatis.

| Rute | Isi |
|---|---|
| `GET /` | Feed peringatan |
| `GET /peringatan/{id}` | Detail, sitasi MOPS, vonis pemeriksa |
| `GET /valuasi/{kode}` | DCF, biaya modal, sensitivitas, sumber tiap input |
| `GET /jejak/{id}` | Operation trace |
| `GET /api/peringatan` | Daftar hasil (JSON) |
| `GET /api/jejak/{id}` | Operation trace (JSON) |
| `GET /api/valuasi/{kode}` | Keluaran kalkulator DCF (JSON) |

---

## Data

Data MOPS asli hanya bisa ditarik dari jaringan Taiwan, jadi repo menyertakan empat
kasus uji di `data/fixtures/` supaya aplikasi jalan di mesin mana pun. Kalau
`data/parsed/` terisi, itu yang dipakai — lewat **kode baca yang sama persis**, supaya
bug di jalur asli tidak bersembunyi di balik jalur fixture. Layar selalu menyatakan
sumber mana yang sedang ditampilkan.

Menarik data asli (dari Taiwan):

```bash
python3 scripts/probe_sources.py      # cek keterjangkauan
python3 scripts/spike_mops.py         # tarik massal
python3 scripts/parse_mops.py         # parse jadi record + URL sitasi
python3 scripts/fetch_details.py      # ambil detail, buang data pribadi
```

Kalkulator valuasi berdiri sendiri dan bisa dijalankan tanpa aplikasi:

```bash
python3 scripts/dcf.py valuation/inputs/2330.json
python3 scripts/dcf.py valuation/inputs/2330.json --forward-g 0.03
```

Aplikasi web memanggil `compute()` dari berkas yang sama, jadi angka di layar tidak
bisa berbeda diam-diam dari kertas kerja.

---

## Keterbatasan yang diketahui

1. **Pemetaan nomor pasal masih sementara.** `KLAUSA_RELEVAN` di `app/agent/screen.py`
   adalah dugaan kerja, belum dicocokkan baris per baris dengan daftar resmi 重大訊息.
   Nomor yang salah menyaring keluar pengumuman penting, dan kegagalan seperti itu
   tidak bersuara. **Wajib diverifikasi sebelum masuk deck.**
2. **Baru satu emiten punya berkas valuasi.** Hanya TSMC (2330). Fubon (2881)
   perusahaan keuangan — DCF biasa tidak berlaku dan butuh metode lain.
3. **Enam sumber input TSMC belum lengkap.** Ditandai di layar valuasi. Angka boleh
   dihitung, belum boleh masuk deck.
4. **Tidak ada konversi mata uang.** Jumlah non-NTD ditolak, bukan dikonversi.
5. **Semantik "ganti", bukan "tambah".** Pengumuman anggaran diperlakukan sebagai
   tingkat belanja, dan hasilnya adalah skenario "bila tingkat ini berlanjut" —
   bukan ramalan.
6. **Reverse DCF tidak menghasilkan nilai intrinsik.** Yang dihasilkannya adalah
   pertumbuhan abadi yang sedang diasumsikan pasar. Nilai wajar hanya ditampilkan
   sebagai skenario dengan asumsi g yang disebutkan.

---

## Troubleshooting

| Gejala | Sebab dan tindakan |
|---|---|
| Layar menyatakan "penalar-aturan" | Tidak ada kunci API di environment. Ini sah; isi `GEMINI_API_KEY` kalau ingin jalur model |
| Penarikan MOPS balas HTTP 200 tapi isinya halaman blokir | Geo-blocking. Sumbernya hanya terjangkau dari jaringan Taiwan — validasi bentuk balasan, bukan kode statusnya |
| `render_design.js` minta `npx playwright install` | Jangan dijalankan. Nomor build Chromium yang terpasang berbeda; skrip sudah menunjuk binary yang ada lewat `PLAYWRIGHT_BROWSERS_PATH` |
| Feed kosong | `data/parsed/` dan `data/fixtures/` sama-sama kosong |
| `404` di `/valuasi/{kode}` | Belum ada `valuation/inputs/{kode}.json` |

---

## Isi repo

| Jalur | Isi |
|---|---|
| `app/` | Aplikasi web dan agent |
| `app/agent/` | Lima tahap pipeline |
| `scripts/` | Penarikan MOPS, parsing, dan kalkulator DCF |
| `valuation/inputs/` | Input DCF per emiten, lengkap dengan sumber tiap angka |
| `design/` | Delapan layar hi-fi + dua diagram wajib deck |
| `wireframe/` | Delapan wireframe beserta alasan tiap wilayah layar |
| `docs/` | Ringkasan aturan lomba, rencana kerja, catatan akses data |
| `tests/` | Test case agent — bahan deck halaman 9 dan Appendix 2 |
| `eval/` | Gold set berlabel dan hasil evaluasi |
| `data/fixtures/` | Empat kasus uji supaya aplikasi jalan di mana saja |

---

## License · 授權 · Lisensi

All rights reserved. See [`LICENSE`](LICENSE). AAIC 2026 organisers and judges may run and
inspect this repository to evaluate the entry. Third-party components and data keep their own
licences ([`docs/pengungkapan-pihak-ketiga.md`](docs/pengungkapan-pihak-ketiga.md)).

版權所有，詳見 [`LICENSE`](LICENSE)。AAIC 2026 主辦單位與評審可為評選目的執行及檢視本專案。
第三方元件與資料沿用其原授權。

Hak cipta dilindungi; lihat [`LICENSE`](LICENSE). Panitia dan juri AAIC 2026 boleh menjalankan
dan memeriksa repo ini untuk penilaian. Komponen dan data pihak ketiga tetap memakai lisensinya masing-masing.

