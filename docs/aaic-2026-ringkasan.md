# AAIC 2026 — Ringkasan Aturan & Analisis Track SYSTEX

Sumber:
- Halaman kompetisi: https://napaincu.github.io/aaic2026/en/index.html
- Aturan resmi (EN): https://napaincu.github.io/aaic2026/rules/competition-rules-en.pdf
- Catatan: versi **Bahasa Mandarin** yang berlaku jika ada perbedaan dengan versi EN.

Nama resmi: **NAPAI Agentic AI Innovation Competition for Campus Applications**
(diselenggarakan bersama TAAI 2026, dibina Kemendikbud Taiwan / MOE Dept. of Information and Technology Education).

Empat prinsip yang jadi "nafas" seluruh penilaian: **Operable · Measurable · Controllable · Field-validated**.

---

## 1. Posisi track di dalam struktur lomba

Peserta memilih **1 kategori** + **1 tema**:

| Kategori | Isi |
|---|---|
| A — Campus Self-Proposed | Tim mencari sendiri masalah nyata di kampus, dan mengurus sendiri wawancara/data/lokasi uji |
| **B — Designated Field Group** | Tim mengerjakan topik/data/API/lingkungan uji yang diumumkan panitia atau mitra |

Track pada gambar ada di **Kategori B**:

- **Mitra**: SYSTEX Corporation
- **Designated application field**: Taiwan
- **Designated challenge**: *Investment Intelligence & AI-Powered Stock Selection Agent* (投資情報與智慧選股 AI Agent)
- **Tema aplikasi** yang paling cocok: **Industry & Public-Sector Co-Creation** (tema no. 4)

Ada satu tantangan Kategori B lain (Ai3 — GovAid Copilot untuk subsidi pengasuhan anak & sewa rumah di Taipei/New Taipei/Taoyuan), jadi pilihannya bukan cuma yang di gambar.

**Technology tags** (boleh multi-pilih, tidak memengaruhi kategori/tema): Agentic Workflow, Domain-Specific Agent, Multi-Agent Collaboration, RAG/Knowledge Agent, Physical/Digital Embodiment, Human-in-the-loop.

---

## 2. Detail tantangan SYSTEX

**Deskripsi.** Pakai Agentic AI untuk menyatukan data finansial, market intelligence, dan model investasi menjadi asisten investasi cerdas yang mampu: riset, analisis, seleksi saham, penjelasan, pemantauan, dan manajemen risiko. Tujuannya membantu investor menyaring kandidat dengan cepat, memahami risiko, dan membentuk **rujukan yang bisa ditelusuri** untuk keputusan investasi.

Panitia secara eksplisit meminta tim **melampaui sekadar menyajikan informasi saham**, menuju dukungan keputusan yang **explainable, verifiable, dan continuously trackable**.

**Core workflow yang diminta** (ini praktis jadi kerangka arsitektur agent):

```
Personalized intelligence → Proactive delivery → Behavioral feedback → Continuous optimization
```

Artinya siklusnya harus tertutup, bukan one-shot:
1. intelijen yang dipersonalisasi per profil investor;
2. pengiriman proaktif (agent yang memulai, bukan menunggu ditanya — mis. monitoring & alert);
3. umpan balik perilaku pengguna (apa yang dibuka, diabaikan, ditindaklanjuti);
4. optimasi berkelanjutan dari umpan balik itu.

**Sumber data & lingkup validasi:**
- Basis utama harus informasi publik yang kredibel dan bisa ditelusuri: **MOPS** (Market Observation Post System), **TWSE** (Taiwan Stock Exchange), **TPEx** (Taipei Exchange), investor conference perusahaan listed & OTC, berita, laporan riset, dan informasi publik lain.
- **Lingkup utama: analisis saham individual perusahaan listed & OTC Taiwan.**
- Versi kebijakan, situs yang ditunjuk, cakupan data, dan **gold answers** untuk penilaian aktual akan menyusul di pengumuman situs resmi → artinya juri akan menguji dengan **test case dan kunci jawaban yang mereka siapkan**, jadi sistem harus siap menjawab pertanyaan yang belum kita lihat, dengan sitasi.
- Panitia berhak memindahkan track berdasarkan isi substantif karya.

