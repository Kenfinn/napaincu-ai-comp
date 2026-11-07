# Rekap Proyek — pegangan untuk lanjut di lokal

Per 28 September 2026. Satu berkas ini cukup untuk melanjutkan tanpa membaca riwayat
percakapan. Rencana awal (14 Sep) ada di [`rencana-kerja.md`](./rencana-kerja.md), dan
aturan lomba lengkapnya di [`aaic-2026-ringkasan.md`](./aaic-2026-ringkasan.md).
**Status terbaru ada di berkas ini.**

---

## 0. Status 7 November — LOLOS FINALIS

Bagian 1–11 di bawah ditulis 28 Sep dan dibiarkan sebagai catatan. Yang berlaku sekarang
adalah bagian ini.

Berkas penyisihan 16 Okt sudah terkirim (lihat `docs/kirim-16-okt.md`; deck dan video
dari branch proposal sudah digabung). Survei 10 responden (6–8 Okt) menjadi bukti
Level 1.

**Tenggat:** paket finalis **13 Nov 23:59** (prototipe jalan, repo, README, metrik
Appendix 2, minimal satu operation trace). Final demo langsung **21 Nov**. Bobot
terberat di final adalah *Task Completion & Stability* (25%), yang juga menjadi tie-break.

**Masih belum pernah dilakukan:** Gemini belum pernah dipanggil, dan aplikasi belum
pernah jalan di data MOPS asli.

| # | Kapan | Siapa | Tugas | Selesai kalau |
|---|---|---|---|---|
| 1 | 8 Nov | Afinzaki | Rekap Bagian 6, Tahap 2: pasang kunci Gemini | Jejak audit `panggilan_model > 0` |
| 2 | 8–9 Nov | Afinzaki | Rekap Bagian 6, Tahap 3 dari jaringan Taiwan: tarik data asli beberapa emiten | Panel "Sumber data: nyata." |
| 3 | 8–11 Nov | Ferry & PDK | Gold set 30–50 pengumuman, ikuti [`panduan-gold-set.md`](./panduan-gold-set.md) | `eval/gold.csv` terisi |
| 4 | 9–10 Nov | Claude | Perbaiki apa pun yang rusak di langkah 1–2; snapshot data asli yang sudah bersih dari PII di-commit agar demo tidak bergantung pada jaringan Taiwan | Aplikasi jalan di data asli dari mesin mana pun |
| 5 | 10–11 Nov | Claude | 👍/👎 per peringatan yang menyetel ambang pemilah (janji deck untuk final) | Tes + tampil di jejak audit |
| 6 | 12 Nov | Afinzaki | `python3 scripts/evaluasi.py --mode aturan model tanpa-pemeriksa --menit-manual N --simpan` | Tabel metrik masuk README |
| 7 | 12–13 Nov | Claude + Afinzaki | README finalis, trace contoh, cara evaluator menjalankan | Paket terkirim 13 Nov |
| 8 | 14–20 Nov | Semua | Latihan demo ≥5 kali, termasuk saat API mati dan saat internet mati | Rencana cadangan teruji |

Tanya-jawab dan valuasi Fubon (2881) **tidak dibangun**. Keduanya disebut sebagai
keterbatasan di demo.

**Evaluasi sudah siap dipakai:** `scripts/evaluasi.py` membandingkan pipeline lengkap
(penalar aturan / model) dengan "LLM tanpa pemeriksa" pada gold set. Pada 4 fixture,
tanpa pemeriksa jumlah dalam USD ikut terbit, sedangkan pipeline lengkap 0 angka salah.

---

## 1. Ringkasnya

Kita ikut NAPAI Agentic AI Innovation Competition 2026, track SYSTEX *Investment
Intelligence & AI-Powered Stock Selection Agent*. Tim 3 orang: Afinzaki (teknis),
Ferry dan PDK (keuangan).

