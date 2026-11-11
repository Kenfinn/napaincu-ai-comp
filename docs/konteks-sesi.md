# Konteks kerja: BACA INI DULU

Pegangan untuk melanjutkan tanpa riwayat percakapan (sesi Claude berikutnya, Antigravity,
dan tim). Per **11 Nov 2026 pagi**. Status harian dan daftar kerja ada di
[`rencana-dan-status.md`](./rencana-dan-status.md); berkas ini menjelaskan "kenapa" dan "di mana".

## 1. Produk, tim, tenggat

- **FEAF · Agentic AI Investment Assistant**, NAPAI AAIC 2026, track SYSTEX. **Lolos finalis.**
- Agent memantau pengumuman material (重大訊息) emiten TWSE/TPEx, mengurai angka beserta
  kalimat sumbernya, memeriksanya secara deterministik, lalu menerbitkan peringatan, sinyal
  risiko, atau skenario valuasi, atau menahannya untuk manusia. Ada halaman saham (Ringkasan,
  Stream, Key Stats, Financials, Valuation, Profile) dan chatbot "Tanya FEAF" (`/tanya`).
- Tim: **Afinzaki** (teknis, pemilik server dan pengguna yang bicara dengan Claude),
  **Ferry** dan **Patrice** (keuangan). Antigravity dipakai sebagai agen kedua lewat prompt.
- **Paket finalis: Jumat 13 Nov 23:59.** Demo final: 21 Nov.
- Penilaian final: Task completion & stability 25%, Field impact 20%, Agentic depth 20%,
  Safety 15%, Innovation 10%, Demo & Q&A 10%. Aturan: [`aaic-2026-ringkasan.md`](./aaic-2026-ringkasan.md).

## 2. Keputusan yang dikunci (jangan diubah tanpa tanya)

| Hal | Keputusan |
|---|---|
| Branch | Kerja langsung di `main` sampai pengguna meminta branch baru |
| Bahasa | Tiga bahasa: English (bawaan), 繁體中文, Bahasa Indonesia. Kunci baru di `app/teks/<nama>.py` (dimuat otomatis), bukan di `app/i18n.py` |
| Warna | Merah = naik, hijau = turun |
| Saran | Tanpa label beli/jual; penafian di semua halaman analisis (izin FSC) |
| Review manusia | Setujui hanya kasus ragu. Angka/kutipan karangan hanya bisa diarsipkan. Setuju "keyakinan rendah" = lanjut ke pemeriksa, bukan terbit |
| 👍/👎 | Satu ambang per server, per pasal (0,40–0,90) |
| Beta | Dari harga harian resmi TWSE/TPEx vs TAIEX, 2 tahun mingguan; data kurang → 1,0 bertanda |
| DCF | **Berbasis kas** (Patrice): pengumuman tanpa pergerakan kas tidak mengubah DCF. Pasal 20 → skenario "bila terealisasi"; pasal 31 memicu pembangunan ulang valuasi |
| Ambang sinyal | Ikut profil risiko (konservatif/moderat/agresif), di `app/ambang_profil.py`. Profil hanya mengubah label; antrean review memakai moderat |
| Data ke Gemini | Hanya data publik. Tidak ada data SYSTEX/mitra |
| README | Diperbarui paling akhir |
| Gaya kerja | Jawab pengguna dalam Bahasa Indonesia, singkat; tanya untuk keputusan penting; QA sendiri sebelum melapor; dokumen untuk manusia memakai gaya humanizer (tanpa tanda pisah, tanpa bold berlebihan) |

## 3. Lingkungan

| Hal | Isi |
|---|---|
| Repo | `Kenfinn/napaincu-ai-comp`, branch `main` |
| Server | Dokploy, **https://feaf.afinzaki.my.id**, port 8000, volume bernama **`feaf-data` → `/data`** (dipasang 11 Nov; sebelumnya volume tanpa nama, data hilang tiap deploy) |
| Env server | `SENTINEL_KODE_AKSES`, `SENTINEL_TARIK_OTOMATIS_DETIK=600`, `SENTINEL_SERTAKAN_CONTOH=0`, `GEMINI_API_KEY`, **`SENTINEL_MODEL=gemini-3.6-flash`**, **`SENTINEL_MODEL_CADANGAN=gemini-3.5-flash,gemini-3.8-flash`**, opsional `SENTINEL_KUNCI_BACA`, `SENTINEL_PROSES_SEMUA`, `SENTINEL_MODEL_MAKS_PER_JALAN`, `FINMIND_TOKEN` |
| Gemini | Kunci dari AI Studio. `gemini-2.5-flash` tercantum di ListModels tapi 404; 3.7/3.8/flash-latest sering 503; 3.5 dan 3.6 jalan (tes 11 Nov). Langganan AI Pro tidak menambah kuota API, hanya kredit Cloud US$10/bulan |
| Deploy | Push ke `main`, tekan Deploy di Dokploy. Panduan: [`deploy-dokploy.md`](./deploy-dokploy.md) |
| Tes | `python3 -m unittest discover -s tests` → **178 tes**, tanpa jaringan |
| Evaluasi | `scripts/evaluasi.py --operasional --arsip-dir <folder arsip>`, `--chat`, mode gold |
| Sesi cloud Claude | Bisa: OpenAPI TWSE/TPEx, situs TWSE/TPEx (harga harian), FinMind, Gemini tidak (tanpa kunci). Tidak bisa: MOPS |
| Laptop Taiwan | Jalan ke MOPS: riwayat pengumuman ([`tarik-riwayat.md`](./tarik-riwayat.md)), uji tautan MOPS |