---

## 3. Field Validation Levels (bagian yang diminta dipahami)

Tangga bukti lapangan, 0–4:

| Level | Nama | Definisi | Status |
|---|---|---|---|
| **0** | Problem hypothesis | Tim mengajukan masalah, **belum ada** bukti dari user atau proses nyata | Hipotesis |
| **1** | Needs interviews | Target user / pemilik proses / stakeholder **sudah diwawancarai**, pain point & kebutuhan terdokumentasi | **Ambang penyisihan** |
| **2** | Data / process validation | Sudah memperoleh data ter-deidentifikasi, dokumen proses, test case, spesifikasi API, atau materi terverifikasi lain | **Ambang final** |
| **3** | Prototype trial | User asli mengoperasikan prototipe di lingkungan simulasi/sandbox/terkontrol dan memberi feedback | Uji coba |
| **4** | Field pilot | Deployment terbatas di unit nyata, ada **catatan operasional** + **perbandingan kuantitatif sebelum/sesudah** | Pilot |

**Aturan ambangnya:**
- Penyisihan (preliminary) **minimal Level 1**.
- Untuk skor bagus di kriteria **"Field Impact & User Validation" (20% di final)**, pada prinsipnya harus **Level 2 ke atas**.
- Jika ada batasan data sensitif, keamanan siber, atau hukum → boleh pakai **data ter-deidentifikasi, data sintetis, sandbox, atau alternatif lain yang disetujui panitia**.

**Terjemahan level ke track SYSTEX** (karena "field"-nya di sini pasar saham, bukan kantor kampus):

| Level | Wujud konkret untuk agent saham |
|---|---|
| 1 | Wawancara investor ritel / analis / manajer portofolio: bagaimana mereka menyaring saham sekarang, berapa lama, di mana macetnya. Dokumentasikan pain point + kutipan. |
| 2 | Kumpulkan data MOPS/TWSE/TPEx nyata, transkrip investor conference, plus **test set berlabel** (pertanyaan → jawaban benar + sumber). Spesifikasi API terdokumentasi. |
| 3 | Investor sungguhan memakai prototipe di sandbox (**paper trading, tanpa uang riil**) dan memberi feedback terstruktur. |
| 4 | Pilot terbatas dengan satu unit/komunitas investor, ada log operasi + perbandingan before/after (mis. waktu screening turun dari X ke Y menit). |

Realistis untuk timeline sekarang: kunci Level 2 sebelum penyisihan, kejar Level 3 sebelum final. Level 3 sepenuhnya sah lewat sandbox — tidak perlu uang riil.

**Aturan pemakaian resource lapangan** (berlaku untuk data/akun/API/perangkat/dokumen dari mitra):
- Hanya untuk keperluan lomba, dalam lingkup yang diizinkan.
- **Dilarang** dipublikasikan, dialihkan, di-reverse engineer, diakses tanpa izin, atau dipakai **melatih model lain**.
- Harus dihapus/dikembalikan setelah lomba bila diminta penyedia.
- Penyedia lapangan **tidak boleh** memakai lomba untuk mendapatkan sistem produksi/komersial gratis; adopsi lanjutan, alih teknologi, magang, atau kerja sama komersial butuh perjanjian terpisah.

---

## 4. Syarat minimum sebuah karya (gerbang kelayakan)

Definisi Agentic AI di aturan: sistem AI berorientasi tujuan yang mampu merencanakan, mengambil keputusan, memanggil tool, atau berinteraksi dengan sistem sesuai state tugas, **dan menyesuaikan aksi berikutnya** berdasarkan hasil antara, error, atau umpan balik pengguna.

Karya **wajib memenuhi butir 1**, plus **minimal 2 dari butir 2–4**:

