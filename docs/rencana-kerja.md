# Rencana Kerja AAIC 2026 — Tim 3 Orang

> Ini rencana awal 14 September. Status terbaru dan langkah berikutnya ada di
> [`rekap.md`](./rekap.md).

Halaman kerja versi interaktif (checklist bisa dicentang bersama):
https://claude.ai/code/artifact/a37a4aa0-91e5-44b2-9830-946977a5d26d

Rangkuman aturan lengkap ada di [`aaic-2026-ringkasan.md`](./aaic-2026-ringkasan.md).

---

## Premis

Penyisihan 16 Oktober adalah **review dokumen, bukan uji sistem**. Prototipe yang benar-benar
jalan baru wajib 13 November, dan hanya kalau lolos finalis (diumumkan 6 November).

Konsekuensinya untuk 33 hari ke depan: yang harus jadi bukan produk, tapi **bukti lapangan**,
**satu alur tipis yang benar-benar jalan**, dan **argumen kenapa masalah ini butuh agent**.

Tim 3 orang dengan satu orang teknis tidak kalah karena kurang canggih. Tim seperti ini kalah
karena scope-nya terlalu lebar.

## Dua gerbang

| | Gerbang 1 — 16 Okt 23:59 | Gerbang 2 — 13 & 21 Nov |
|---|---|---|
| Bentuk | Review dokumen | Sistem yang jalan |
| Wajib | Deck ≤12 hal, video ≤4 menit, materi validasi lapangan, formulir + deklarasi | Prototipe + akun evaluator, repo, README teknis, metrik Appendix 2, ≥1 operation trace, demo langsung |
| Tidak diminta | Sistem produksi, akurasi tinggi, source code | — |

40% nilai penyisihan (bukti masalah 20% + ketepatan desain agentic 20%) tidak memuat satu baris kode pun.

## Keputusan scope

> Agen yang memantau daftar saham pilihan satu investor, mendeteksi kejadian material dari
> MOPS/TWSE/TPEx, lalu mengirim peringatan bersitasi hanya ketika kejadian itu relevan dengan
> profil risikonya — dan belajar dari reaksi investor untuk menyetel ambang relevansinya.

**Kenapa sudut ini:** satu-satunya bentuk yang menutup keempat tahap core workflow yang diminta
panitia (personalized intelligence → proactive delivery → behavioral feedback → continuous
optimization), termasuk dua tahap yang hampir pasti dilewati tim lain. Alasan "kenapa harus agent"
juga jadi mudah dijawab: pemantauan berjalan tanpa dipicu pertanyaan.

**Jangan dibangun:**

| Dilarang / dihindari | Alasan |
|---|---|
| Eksekusi order otomatis | Pasal 14.2 melarang aksi berdampak substantif tanpa otorisasi |
| Prediksi harga | Tidak bisa disitasi, menabrak kriteria traceability |
| Optimasi portofolio | Menambah permukaan tanpa menambah nilai |
| Chat serba bisa | Melemahkan argumen agentic |

Aturan menyebut eksplisit: untuk urusan **keuangan**, human review dan mekanisme stop
*dihitung sebagai desain yang baik*. Batasan ini menambah nilai.

## Arsitektur tiga lapis

1. **Evidence layer** — serap MOPS/TWSE/TPEx jadi dokumen ternormalisasi (URL sumber, tanggal,
   kode saham) + penyimpanan angka terstruktur terpisah. Ini yang membuat *traceable* bisa dibuktikan.
2. **Agent layer** — planner → tool → state/retry → **verifier output** yang mencocokkan tiap angka
   hasil generasi dengan penyimpanan terstruktur. Tidak cocok → tolak dan eskalasi.
3. **Dua permukaan** — (a) feed peringatan proaktif; (b) antarmuka tanya-jawab di atas evidence
   layer yang sama, supaya gold answers dan test case juri bisa dijalankan.

```
watchlist + profil risiko → pantau sumber → deteksi kejadian → nilai relevansi
  → [relevan?] → susun alert bersitasi → verifikasi angka → kirim
  → reaksi user → setel ambang
```

## Pembagian peran

| | Jalur | Definisi selesai 16 Okt |
|---|---|---|
| **A** (kamu) | Agent & Data | Satu emiten, satu jenis kejadian, satu alert bersitasi — jalan ujung ke ujung, bisa direkam |
| **B** | Lapangan & Bukti | 6–8 wawancara terdokumentasi dengan pain point terkuantifikasi + gold set 30–50 pertanyaan berlabel |
| **C** | Produk & Submisi | Semua berkas terkirim 15 Okt |

Ketiganya wajib mahasiswa aktif. Dosen/penasihat boleh membimbing, tidak boleh mengerjakan
desain inti, pemrograman, evaluasi, atau presentasi.

## Fase

| Fase | Tanggal | Fokus |
|---|---|---|
| 0 | 13–18 Sep | Kunci arah: konfirmasi kelayakan, hadiri briefing 18 Sep, uji 72 jam, scope satu kalimat |
| 1 | 19–27 Sep | Wawancara (kunci Level 1) + evidence layer 20–30 emiten |
| 2 | 28 Sep–8 Okt | Satu alur tipis ujung ke ujung + verifier + gold set (kunci Level 2) |
| 3 | 9–14 Okt | Produksi deck 12 halaman & video 4 menit, cek anonimitas |
| 4 | 15–16 Okt | Kirim 15 Okt, verifikasi semua tautan |
| 5 | 17 Okt–6 Nov | Jangan berhenti: perluas cakupan, kejar Level 3 di sandbox, tulis README bertahap |
| 6 | 6–13 Nov | Paket finalis: repo, akun evaluator, metrik Appendix 2, operation trace |
| 7 | 14–21 Nov | Latihan demo ≥5 kali termasuk saat gagal, siapkan rencana cadangan |

Rincian tugas per fase ada di halaman kerja interaktif (tautan di atas).

## Risiko yang harus dijawab minggu ini

1. **[Pemblokir] Status kemahasiswaan** — aturan menyebut mahasiswa aktif di perguruan tinggi
   *di Taiwan*, ditentukan per tenggat pendaftaran. Tanyakan ke panitia sekarang.
2. **[Pemblokir] Bahasa sumber** — MOPS/TWSE/TPEx berbahasa Mandarin tradisional. Uji keandalan
   pipeline terjemahan untuk angka dan istilah akuntansi.
3. **[Uji 72 jam] Keterambilan data** — tarik & parse 20 pengumuman MOPS untuk 5 emiten. Gagal
   dalam 3 hari → pindah ke tantangan Ai3 (GovAid Copilot): sumber lebih sedikit, lebih stabil,
   logika kelayakannya lebih mudah dibuat agentic.
4. **[Pantau] Gold answers belum diumumkan** — jangan hard-code emiten demo. Briefing 18 September
   kemungkinan memperjelas cakupan data.
