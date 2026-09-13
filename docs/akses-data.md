# Teknik Akses Data: MOPS / TWSE / TPEx

Catatan teknis untuk uji 72 jam (Fase 0). Jalankan `python3 scripts/probe_sources.py`
dari jaringan kampus untuk memastikan sumber mana yang bisa diakses.

---

## Temuan penting sebelum mulai

**TWSE, TPEx, dan MOPS memblokir IP luar Taiwan dan IP datacenter — dengan HTTP 200.**

Halaman blokirnya berisi teks "FOR SECURITY REASONS, THIS PAGE CAN NOT BE ACCESSED"
tapi status kodenya tetap 200. Pipeline yang hanya memeriksa `response.status_code == 200`
akan mencatatnya sebagai sukses dan menyimpan HTML sampah ke database.

Dua konsekuensi:

1. **Jalankan dari jaringan kampus di Taiwan.** Kalau nanti deploy ke cloud (AWS/GCP),
   ini akan gagal lagi — rencanakan sejak awal.
2. **Validasi bentuk respons, bukan status code.** Setiap fetcher wajib memeriksa bahwa
   hasilnya benar-benar JSON/tabel yang diharapkan. Ini juga bahan bagus untuk halaman
   *failure handling* di deck (halaman 7 Appendix 1).

---

## Tiga lapis sumber

### Lapis 1 — OpenAPI resmi (paling bersih, pakai ini dulu)

| Sumber | Base URL | Bentuk |
|---|---|---|
| TWSE | `https://openapi.twse.com.tw/v1` | REST JSON, tanpa autentikasi |
| TPEx | `https://www.tpex.org.tw/openapi/v1` | REST JSON, tanpa autentikasi |

Daftar endpoint lengkap ada di `/swagger.json` masing-masing. Cakupan: harga harian,
valuasi (PER/PBR/yield), perdagangan institusional, pendapatan bulanan, indeks, dan
sebagian data laporan keuangan.

Catatan lapangan:
- Endpoint lawas memakai **tanggal kalender ROC (民國)** — tahun 2026 = tahun 115. Wajib dikonversi.
- Beri jeda antar-request (0,5–1 detik). Tidak ada dokumentasi rate limit resmi, jadi bersikap sopan.
- Beberapa endpoint mengembalikan CSV walau diminta JSON. Periksa `Content-Type`.

### Lapis 2 — MOPS (sumber pengungkapan sebenarnya, tidak punya REST API)

MOPS adalah form-POST yang mengembalikan tabel HTML, bukan API. Ini sumber utama untuk
**重大訊息 (pengumuman kejadian material)** — inti dari agen pemantau watchlist.

Domain (ketiganya melayani isi yang sama, berguna sebagai fallback):
- `mops.twse.com.tw` — utama
- `mopsov.twse.com.tw` — cadangan
- `mopsc.twse.com.tw` — versi baru

Endpoint yang relevan:

| Path | Isi |
|---|---|
| `/mops/web/ajax_t51sb10` | 重大訊息 — pengumuman kejadian material |
| `/mops/web/ajax_t163sb04` | 綜合損益彙總表 — ringkasan laba rugi komprehensif |
| `/mops/web/ezsearch` | 公告快易查 — pencarian cepat pengumuman |

Teknik: POST `application/x-www-form-urlencoded` dengan parameter seperti
`step`, `firstin`, `TYPEK` (`sii` = listed, `otc` = OTC), `year` (tahun ROC), `season`.
Lalu parse tabelnya dengan `pandas.read_html()` atau BeautifulSoup.

Jebakan yang sering muncul:
- Struktur tabel berubah antar jenis laporan — jangan asumsikan indeks kolom tetap.
- Encoding campur Big5/UTF-8 di data lama.
- Rate limit agresif. Beri jeda 1–3 detik dan siapkan retry dengan backoff.
- Materi investor conference berupa **PDF**, butuh ekstraksi terpisah.

### Lapis 3 — Agregator (untuk kecepatan, bukan pengganti sitasi)

[FinMind](https://finmind.github.io/) — gratis, sumbernya dari MOPS, tanpa perlu token
(300 request/jam; 600 dengan token gratis). Terverifikasi bisa diakses bahkan dari luar Taiwan.

```python
from FinMind.data import DataLoader
api = DataLoader()
api.taiwan_stock_financial_statement(stock_id="2330", start_date="2026-01-01")
```

**Dua catatan aturan yang mengikat:**

1. Agregator adalah **resource pihak ketiga** → wajib diungkap di formulir deklarasi dan
   lisensinya dipatuhi (Pasal 13.4).
2. Deskripsi tantangan meminta basis utamanya informasi publik yang **bisa ditelusuri**.
   Jadi boleh memakai agregator untuk kecepatan, tapi **sitasi yang ditampilkan ke pengguna
   harus menunjuk ke URL MOPS/TWSE aslinya**, bukan ke endpoint agregator.

Strategi yang aman: agregator sebagai jalur cepat dan fallback, MOPS sebagai sumber sitasi.

---

## Teknik khusus untuk agen pemantau

1. **Deteksi perubahan lewat snapshot + diff.** Tarik daftar 重大訊息 secara berkala, hash tiap
   entri, bandingkan dengan snapshot sebelumnya. Yang baru itulah pemicu agent. Jauh lebih
   murah daripada memproses ulang semuanya.
2. **Simpan URL sumber + timestamp pengambilan di setiap dokumen.** Ini yang membuat
   *traceable* bisa dibuktikan, dan tanpa ini sitasi tidak bisa diverifikasi juri.
3. **Pisahkan angka ke penyimpanan terstruktur.** Fondasi verifier: setiap angka di output
   dicocokkan ke penyimpanan ini. Tidak cocok → tolak dan eskalasi ke manusia.
4. **Cache agresif.** Menurunkan biaya API — dan biaya adalah salah satu metrik wajib
   Appendix 2 yang harus dilaporkan di final.
5. **Catat setiap kegagalan fetch sebagai event.** Ini sekaligus jadi bahan *operation trace*
   yang wajib disertakan di final, jadi jangan dibuang ke `/dev/null`.

---

## Sumber

- [TWSE OpenAPI](https://openapi.twse.com.tw/)
- [TPEx OpenAPI](https://www.tpex.org.tw/openapi/)
- [公開資訊觀測站 MOPS](https://mops.twse.com.tw/mops/web/index)
- [FinMind](https://github.com/FinMind/FinMind)
- [政府資料開放平臺](https://data.gov.tw/)