1. **[WAJIB] Goal orientation & task decomposition** — memecah tujuan jadi ≥2 langkah yang saling bergantung berurutan, dan maju berdasarkan status eksekusi.
2. **Tool / external-system invocation** — API, database, knowledge base, sistem administrasi kampus, software, layanan cloud, perangkat.
3. **State management & dynamic adjustment** — merevisi rencana, retry, beralih ke tool alternatif, atau menghentikan tugas berdasarkan hasil antara/error/perubahan lingkungan/feedback user.
4. **Access control & risk management** — konfirmasi manusia, pembatasan izin, log operasi, failure recovery, verifikasi output.

**Yang pada prinsipnya TIDAK lolos:** Q&A satu giliran, generasi konten sekali jalan, RAG/retrieval QA murni, otomasi yang sepenuhnya kaku tanpa keputusan berbasis state, atau simulasi video tanpa sistem yang bisa diverifikasi.

**Penting:** Multi-Agent, long-term memory, self-reflection, self-repair **tidak wajib**. Juri menilai **ketepatan**, bukan tumpukan teknologi. Menumpuk framework tanpa alasan justru merugikan.

---

## 5. Kriteria penilaian

### Penyisihan — review dokumen, total 100

| Kriteria | Bobot |
|---|---|
| Problem & Field-Need Evidence | 20% |
| Appropriateness of Agentic AI Design | 20% |
| Technical & Data Planning | 20% |
| Prototype & Validation Plan | 15% |
| Innovation & Scalability Potential | 15% |
| Safety, Governance & Ethics | 10% |

### Final — demo langsung di lokasi, total 100

| Kriteria | Bobot |
|---|---|
| **Task Completion & Stability** | **25%** |
| Field Impact & User Validation | 20% |
| Agentic Technical Depth & Appropriateness | 20% |
| Safety, Controllability & Governance | 15% |
| Innovation & Scalability Value | 10% |
| On-site Demonstration & Q&A | 10% |

**Tie-break** berurutan: Task Completion & Stability → Field Impact & User Validation → Safety, Controllability & Governance. Jika masih seri, keputusan dewan juri.

**Prinsip kunci:** *"A higher degree of autonomy is not necessarily better."* Untuk urusan berisiko tinggi — persetujuan administratif, nilai, **keuangan**, kesehatan, hukum, data pribadi — adanya **human review, tiered permission, dan mekanisme stop justru dihitung sebagai desain yang baik.** Track saham masuk kategori "keuangan", jadi ini langsung relevan.

Juri boleh meminta tim menjalankan **test case yang mereka tentukan**, dan boleh memeriksa **log sistem, dokumentasi, dan source code**.

---

## 6. Materi yang harus dikumpulkan

### Penyisihan — 2026.10.16, Jumat 23:59
1. **Proposal deck PDF, maks 12 halaman** (cover, daftar isi, lampiran ikut dihitung). Nama file: `Category_Theme_TeamName_Proposal.pdf`
2. **Video konsep/demo, maks 4 menit** — anggota tim harus menjelaskan & mendemokan masalah, alur tugas agent, pemanggilan tool, operasi prototipe, atau hasil yang terverifikasi. MP4 atau tautan unlisted yang bisa diakses.
3. **Materi kebutuhan & validasi lapangan** — sumber kebutuhan, target user, bukti wawancara/proses, kontak lapangan, **level validasi saat ini**. Boleh ringkasan ter-deidentifikasi bila menyangkut informasi rahasia.
4. **Formulir pendaftaran online & deklarasi** — termasuk pengungkapan resource pihak ketiga, karya sebelumnya, keikutsertaan di lomba lain, dan pendanaan lain.

> **Review penyisihan bersifat anonim.** Deck, video, dan nama file **tidak boleh** memuat nama universitas, jurusan, dosen pembimbing, atau tanda pengenal lain.

### Struktur deck yang direkomendasikan (Appendix 1 — 12 halaman)