Produknya **Sentinel Saham**. Agent ini memantau pengumuman resmi MOPS (重大訊息),
menghitung ulang valuasi kalau ada pengumuman yang mengubah angka, dan **menolak
menerbitkan peringatan** kalau angkanya tidak bisa ditelusuri balik ke dokumen sumber.

**Posisi sekarang:** agent dan web-nya sudah jadi dan teruji. Yang tertinggal adalah
bukti lapangan (wawancara). Tenggat terdekat **16 Oktober 23:59**, target kirim 15 Oktober.

---

## 2. Lomba dalam satu halaman

### Jadwal

| Tanggal | Apa |
|---|---|
| **16 Okt 23:59** | Penyisihan: review dokumen, anonim |
| 6 Nov | Pengumuman finalis |
| 13 Nov 23:59 | Paket finalis: prototipe jalan, repo, README, metrik evaluasi |
| 21 Nov | Final: demo langsung |

### Yang dikumpulkan 16 Oktober (4 berkas)

1. Deck PDF maks **12 halaman**, nama `Category_Theme_TeamName_Proposal.pdf`
2. **Video maks 4 menit.** Anggota tim harus tampil menjelaskan dan mendemokan
3. Materi validasi lapangan: target user, bukti wawancara, kontak lapangan, level validasi
4. Formulir dan deklarasi, termasuk pengungkapan resource pihak ketiga

**Anonim:** deck, video, dan nama berkas tidak boleh memuat nama kampus, jurusan,
dosen, atau tanda pengenal lain.

### Syarat disebut "agent" (Pasal 4)

Wajib butir 1, plus minimal 2 dari butir 2–4:

| # | Syarat | Kita penuhi lewat |
|---|---|---|
| 1 | Tujuan dipecah jadi ≥2 langkah yang saling bergantung | Pipeline 5 tahap, tiap tahap bergantung pada hasil tahap sebelumnya |
| 2 | Memanggil tool / sistem luar | MOPS, kalkulator DCF, API model |
| 3 | Mengelola state dan menyesuaikan diri | Berhenti kalau tidak yakin; API gagal → retry → penalar aturan |
| 4 | Kontrol akses dan manajemen risiko | Pemeriksa keluaran, jejak audit, tanpa eksekusi order |

Kita memenuhi keempatnya.

**Yang TIDAK diminta, dan justru merugikan kalau dipaksakan:** melatih atau fine-tune
model, multi-agent, LangChain/CrewAI, vector DB/RAG. Juri menilai ketepatan desain,
bukan tumpukan teknologi. Untuk urusan keuangan, adanya human review dan mekanisme
stop **dihitung sebagai desain yang baik**.

### Bobot nilai

| Penyisihan | | Final | |
|---|---|---|---|
| Problem & Field-Need Evidence | 20% | **Task Completion & Stability** (juga tie-break pertama) | **25%** |
| Appropriateness of Agentic Design | 20% | Field Impact & User Validation | 20% |
| Technical & Data Planning | 20% | Agentic Technical Depth | 20% |
| Prototype & Validation Plan | 15% | Safety, Controllability & Governance | 15% |
| Innovation & Scalability | 15% | Innovation & Scalability | 10% |
| Safety, Governance & Ethics | 10% | Demo & Q&A | 10% |

Penyisihan tidak menilai "sistem jalan sempurna", tapi desain yang tepat dan bukti
bahwa masalahnya nyata. Di final kebalikannya: stabil mengalahkan pintar.

### Level validasi lapangan

Level 1 (sudah wawancara) adalah **ambang minimum penyisihan**. Level 2 (data, test
set berlabel) dibutuhkan untuk nilai bagus di final. **Kita masih di Level 0**, karena
belum ada wawancara.

---

## 3. Keputusan yang sudah dikunci

