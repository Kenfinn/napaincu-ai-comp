# Rencana menuju paket finalis (13 Nov) dan final (21 Nov)

Disusun 10 Nov 2026. Berkas ini menggantikan Bagian 0 di `rekap.md` sebagai daftar kerja.

## Keputusan yang sudah diambil (10 Nov)

| Hal | Keputusan |
|---|---|
| Kasus HELD yang boleh disetujui manusia | **Hanya kasus ragu**: mata uang asing, belum ada model valuasi, keyakinan rendah, pasal tak terbaca. Kutipan/angka yang tidak ada di dokumen hanya bisa **diarsipkan** |
| Beta untuk DCF otomatis | **Dihitung dari harga**: return mingguan 2 tahun vs TAIEX. Data kurang → beta 1,0 dan ditandai |
| Chatbot "Tanya FEAF" | **Versi awal 13 Nov, lengkap 21 Nov** |
| Ambang dari umpan balik 👍/👎 | **Satu untuk server** (satu investor per server) |
| Kesimpulan analisis | Tanpa label beli/jual (brief hal. 9, regulasi FSC) |
| Warna | Merah = naik, hijau = turun |

## Temuan yang mengubah prioritas

1. **Gemini belum pernah jalan.** Kunci sudah terbaca, tapi setiap panggilan gagal **HTTP 404**:
   nama model `gemini-2.5-flash` tidak ditemukan untuk kunci itu.
2. **Daftar pasal salah sasaran.** Dari 371 pengumuman TWSE asli (10 Nov), pasal **31**
   (laporan keuangan kuartal) berjumlah 108 dan selama ini dilewati. Pasal 11 ternyata berisi
   pengurangan modal, saham treasuri, dan konversi obligasi, bukan belanja modal.
3. **OpenAPI pengumuman tertunda ±1 hari** (berisi pengumuman hari sebelumnya).

## Track paralel

| ID | Pekerjaan | Siapa | Bergantung pada |
|---|---|---|---|
| 0 | Model otomatis jatuh ke model *flash* yang tersedia bila 404; dicatat di jejak | Claude | — |
| 0b | Jalankan perintah daftar model di Docker Terminal Dokploy, kirim hasilnya | Afinzaki | — |
| A1 | State sesuai brief hal. 7 + antrean review manusia | Claude | — |
| A2 | Triase dengan skor keyakinan + 👍/👎 → ambang per pasal (0,40–0,90, riwayat, reset, kunci) | Claude | A1 |
| B1 | Draf pemetaan pasal dari data asli + regulasi | Claude | — |
| B1b | **Verifikasi pemetaan pasal** + ambang ringkasan (`app/ringkasan.py`, `AMBANG`) | Ferry & Patrice | B1 |
| B2 | DCF otomatis untuk semua emiten non-keuangan; pasal 31 memicu hitung ulang | Claude | — |
| B3 | Sitasi angka laporan keuangan ke halaman MOPS | Claude | — |
| B3b | Uji tautan MOPS dari laptop Taiwan; cocokkan 10 angka FinMind vs MOPS | Afinzaki | B3 |
| C1 | Chatbot "Tanya FEAF" | Claude | 0, B2, B3 |
| D1 | Ekspor kandidat gold set dari arsip mentah server (semua emiten sejak 8 Nov) | Claude | — |
| D2 | **Gold set 30–50** + baseline menit manual | Ferry & Patrice | D1, B1b |
| D3 | Set uji serangan otomatis dari pengumuman asli | Claude | — |
| D4 | Skrip evaluasi lengkap (semua metrik Appendix 2) | Claude | A1, A2 |
| D5 | Laporan evaluasi + laporan keamanan + operation trace asli dengan model | Claude | 0, D2, D3, D4 |
| E1 | README finalis | Claude | semua |
| E2 | Deck terbaru, video demo, formulir pihak ketiga & self-assessment, kebutuhan demo final | Afinzaki + tim | — |

**Jalur kritis:** 0 → B1 → B1b → D2 → D5.

## Jadwal

| | Claude | Afinzaki | Ferry & Patrice |
|---|---|---|---|
| Sel 10 | 0, A1, B1, D1 | 0b; mulai E2 | Tunggu draf B1 |
| Rab 11 | A2, B2, D3 | B3b; riwayat MOPS dari laptop | **B1b** (pagi), **D2** |
| Kam 12 | B3, D4, D5, mulai C1 | Rekam video | D2 selesai (siang) |
| Jum 13 | C1 versi awal, E1, QA akhir | **Kirim paket** | Cek isi berkas |
| 14–21 | C1 lengkap, relay real-time, perbaikan | Latihan demo ≥5× | Latihan Q&A |

## Kriteria QA (selesai = lolos semua)

| Item | Lolos bila |
|---|---|
| 0 | Jejak audit asli di server: `panggilan_model > 0`, bukan mode cadangan |
| A1 | Nama state di layar dan jejak = brief hal. 7; verifier gagal → HELD; keputusan manusia tercatat sebagai langkah terakhir |
| A2 | 👎 berulang pada satu pasal menaikkan ambangnya dan peringatan sejenis diarsipkan dengan alasan; ambang tetap di 0,40–0,90; reset berfungsi |
| B1 | Pasal 31, 20, 22/23, 10, 1 lolos saringan; pasal 12 dilewati; **disetujui Ferry/Patrice** |
| B2 | Valuasi tampil untuk ≥10 emiten acak non-keuangan; DCF otomatis 2330 mendekati berkas manual; emiten keuangan ditandai tidak berlaku |
| B3 | Setiap angka laporan keuangan punya tautan MOPS; lolos uji dari laptop Taiwan; 10 angka FinMind = MOPS |
| C1 | ≥80% pertanyaan uji benar dan bersitasi; 0 angka karangan lolos; 0 kata beli/jual; injeksi lewat pertanyaan gagal |
| D | Semua metrik Appendix 2 terisi angka asli; 0 angka salah terbit di pipeline lengkap vs baseline tanpa pemeriksa |
| Semua | Tes otomatis lulus; tiga bahasa tanpa kunci hilang; tidak ada kunci/data pribadi di repo; flowchart pengecekan lolos |

## Rancangan chatbot "Tanya FEAF"

- Pertanyaan bebas dalam tiga bahasa (angka laporan, dampak pengumuman, "what do you think of X").
- Gemini memanggil tool aplikasi (harga, laporan keuangan, ringkasan, pengumuman, valuasi), maksimal 5 langkah.
- Pemeriksa jawaban: setiap angka harus ada di hasil tool; kata beli/jual dilarang.
- Setiap jawaban bersumber (tautan MOPS/TWSE) dan punya jejak audit.
- Di luar lingkup (prediksi harga, order, data pribadi) → ditolak dengan sopan.