| Hal | Isi |
|---|---|
| 1 | Cover anonim: judul karya, kategori, track, technology tags |
| 2 | Masalah, target user, alur kerja saat ini |
| 3 | Wawancara kebutuhan, bukti lapangan, pain point terkuantifikasi |
| 4 | Kenapa harus Agentic AI; perbandingan dengan chatbot biasa / RAG / workflow kaku |
| 5 | Alur tugas & diagram state agent |
| 6 | Arsitektur sistem, model, tool, API, aliran data |
| 7 | Izin, kolaborasi manusia–AI, keamanan, penanganan kegagalan |
| 8 | Tampilan prototipe / alur operasi |
| 9 | Test case, baseline, metrik evaluasi |
| 10 | Deployment, biaya, pemeliharaan, rencana adopsi lapangan |
| 11 | Inovasi, skalabilitas, pengembangan ke depan |
| 12 | Peran tim, perbedaan dari karya sebelumnya, resource pihak ketiga, pengungkapan risiko |

### Pra-final (untuk finalis) — 2026.11.13, Jumat 23:59
1. Prototipe / lingkungan uji yang bisa dijalankan (sediakan **akun evaluator khusus dengan izin terkontrol** bila perlu login).
2. Repo GitHub/GitLab (privat atau publik) atau paket source terenkripsi. Bila source penuh tak bisa diberikan karena lisensi/pembatasan lapangan: serahkan modul yang bisa diaudit, dokumentasi antarmuka, catatan eksekusi, dan penjelasan.
3. **README / dokumentasi teknis**: arsitektur, langkah instalasi & eksekusi, dependensi, info model & versi, API, environment variable, lisensi, aliran data, izin, keterbatasan yang diketahui, troubleshooting.
4. **Materi evaluasi agent**: test case, baseline, success rate, akurasi, latensi, biaya, jenis error, tingkat intervensi manusia, dan **minimal satu operation trace / event record**.
5. Deck terbaru, video demo, catatan validasi lapangan, formulir pengungkapan resource pihak ketiga, formulir self-assessment data & keamanan, kebutuhan demo final.

> Semua dokumen dan source code **dilarang** memuat password, API key, data pribadi yang belum di-deidentifikasi, atau informasi rahasia tanpa izin.

### Disclosure minimum evaluasi agent di final (Appendix 2)
- Definisi keberhasilan tugas, jumlah test case, lingkungan pengujian.
- Perbandingan dengan proses manual/manusia, workflow kaku, model tunggal, atau baseline wajar lain.
- Success rate, akurasi, latensi rata-rata & maksimum, biaya model/API.
- Tool-call success rate, jumlah retry, tingkat intervensi manusia, tingkat terminasi.
- Kategori error, keterbatasan yang diketahui, skenario terburuk, metode pemulihan.
- Minimal satu operation trace / event record / layar eksekusi yang bisa diaudit.
- Sumber data, model & versinya, serta metode version management untuk prompt/strategi utama.
- Hasil uji untuk data pribadi, keamanan siber, izin, **prompt injection**, dan output yang tidak pantas.

---

## 7. Aturan tim & kelayakan

- Mahasiswa aktif di perguruan tinggi **di Taiwan**, termasuk S2 & S3, jurusan apa pun. Status kemahasiswaan ditentukan per batas waktu pendaftaran.
- **2–5 mahasiswa per tim**, wajib 1 ketua. Dosen pembimbing opsional. Tim yang melakukan validasi lapangan nyata **wajib** menunjuk **field liaison** (boleh orang yang sama dengan pembimbing).
- Boleh lintas kampus & lintas disiplin. **Satu mahasiswa hanya boleh ikut satu tim.** Karya inti yang sama tidak boleh diajukan oleh tim berbeda atau di kategori berbeda.
- Dosen/staf lapangan/penasihat teknis **hanya boleh** membimbing, menjelaskan kebutuhan, dan membantu pengujian — **tidak boleh** mengerjakan desain inti, pemrograman, evaluasi, atau presentasi/Q&A.
- Perubahan anggota/ketua/pembimbing/field liaison harus diajukan dalam **7 hari** setelah pengumuman finalis. Anggota hanya boleh dikurangi atau diganti, **tidak boleh ditambah** melebihi 5.

---

## 8. Hadiah