| Hal | Keputusan | Alasan |
|---|---|---|
| Bentuk prototipe | Web, FastAPI + HTML server-rendered | Kode data sudah Python. Tanpa npm, tanpa build step |
| Login | Tidak ada | Tidak ada kata sandi yang disimpan, tidak ada kewajiban PDPA tambahan |
| Model | Gemini free tier (`gemini-2.5-flash`), bisa ditukar lewat env var | Gratis, dan konteksnya muat pengumuman Mandarin panjang |
| Tahap 3–4 | **Tidak memakai model**, murni aritmetika dan pemeriksaan | Model tidak pernah menghitung dan tidak pernah menilai dirinya sendiri |
| Tanpa kunci API | Aplikasi tetap jalan pakai penalar aturan | Sekaligus jadi baseline pembanding untuk Appendix 2 |
| Mata uang asing | Ditolak (fail-closed) | Lebih baik tidak terbit daripada salah konversi diam-diam |
| Eksekusi order | Tidak ada, di mana pun | Dilarang Pasal 14.2 |

**Konsekuensi free tier yang wajib diungkap di deck:** Google memakai konten free tier
untuk meningkatkan produknya. Ini aman untuk kita karena pengumuman MOPS dokumen publik
dan data pribadi (`發言人`, jabatan, telepon) sudah dibuang sebelum disimpan. Kalau
nanti perlu menganalisis data yang tidak publik, free tier tidak boleh dipakai.

---

## 4. Yang sudah jadi

Semua sudah digabung ke `main`.

| Bidang | Hasil | Letak |
|---|---|---|
| Aturan | Ringkasan lengkap aturan lomba | `docs/aaic-2026-ringkasan.md` |
| Akses data | MOPS diuji dari jaringan kampus: 5 emiten, 711 pengumuman, 100% bersitasi | `docs/akses-data.md`, `scripts/` |
| Valuasi | Kalkulator DCF deterministik untuk TSMC (2330) | `scripts/dcf.py`, `valuation/inputs/2330.json` |
| Desain | 8 layar hi-fi, 8 wireframe, 2 diagram wajib (state agent untuk deck hal. 5, arsitektur untuk hal. 6), semua sudah jadi PNG | `design/`, `design/export/`, `wireframe/` |
| **Agent** | Pipeline 5 tahap: saring → pilah → sari → hitung ulang → periksa | `app/agent/` |
| Web | Feed, detail peringatan, jejak audit, valuasi | `app/main.py`, `app/templates/` |
| Tes | 17 tes lulus, termasuk uji prompt injection dan uji "API key tidak pernah bocor ke jejak" | `tests/test_agent.py` |
| Dokumentasi | README teknis, memenuhi butir 3 syarat Pra-final | `README.md` |

### Cara kerja agent

```
Pengumuman MOPS
   [0] SARING   deterministik  nomor pasal tidak relevan → DILEWATI (tidak sampai ke model)
   [1] PILAH    model          menyentuh input valuasi yang mana?
   [2] SARI     model          angka berapa, dari kalimat mana persis?
                               tidak ada angka lengkap dengan kalimatnya → DITAHAN
   [3] HITUNG   deterministik  dcf.compute() sebelum vs sesudah
   [4] PERIKSA  deterministik  7 pemeriksaan: label, kutipan, angka, mata uang,
                               satuan, konversi, besaran
                               gagal → DITOLAK, alasan tercatat
                               lolos → TERBIT
```

Empat data contoh (fixture) sengaja memuat kasus yang menunjukkan pertahanannya:

| Kasus | Hasil | Yang dibuktikan |
|---|---|---|
| Belanja modal TSMC | terbit | Alur normal jalan ujung ke ujung |
| Belanja modal + kalimat prompt injection | terbit dengan angka yang **benar** | Injeksi tercatat, angka sisipan tidak pernah terbit |
| Pengumuman rutin MediaTek | dilewati | Disaring sebelum sampai ke model |
| Jumlah dalam USD | ditolak | Fail-closed pada mata uang asing |

---

## 5. Yang belum selesai

### Terlambat atau paling berisiko

| Hal | Status | Kenapa penting |
|---|---|---|
| **Wawancara 6–8 responden** | Belum mulai. Jadwalnya sudah lewat (19–27 Sep) | Ambang minimum penyisihan. Menentukan 20% nilai, deck hal. 2–3, dan berkas ke-3 |
| **Angka baseline manual** | Belum ada | Diambil dari wawancara. Wajib untuk perbandingan Appendix 2, **tidak bisa direkonstruksi belakangan** |
| **Field liaison** | Belum ditunjuk | Wajib menurut Pasal 7 |

