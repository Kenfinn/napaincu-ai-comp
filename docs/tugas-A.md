# Tugas A — Agent & Data (28 Sep – 8 Okt)

Turunan dari [`rencana-kerja.md`](./rencana-kerja.md) untuk jalur A. Catatan teknis sumber data
ada di [`akses-data.md`](./akses-data.md).

**Definisi selesai 8 Okt:** 1 emiten → 1 jenis kejadian → 1 alert bersitasi, jalan ujung ke ujung,
bisa dijalankan ulang di depan orang lain dan direkam untuk video.

**Status per 28 Sep:** status mahasiswa ✅ · pendaftaran tim ✅ · briefing ditinjau ✅ (tidak ada
perubahan) · **uji 72 jam belum** → itu tugas pertama.

---

## 0. Uji 72 jam — go / no-go (28 – 30 Sep) ⛔ pemblokir

Semua tugas di bawahnya menunggu keputusan ini.

- [ ] Jalankan `python3 scripts/probe_sources.py --json > probe-hasil.json` **dari jaringan kampus
      di Taiwan** (dari cloud/luar Taiwan pasti terblokir, jadi hasilnya tidak berarti)
- [ ] Pilih 5 emiten uji, mis. 2330, 2317, 2454, 2412, 2881
- [ ] Tarik 20 pengumuman 重大訊息 (MOPS `ajax_t51sb10`) untuk 5 emiten itu
- [ ] Parse jadi baris: kode saham, tanggal, judul, isi, URL sumber
- [ ] Uji terjemahan zh-TW → ID/EN pada 5 pengumuman yang memuat angka; cek manual apakah angka
      dan istilah akuntansinya tetap benar
- [ ] Tulis keputusan (1 paragraf) di akhir dokumen ini

| Hasil | Keputusan |
|---|---|
| MOPS bisa ditarik & diparse, terjemahan angka aman | **Go** — lanjut ke langkah 1 |
| MOPS terblokir tapi FinMind/OpenAPI jalan | Go dengan FinMind sebagai jalur ambil, **sitasi tetap ke URL MOPS** |
| Tidak ada yang jalan dalam 3 hari | **No-go** — bahas pindah ke Ai3 (GovAid Copilot) dengan tim |

## 1. Evidence layer minimal (30 Sep – 1 Okt)

- [ ] Kunci jalur demo: **1 emiten + 1 jenis kejadian** (mis. 2330 + pengumuman laba/pendapatan)
- [ ] Fetcher MOPS yang **memvalidasi bentuk respons**, bukan status code (halaman blokir = HTTP 200)
- [ ] Retry dengan backoff + jeda 1–3 detik antar-request
- [ ] Simpan dokumen: `stock_id`, `tanggal`, `judul`, `isi_asli`, `url_sumber`, `fetched_at`, `hash`
- [ ] Penyimpanan angka terstruktur terpisah (SQLite cukup) dari TWSE OpenAPI / FinMind —
      konversi tanggal ROC (115 = 2026)
- [ ] Setiap kegagalan fetch dicatat sebagai event, jangan dibuang

## 2. Deteksi kejadian (1 – 2 Okt)

- [ ] Snapshot daftar 重大訊息 → hash tiap entri → diff dengan snapshot sebelumnya
- [ ] Entri baru = pemicu agent

## 3. Profil & relevansi (2 – 3 Okt)

- [ ] `watchlist.json` + `profil_risiko.json` untuk satu investor contoh
- [ ] Penilaian relevansi kejadian terhadap profil → skor + alasan singkat
- [ ] Ambang relevansi sebagai parameter, **bukan hard-code** (dipakai lagi di langkah 7)

## 4. Susun alert bersitasi (3 – 5 Okt)

- [ ] LLM menyusun alert singkat dari dokumen sumber (termasuk terjemahan)
- [ ] Tiap klaim menunjuk ke URL MOPS/TWSE asli, bukan endpoint agregator
- [ ] Tidak ada rekomendasi beli/jual, prediksi harga, atau eksekusi order

## 5. Verifier (5 – 6 Okt)

- [ ] Ekstrak semua angka dari alert hasil generasi
- [ ] Cocokkan tiap angka ke penyimpanan terstruktur
- [ ] Tidak cocok → alert **ditolak** dan masuk antrean eskalasi manusia
- [ ] Siapkan satu kasus gagal yang sengaja dibuat (angka salah) untuk demo safety

## 6. Operation trace (6 – 7 Okt)

- [ ] Log tiap langkah: rencana, tool yang dipanggil, input/output ringkas, retry, hasil verifier,
      latensi, biaya token
- [ ] Format yang bisa dibaca manusia (JSONL + satu tampilan ringkas) — ini wajib di final

## 7. Ujung ke ujung + rekaman (7 – 8 Okt)

- [ ] Satu perintah menjalankan seluruh alur dari data sampai alert terkirim
- [ ] Jalankan ulang ≥3 kali tanpa intervensi
- [ ] Serahkan rekaman kasar ke C
- [ ] *(Opsional)* reaksi 👍/👎 menyetel ambang relevansi — versi paling sederhana, untuk cerita
      *behavioral feedback → continuous optimization* di deck

## Jangan dikerjakan sekarang

UI rapi · banyak emiten · akurasi tinggi · antarmuka tanya-jawab (itu Fase 5). Belum dinilai di
penyisihan.

## Serahan ke tim

| Kapan | Ke | Apa |
|---|---|---|
| 30 Sep | Semua | Keputusan go / no-go |
| 6 Okt | C | Diagram arsitektur final + contoh alert untuk deck |
| 8 Okt | C | Rekaman demo kasar |
| 8 Okt | B | Format gold set yang bisa langsung dijalankan di Fase 3 |

---

## Keputusan uji 72 jam

_(isi setelah langkah 0 selesai)_