Total **NT$150.000**, dibagi rata NT$75.000 per kategori (Campus Self-Proposed & Designated Field). Per kategori, 8 tim menang:

| Penghargaan | Tim | Per tim | Subtotal |
|---|---|---|---|
| Juara 1 | 1 | NT$25.000 | NT$25.000 |
| Juara 2 | 1 | NT$15.000 | NT$15.000 |
| Juara 3 | 1 | NT$10.000 | NT$10.000 |
| Honorable mention | 5 | NT$5.000 | NT$25.000 |

Hadiah bisa tidak diberikan bila kualitas kurang; dewan juri boleh menyesuaikan jumlah/alokasi dalam batas total. Hadiah kena potong pajak penghasilan. Panitia bisa menambah special award (korporat, lapangan, keamanan, lintas disiplin) tergantung sponsor.

---

## 9. Jadwal

| Tahap | Tanggal |
|---|---|
| Aturan diumumkan & pendaftaran dibuka | **Situs: 08/12 (Rabu) · PDF: 28 Agustus 2026 (Jumat)** — ada selisih, ikuti situs resmi |
| Briefing & capacity-building workshop | 18 September 2026 (Jumat), 14:00–16:00 |
| **Pendaftaran & submisi penyisihan ditutup** | **16 Oktober 2026 (Jumat) 23:59** |
| Pengumuman finalis | 6 November 2026 (Jumat) |
| Batas submisi final | 13 November 2026 (Jumat) 23:59 |
| **Final & showcase** | **21 November 2026 (Sabtu)** |

Lokasi final: **The Great Roots Forestry Spa Resort**, Distrik Sanxia, New Taipei City — bersamaan dengan pameran & penghargaan TAAI 2026.

Panitia boleh menyesuaikan jadwal/format/tempat karena kondisi venue, bencana alam, wabah, masalah sistem, atau keadaan lain.

---

## 10. Keamanan, data, dan AI safety (kritis untuk track finansial)

Dari Pasal 14 aturan:

1. Pengumpulan/pemrosesan data pribadi harus patuh **Personal Data Protection Act** Taiwan: minimisasi data, de-identifikasi, access control, masa retensi, mekanisme penghapusan. Data pribadi/sensitif tanpa otorisasi sah **dilarang** dipakai.
2. **Sistem dilarang, tanpa otorisasi**, mengirim email atau dokumen resmi, **melakukan pembayaran**, menghapus data, mengubah nilai, menyetujui dokumen, mengendalikan peralatan, atau melakukan aksi lain yang berdampak substantif. Operasi berisiko tinggi **wajib** menyertakan konfirmasi manusia, tingkatan izin, dan pencatatan lengkap.
3. Tim harus menilai **prompt injection**, pemanggilan tool tanpa izin, kebocoran data, halusinasi, bias, input berbahaya, risiko supply chain, dan kegagalan layanan pihak ketiga — lalu mengusulkan proteksi, monitoring, dan pemulihan.
4. Bila terjadi kebocoran data/kredensial/akses tanpa izin → **segera hentikan** operasi terkait dan laporkan ke panitia & kontak lapangan. Dilarang menyembunyikan atau memperluas insiden lewat pengujian mandiri.
5. Panitia boleh meminta tim menghentikan fungsi tertentu, memakai data sintetis, membatasi demo publik, atau melakukan uji tambahan. Pelanggaran serius → diskualifikasi.

**Implikasi langsung untuk agent saham:** eksekusi order otomatis tanpa konfirmasi manusia melanggar Pasal 14.2 ("melakukan pembayaran"/aksi berdampak substantif). Desain yang benar adalah **decision support dengan human-in-the-loop**: agent menyaring, menjelaskan, memberi sitasi, dan memantau — manusia yang memutuskan. Ini bukan batasan, ini justru yang dinilai sebagai desain baik (15% bobot Safety di final).

---

## 11. HAKI, orisinalitas, resource pihak ketiga (Pasal 13)