### Belum pernah benar-benar jalan

- **Gemini belum pernah dipanggil sekali pun.** Semua jejak menunjukkan
  `panggilan_model: 0`. Kodenya sudah ada, tapi belum teruji dengan kunci asli.
- **Aplikasi baru jalan di 4 data contoh**, belum di data asli. MOPS memblokir IP luar
  Taiwan dan IP datacenter, jadi data asli hanya bisa ditarik dari laptop di jaringan
  kampus.

Keduanya dikerjakan di Bagian 6.

### Butuh Ferry & PDK

| Hal | Letak |
|---|---|
| Verifikasi daftar pasal 重大訊息 yang relevan (11, 20, 22, 2). Masih bertanda "BELUM DIVERIFIKASI" | `app/agent/screen.py` |
| Ganti 5 sumber bertanda "GANTI" dengan URL MOPS/TWSE. Arus kas 2023–2024 masih **perkiraan** yang disetel agar cocok dengan hitungan tangan | `valuation/inputs/2330.json` |
| Gold set: 30–50 pertanyaan berlabel (jawaban benar + sumber) untuk Level 2 | Belum ada, target 8 Okt |
| Metode valuasi untuk Fubon (2881). DCF biasa tidak berlaku untuk perusahaan keuangan | Untuk November |

### Janji di kalimat scope yang belum dibangun

- **"Belajar dari reaksi investor untuk menyetel ambang"**: ambang pemilah masih angka
  tetap (0,55).
- **Permukaan tanya-jawab**: baru ada mockup hi-fi.

Untuk Oktober, cukup ditulis jujur di deck sebagai rencana. Untuk final, keduanya harus
jalan atau kalimat scope-nya dipersempit.

### Berkas 16 Oktober

| Berkas | Status |
|---|---|
| 1. Deck 12 halaman | Belum. Bahan untuk hal. 5, 6, 8, 9 sudah ada |
| 2. Video ≤4 menit | Belum |
| 3. Materi validasi lapangan | Belum, bergantung pada wawancara |
| 4. Formulir & deklarasi | Pendaftaran sudah jalan. Deklarasi pihak ketiga perlu menyebut Gemini free tier |

---

## 6. Menjalankan di laptop — tiga tahap

Kerjakan berurutan. Tiap tahap punya tanda berhasil. Jangan lanjut sebelum tandanya muncul.

### Tahap 1 — jalankan apa adanya

Tanpa kunci, memakai data contoh. Bisa dari jaringan mana saja.

```bash
git clone https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m unittest discover -s tests      # harus: Ran 17 tests ... OK
uvicorn app.main:app --reload
```

Buka <http://127.0.0.1:8000>.

**Tanda berhasil:** muncul 4 peringatan, yaitu 2 terbit, 1 ditolak, 1 dilewati. Di atas
ada pita **"Data contoh."**. Kotak *Mesin penalar* di panel samping bertitik kuning dan
bertuliskan *"Tanpa kunci API — penalar berbasis aturan. Sumber data: fixture."*

Kalau repo-nya sudah pernah di-clone, cukup `git pull`, lalu mulai dari baris
`python3 -m venv`. Setiap membuka terminal baru, jalankan
`source .venv/bin/activate` dulu.

### Tahap 2 — pasang kunci Gemini

1. Buat kunci gratis di <https://aistudio.google.com> (menu *Get API key*).
2. Di terminal yang sama dengan tempat menjalankan aplikasi:

```bash
read -rs GEMINI_API_KEY && export GEMINI_API_KEY   # tempel kunci, tekan Enter (tidak tampil di layar)
uvicorn app.main:app --reload
```

