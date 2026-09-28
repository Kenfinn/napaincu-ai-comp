# Tugas A — Agent & Data (28 Sep – 8 Okt)

Turunan dari [`rencana-kerja.md`](./rencana-kerja.md) untuk jalur A. Catatan teknis sumber data
ada di [`akses-data.md`](./akses-data.md).

**Definisi selesai 8 Okt:** 1 emiten → 1 jenis kejadian → 1 alert bersitasi, jalan ujung ke ujung,
bisa dijalankan ulang di depan orang lain dan direkam untuk video.

**Status per 28 Sep:** status mahasiswa ✅ · pendaftaran tim ✅ · briefing ditinjau ✅ · **uji 72 jam belum**.

## Cara bagi kerja

- **Kamu** = yang butuh jaringan kampus Taiwan, keputusan, penilaian manusia, kunci API, dan
  rekaman. Claude tidak bisa mengakses MOPS/TWSE dari cloud (terblokir di luar Taiwan).
- **Claude** = menulis kode, skema data, tes, dan dokumentasi. Claude bekerja memakai
  **data mentah yang kamu tarik dari kampus lalu commit ke repo** — itu jembatannya.

---

## ▶️ Mulai sekarang (28 – 29 Sep)

| # | Siapa | Tugas | Selesai kalau |
|---|---|---|---|
| 1 | Claude | Tulis skrip uji 72 jam: tarik 20 pengumuman 重大訊息 untuk 5 emiten, simpan HTML mentah + hasil parse | Skrip ada di `scripts/`, bisa dijalankan satu perintah |
| 2 | Kamu | Siapkan API key LLM (disimpan di `.env` lokal, **jangan di-commit**) | Key jalan di laptopmu |
| 3 | Kamu | Konfirmasi 5 emiten uji (usulan: 2330, 2317, 2454, 2412, 2881) | Balas "ok" atau ganti |
| 4 | Kamu | Jadwalkan waktu di jaringan kampus besok | — |

## Uji 72 jam (29 – 30 Sep) ⛔ pemblokir

| # | Siapa | Tugas |
|---|---|---|
| 5 | Kamu | Di jaringan kampus: jalankan `probe_sources.py --json` dan skrip uji 72 jam |
| 6 | Kamu | Commit & push hasil mentahnya ke `data/raw/` (bahan kerja Claude) |
| 7 | Claude | Parser dari data mentah + skrip uji terjemahan zh-TW → ID/EN pada 5 pengumuman berangka |
| 8 | Kamu | Cek manual hasil terjemahan: angka & istilah akuntansi benar? |
| 9 | Kamu | **Putuskan go / no-go**, kabari tim (30 Sep) |

| Hasil | Keputusan |
|---|---|
| MOPS bisa ditarik & diparse, terjemahan angka aman | **Go** |
| MOPS terblokir tapi FinMind/OpenAPI jalan | Go, FinMind untuk ambil data, **sitasi tetap ke URL MOPS** |
| Tidak ada yang jalan | **No-go** → bahas pindah ke Ai3 (GovAid Copilot) |

## Setelah Go — alur tipis (30 Sep – 8 Okt)

| Tanggal | Claude kerjakan | Kamu kerjakan |
|---|---|---|
| 30 Sep | — | Kunci jalur demo: 1 emiten + 1 jenis kejadian |
| 30 Sep – 1 Okt | Evidence layer: fetcher dengan validasi bentuk respons + retry, skema SQLite (dokumen + angka terstruktur), konversi tanggal ROC | Jalankan fetcher di kampus, push hasilnya |
| 1 – 2 Okt | Deteksi kejadian baru (snapshot + hash + diff) | — |
| 2 – 3 Okt | `watchlist.json`, `profil_risiko.json`, skor relevansi dengan ambang sebagai parameter | Review: profil investor contohnya masuk akal? (cocokkan dengan temuan wawancara B) |
| 3 – 5 Okt | Penyusun alert bersitasi via LLM | Review 3–5 contoh alert: jelas, tidak berbau saran beli/jual? |
| 5 – 6 Okt | Verifier angka + satu kasus gagal sengaja untuk demo safety | Coba "rusak" sendiri: apakah verifier menangkapnya? |
| 6 – 7 Okt | Operation trace (JSONL + tampilan ringkas: langkah, tool, retry, latensi, biaya) | — |
| 7 – 8 Okt | Runner satu perintah + README singkat cara menjalankan | Jalankan ujung ke ujung ≥3 kali, **rekam**, serahkan ke C |
| opsional | Reaksi 👍/👎 menyetel ambang relevansi | Putuskan apakah masuk video |

## Serahan ke tim (tanggung jawabmu)

| Kapan | Ke | Apa |
|---|---|---|
| 30 Sep | Semua | Keputusan go / no-go |
| 6 Okt | C | Diagram arsitektur + contoh alert untuk deck (Claude bisa bantu siapkan) |
| 8 Okt | C | Rekaman demo kasar |
| 8 Okt | B | Format gold set yang bisa langsung dijalankan di Fase 3 |

## Jangan dikerjakan sekarang

UI rapi · banyak emiten · akurasi tinggi · antarmuka tanya-jawab (Fase 5). Belum dinilai di penyisihan.

---

## Keputusan uji 72 jam

_(isi setelah langkah 9)_