## 4. Peta kode

| Berkas | Isi |
|---|---|
| `app/main.py` | Rute web/API, pemantau (tarik → proses → valuasi → proses), hasil awal tanpa model saat start, kunci baca, `/review`, `/ambang`, `/saham/{kode}` |
| `app/tarik.py` | Penarik OpenAPI semua emiten, watchlist, pengurai butir, entitas HTML/radikal Kangxi, impor riwayat |
| `app/agent/pipeline.py` | Orkestrasi + jejak; jalur valuasi (penyari → triase → pemeriksa → DCF → skenario) dan jalur sinyal |
| `app/agent/screen.py` | Pasal → jalur (20 valuasi; 22/23 risiko; 11/35 modal; 31 laporan; 1/3/40 berat) |
| `app/agent/sinyal.py` | Pengurai sinyal deterministik (penjaminan per penerima, modal, laporan, berat) |
| `app/ambang_profil.py` | Ambang sinyal per profil risiko |
| `app/agent/extract.py` | Penyari (Gemini / penalar aturan), `LABEL_SAH` |
| `app/agent/triase.py`, `app/umpan_balik.py` | Skor keyakinan; ambang dari 👍/👎 |
| `app/agent/verify.py` | 7 cek + sirkularitas; satuan wajib tertulis di sumber |
| `app/agent/llm.py` | Gemini REST, cache, model 404 dicoret, cadangan saat sibuk, pemutus per jalan |
| `app/review.py` | Keputusan review per jenis penahanan |
| `app/valuasi_otomatis.py`, `app/harga_resmi.py`, `app/sitasi.py` | DCF otomatis (cache berversi `VERSI_SKEMA`), harga harian resmi untuk beta, tautan MOPS |
| `app/pasar.py`, `app/ringkasan.py` | Data pasar & laporan (FinMind), tab Ringkasan |
| `app/chat.py` | Tanya FEAF: penjaga, function calling ke 7 alat, pemeriksa angka, jejak |
| `scripts/evaluasi.py`, `scripts/uji_serangan.py` | Evaluasi Appendix 2, set uji serangan |

## 5. Temuan penting

1. Sebelum B1, data asli tidak menghasilkan satu pun peringatan. Sesudah B1: 241 terbit dari 581.
2. OpenAPI pengumuman tertunda sekitar 1 hari. Real-time butuh relay laptop Taiwan (backlog).
3. Satuan (仟元) sering hanya di label; total transaksi pasal 20 ada di butir yang juga memuat
   jumlah unit; penerima penjaminan ditulis berurutan dalam satu butir.
4. Emiten yang belum di-cache butuh ±2 menit untuk tab Valuation (beta: 25 bulan harga harian,
   jeda 2 detik, TWSE membalas 307 bila terlalu sering). Belum diperbaiki: item kesiapan demo.
5. Pasal 1 bisa memuat nama orang (公司名稱(或負責人姓名)); tidak diambil.
6. Cache profil TPEx sempat menyimpan nama pejabat dan email (diperbaiki 10 Nov, perlu ditulis
   di formulir self-assessment).

## 6. Pembagian kerja dengan Antigravity

Antigravity menyelesaikan putaran 2 lewat [`prompt-antigravity-berurutan.md`](./prompt-antigravity-berurutan.md);
laporannya [`laporan-antigravity-2.md`](./laporan-antigravity-2.md) dengan tinjauan Claude di akhir.
Untuk putaran berikutnya, tulis prompt baru dengan kepemilikan berkas yang jelas dan pemeriksa
per item (pola yang sama), lalu tinjau hasilnya terhadap kode sebelum deploy.

## 7. Konvensi teknis

- Model tidak pernah menghitung atau menilai dirinya sendiri; angka diperiksa kode.
- Tidak ada kunci API atau data pribadi di repo.
- Tes tidak boleh menyentuh jaringan; patch `pasar._ambil_json`/`_finmind` atau arahkan cache ke folder sementara.
- Setiap commit diakhiri baris atribusi Claude seperti commit sebelumnya.