Pakai `read -rs` supaya kunci tidak tercatat di riwayat terminal. **Jangan pernah**
menulis kunci ke berkas yang di-commit. `.env` dan `.venv/` sudah diabaikan git.

**Tanda berhasil:** kotak *Mesin penalar* bertuliskan *"Model aktif."* dan titiknya
tidak lagi kuning. Di halaman jejak audit salah satu peringatan, angka
**Panggilan model** lebih dari 0.

Hasil pipeline di-cache sejak server menyala. Kalau kunci baru dipasang setelah server
jalan, matikan server (Ctrl+C) lalu nyalakan lagi, atau buka
<http://127.0.0.1:8000/?segarkan=1>.

### Tahap 3 — data asli (wajib dari jaringan kampus / Taiwan)

```bash
python3 scripts/spike_mops.py                              # daftar pengumuman 5 emiten → data/raw/
python3 scripts/parse_mops.py                              # → data/parsed/announcements.json
python3 scripts/fetch_details.py --code 2330 --limit 20    # isi lengkap → data/parsed/details.json
uvicorn app.main:app --reload
```

**Tanda berhasil:** pita "Data contoh." hilang, dan panel samping bertuliskan
*"Sumber data: nyata."*

Yang perlu diketahui:

- Skrip sengaja lambat, dengan jeda 2–2,5 detik per permintaan. **Jangan turunkan jedanya**,
  karena MOPS server publik.
- Baru TSMC (2330) yang punya berkas valuasi. Pengumuman emiten lain akan berakhir
  **ditahan** dengan alasan "belum ada berkas valuasi". Itu perilaku yang benar,
  bukan bug.
- Folder `data/` tidak di-commit, karena isinya besar dan hanya bisa ditarik dari Taiwan.
  Untuk kembali ke data contoh, pindahkan atau ganti nama folder `data/parsed/`.

---

## 7. Tugas minggu ini (28 Sep – 4 Okt)

### Ferry & PDK — jalur kritis

1. **Mulai wawancara.** Target 6–8 orang, idealnya yang memantau saham Taiwan.
   Tiap wawancara wajib menghasilkan angka, bukan cuma cerita:
   - berapa menit memeriksa satu pengumuman
   - berapa emiten dipantau
   - seberapa sering memeriksa
   - kapan terakhir telat tahu ada pengumuman penting
   - apa yang dilakukan setelah tahu

   **Jangan pitch produknya duluan.** Tanyakan apa yang mereka lakukan terakhir kali,
   bukan apa yang mereka kira akan lakukan. Catat sebagai "Responden A/B/C", bukan nama.
   Minta persetujuan di awal: direkam atau dicatat, disimpan berapa lama, cara minta hapus.
2. Tunjuk satu **field liaison**.
3. Verifikasi daftar pasal di `screen.py` dan sumber "GANTI" di `2330.json`.

### Afinzaki — dua hal teknis saja, jangan tambah fitur

1. Tahap 2 di atas: kunci Gemini, dengan target jejak pertama yang `panggilan_model > 0`.
2. Tahap 3 di atas, dari jaringan kampus. Rekam layarnya sekalian untuk bahan video.

Rincian per tanggal sampai 8 Oktober ada di [`tugas-A.md`](./tugas-A.md).

### Claude

1. Revisi halaman Notion "Panduan Wawancara Level 1": tambah pertanyaan pengukuran
   baseline, skrip persetujuan PDPA, format catatan anonim.
2. Draf deck untuk halaman yang tidak bergantung wawancara (hal. 1 dan 4–12).
3. Skrip pembanding Appendix 2: penalar aturan vs model pada kasus yang sama.

### Sesudahnya

| Tanggal | Fokus |
|---|---|
| 5–8 Okt | Wawancara rampung, gold set, isi deck hal. 2–3 |
| 9–14 Okt | Finalisasi deck, rekam video, cek anonimitas semua berkas |
| 15 Okt | Kirim dan verifikasi semua tautan. 16 Okt cadangan |

---

## 8. Batasan yang tidak boleh dilanggar