- HAKI pada prinsipnya milik tim, kecuali ada perjanjian terpisah dengan kampus/pembimbing/penyedia lapangan/pihak ketiga — **wajib diungkap saat pendaftaran**.
- Tim memberi panitia hak pakai **tanpa kompensasi** atas judul, abstrak, gambar, materi presentasi, video demo, dan konten yang dirilis publik — untuk promosi, pameran hasil, pendidikan, dan diseminasi nirlaba. **Source code, data, dan konten rahasia tidak dipublikasikan** tanpa persetujuan terpisah pemegang hak.
- Ikut lomba **bukan** berarti menyerahkan hasil/hak secara cuma-cuma. Deployment lanjutan, alih teknologi, lisensi, pengadaan, atau kerja sama komersial butuh perjanjian terpisah.
- Karya harus orisinal. Memakai open source, model, dataset, API, generative AI, atau konten pihak ketiga: patuhi lisensi dan **ungkapkan sumber, tujuan, dan lingkup pemakaian**.
- Karya yang pernah ikut lomba/menang/dikomersialkan/didanai **boleh** diajukan, tapi harus mengungkap hasil sebelumnya dan menjelaskan secara spesifik fungsi baru, teknologi Agentic AI, dan validasi lapangan yang ditambahkan. **Penilaian fokus pada konten yang baru ditambahkan.**

---

## 12. Kejujuran, konflik kepentingan, dan banding (Pasal 15)

- Penilaian penyisihan anonim; bukti kolaborasi lapangan diverifikasi terpisah oleh staf administratif. Identitas tim boleh dibuka di final.
- Juri/penasihat/staf wajib menjaga kerahasiaan; yang punya konflik kepentingan langsung wajib mengungkap dan mengundurkan diri dari penilaian.
- Perjokian, plagiarisme, pemalsuan data, mengganggu tim lain, akses tanpa izin, menyembunyikan konflik kepentingan → pembatalan keikutsertaan/finalis/penghargaan, penarikan hadiah & sertifikat, plus tanggung jawab hukum.
- Skor & peringkat profesional dari juri **tidak bisa dibanding**. Keberatan atas kelayakan, prosedur administratif, perjokian, plagiarisme, atau konflik kepentingan harus diajukan dengan bukti dalam **7 hari** setelah pengumuman hasil. Keputusan panitia final.

---

## 13. Catatan strategis untuk track SYSTEX

1. **"Traceable" adalah kata kuncinya.** Deskripsi tantangan menyebut *traceable references*, dan panitia akan menyiapkan **gold answers**. Setiap klaim output harus punya sitasi ke dokumen MOPS/TWSE/TPEx yang spesifik — idealnya sampai level halaman/baris laporan.
2. **Bangun untuk test case yang belum terlihat.** Karena set evaluasi diumumkan belakangan, desain harus generalis di seluruh saham listed & OTC Taiwan, bukan hard-code beberapa emiten demo.
3. **Jangan lewatkan "proactive delivery" dan "behavioral feedback".** Dua tahap ini yang membedakan agent dari chatbot, dan sekaligus jadi bukti kuat untuk kriteria *Agentic Technical Depth* (20%). Kebanyakan tim kemungkinan berhenti di "personalized intelligence".
4. **Halusinasi angka finansial = risiko terbesar.** Siapkan lapisan verifikasi output yang mencocokkan angka hasil generasi dengan sumber terstruktur, dan tolak/eskalasi bila tidak cocok. Ini memenuhi butir 4 syarat minimum sekaligus kriteria Safety.
5. **Baseline itu wajib, bukan opsional.** Appendix 2 meminta perbandingan dengan proses manual, workflow kaku, atau model tunggal. Siapkan sejak awal — jangan dikejar di akhir.
6. **Bukti lapangan Level 1 harus jalan paralel dengan coding.** Wawancara investor tidak bisa dikerjakan di minggu terakhir, dan bobotnya 20% di penyisihan.
7. **Perhatikan syarat kelayakan peserta.** Aturan menyebut mahasiswa aktif di perguruan tinggi **di Taiwan**. Kalau status tim tidak sesuai, konfirmasi dulu ke panitia sebelum menginvestasikan waktu.