- **Tidak ada API key, kata sandi, atau data pribadi** di dokumen maupun kode yang
  diserahkan. Kunci hanya dari environment variable. Ada tes yang menjaga ini.
- **Data pribadi dibuang di sumber:** `fetch_details.py` membuang `發言人`, `發言人職稱`,
  `發言人電話`. Yang dicatat hanya *field mana* yang dibuang, bukan isinya.
- **Jeda antar-permintaan ke MOPS jangan diturunkan** (`POLITE_DELAY`).
- **Tidak ada eksekusi order otomatis** (Pasal 14.2).
- **Anonim** di deck, video, dan nama berkas penyisihan.
- **Label jujur:** layar harus selalu menyebut mesin yang dipakai (model atau penalar
  aturan) dan sumber datanya (asli atau fixture).
- Merah = naik, hijau = turun (konvensi pasar Taiwan).

---

## 9. Peta repo

```
app/
  main.py               rute web + API
  config.py             setelan, semuanya dari environment variable
  store.py              baca data/parsed/, jatuh ke data/fixtures/ kalau kosong
  agent/
    screen.py           [0] saringan nomor pasal
    llm.py              antarmuka model (Gemini) + penanganan gagal
    extract.py          [1–2] pilah & sari, plus penalar aturan cadangan
    recompute.py        [3] hitung ulang DCF
    verify.py           [4] 7 pemeriksaan
    pipeline.py         orkestrasi + jejak audit → data/traces/
  templates/, static/   tampilan
scripts/
  spike_mops.py         tarik daftar pengumuman (jaringan Taiwan)
  parse_mops.py         HTML mentah → announcements.json
  fetch_details.py      isi lengkap → details.json (buang data pribadi)
  dcf.py                kalkulator DCF (CLI + dipakai web)
  render_design.js      design/*.dc.html → PNG
  build_figma_svg.py    gabung PNG → satu SVG untuk Figma
valuation/inputs/       input valuasi per emiten (baru 2330)
data/fixtures/          4 kasus contoh, di-commit
design/, wireframe/     layar hi-fi, wireframe, diagram
docs/                   ringkasan aturan, akses data, rencana, rekap ini
tests/                  17 tes
```

---

## 10. Tautan

| Apa | Di mana |
|---|---|
| Rencana kerja + status (Notion) | 🧭 AAIC 2026 — Rencana Kerja Tim 3 Orang, di VAULT / Obsidian Notes |
| Panduan wawancara (Notion) | AAIC 2026 — Panduan Wawancara Level 1 |
| Halaman kerja interaktif (checklist) | <https://claude.ai/code/artifact/a37a4aa0-91e5-44b2-9830-946977a5d26d> |
| Situs & aturan resmi | <https://napaincu.github.io/aaic2026/en/index.html> |
| Figma | File `ZTux17Ef8AZGb4yHUumizI` |

---

## 11. Catatan untuk sesi Claude berikutnya

- Baca berkas ini dulu, lalu `docs/aaic-2026-ringkasan.md` kalau butuh detail aturan.
- Kerja di `main` (branch lama `claude/aaic-2026-rules-6yy7gu` dan `claude/vigilant-feynman-cijkv5` sudah digabung). Daftar tugas jalur A ada di `docs/tugas-A.md`.
- **Figma:** percobaan membangun diagram sebagai layer asli gagal di tengah jalan, karena
  parser vector Figma tidak menerima perintah arc SVG (`A`). Kemungkinan ada frame
  setengah jadi di sekitar koordinat (−3253, 1900). Bersihkan dulu sebelum membangun
  ulang, dan ganti ikon arc dengan ELLIPSE + garis lurus. Prioritas rendah, karena
  PNG untuk deck sudah siap.
- Diagram di `design/*.dc.html` adalah **spesifikasi** pipeline, bukan ilustrasi. Kalau
  alur agent berubah, diagramnya ikut diubah.
- Setiap klaim angka di layar valuasi harus cocok persis dengan keluaran
  `python3 scripts/dcf.py`. Juri bisa mencocokkannya.
