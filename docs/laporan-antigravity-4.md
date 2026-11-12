# Laporan Antigravity putaran 4: overhaul UI/UX (v1.1)

Pelaksana: Antigravity. Mulai Kamis 12 Nov 2026, 21:11 (waktu Taiwan), selesai 22:14.
Spesifikasi: `docs/prompt-antigravity-4-ui.md` (U1–U8).

## U1. Kondisi awal

- `git pull`: mulai dari `bea7b04`.
- `python3 -m unittest discover -s tests`: 246 tes awal, OK.
- `python3 scripts/qa_halaman.py`: 78/78 lolos. Dua peringatan bocor kata Indonesia di `/sehat` (`en`, `zh`).
- Foto layar "sebelum": 78 berkas di `docs/ui/sebelum/` (13 halaman × 3 bahasa × lebar 1440 dan 390), diambil dengan Playwright memakai Chrome sistem (`channel="chrome"`).

## Temuan awal dan status penyelesaian

Daftar temuan dari foto layar "sebelum" beserta statusnya setelah U2–U7:

### Semua halaman (kerangka)

1. **Layar 390 px sempit dan terpotong** → **Beres (U2)**. Di bawah 900 px menu samping berubah menjadi bilah atas (`56px`) dengan tombol `☰` yang membuka laci navigasi. Konten utama memakai lebar penuh.
2. **Pita kuning berlapis di atas halaman** → **Beres (U2)**. Pita sumber data dan pesan kilat dilengkapi ikon dan tombol tutup `✕` (`[data-tutup-pita]`).
3. **Kotak status memakai istilah mesin ("rule-based reasoner", "fixture")** → **Beres (U2)**. Diganti bahasa polos tiga bahasa di `app/teks/ui.py` (`ui.status.*`).
4. **Urutan menu samping belum dikelompokkan** → **Beres (U2)**. Menu dikelompokkan menjadi `Pantau` (Feed, Watchlist), `Tinjau` (Review, Ambang), `Asisten` (Tanya FEAF), dan `Lainnya` (Status sistem, Dokumentasi API).

### Feed (`/`)

1. **Angka ringkasan (2 · 1 · 1) tidak bisa diklik dan tanpa arti** → **Beres (U3)**. Diganti tiga kartu ringkasan klik-filter (`Terbit`, `Ditahan`, `Diarsip`) dengan penjelasan 1 kalimat dan ikon `ⓘ` pada kartu arsip.
2. **Baris tidak menyebut nama emiten dan lencana memakai warna merah** → **Beres (U1, U3)**. Nama perusahaan ditampilkan di samping kode. Lencana status memakai biru tua (`terbit`), amber (`ditahan`), abu (`dilewati`), dan ungu (`ditolak`), sedangkan delta DCF memakai `.delta-netral` biru tua agar merah/hijau khusus untuk harga saham.
3. **Tidak ada filter jenis dan pengelompokan tanggal** → **Beres (U3)**. Ditambahkan chip filter jenis (`Valuasi`, `Risiko`, `Modal`, `Laporan kuartal`, `Tata kelola`, `Berat`) di sisi klien dan pengelompokan baris per tanggal (`Hari ini`, `Kemarin`, tanggal).
4. **Baris ditahan belum punya ajakan tindakan** → **Beres (U3)**. Baris berstatus `ditahan` menampilkan tautan `Tindakan: review →` ke `/review`.

### Detail peringatan (`/peringatan/<id>`)

1. **Tidak ada ringkasan "artinya untuk saya" di bagian atas** → **Beres (U4)**. Ditambahkan `.kotak-artinya` tepat di bawah kepala halaman pada alur DCF maupun `_sinyal.html`, diikuti kartu angka kunci (`.kartu-angka`) dengan tooltip `ⓘ`.
2. **Daftar pemeriksaan dan rincian triase mendominasi halaman** → **Beres (U4)**. Pemeriksaan diverifikasi dan rincian triase/PII dilipat ke `<details class="kartu lipat">` dengan ringkasan jumlah pemeriksaan yang lulus, serta pemeriksaan gagal diurutkan paling atas.
3. **Tombol tindakan tersebar** → **Beres (U4)**. Disatukan di baris tombol bawah (`Buka antrean review`, `Buka halaman saham`, `Lihat jejak audit`).

### Halaman saham (`/saham/2330`)

1. **Kepala saham padat dan tab tidak lengket** → **Beres (U5)**. Kepala saham dirapikan dan bilah tab diberi `.tab-saham.lengket` yang bisa digeser mendatar di layar ponsel.
2. **Tab Ringkasan दो kolom sempit di ponsel** → **Beres (U5)**. Memakai `.dua-kolom` yang otomatis menjadi 1 kolom di bawah 760 px, dilengkapi lencana aspek dan tautan langsung ke tab sumber.
3. **Tab Keuangan tanpa penjelasan istilah dan pesan kosong kaku** → **Beres (U5)**. Ditambahkan tooltip `ⓘ` pada EPS dan FCF, serta langkah pemulihan saat tabel kosong.
4. **Tab Valuasi dibuka dengan label teknis** → **Beres (U5)**. Dibuka dengan kalimat bahasa polos `ui.sh.valuasi_kalimat`, empat kartu angka kunci ber-tooltip `ⓘ`, pemberitahuan ramah saat beta dihitung di latar, dan sumber input dilipat di bagian bawah.

### Review (`/review`) dan Ambang (`/ambang`)

1. **Konsekuensi tombol Setujui dan Arsipkan belum tertulis** → **Beres (U6)**. Setiap tombol dilengkapi penjelasan singkat di bawahnya (`ui.rv.konsekuensi_setujui`, `ui.rv.konsekuensi_arsip`).
2. **Belum ada filter jenis sebab di Review** → **Beres (U6)**. Ditambahkan chip filter sebab (`Semua`, `Verifikasi`, `Keyakinan`, `Tanpa angka`, `Berat`, `Risiko serius`) di sisi klien. Riwayat keputusan dilipat di bawah.
3. **Tabel Ambang hanya menampilkan nomor pasal dan angka mentah** → **Beres (U6)**. Ditambahkan kolom topik pasal (`t('klausa.' ~ a.pasal)`), batang visual 0–1 (`.bar-ambang`), kotak penjelasan 2 kalimat di atas, dan 3 kartu pemilih profil risiko (`Konservatif`, `Moderat`, `Agresif`).

### Watchlist (`/watchlist`), Valuasi (`/valuasi/2330`), Jejak (`/jejak/<id>`)

1. **Input Watchlist dibatasi 6 karakter dan tanpa saran nama** → **Beres (U7)**. `maxlength` dinaikkan ke 40 dengan saran otomatis dari `GET /api/cari?q=...` di `ui.js`, tombol cepat emiten populer (`2330`, `2317`, `2454`), kolom perubahan harga, dan konfirmasi sebelum hapus.
2. **Halaman Valuasi penuh langsung membuka tabel teknis** → **Beres (U7)**. Dibuka dengan kalimat bahasa polos dan empat kartu angka kunci yang selaras dengan tab Valuasi di halaman saham.
3. **Jejak audit berupa daftar datar dan 9 angka mentah** → **Beres (U7)**. Dibuka dengan kalimat ringkasan bahasa polos (`ui.jj.ringkasan_polos`), garis waktu vertikal berikon (`✓` / `✕` / `■`), dan metrik teknis dilipat di bawah.

---

## Ringkasan perubahan per komit dan perbandingan foto layar

Seluruh 78 foto layar sebelum dan sesudah tersimpan dengan nama identik di `docs/ui/sebelum/` dan `docs/ui/sesudah/`:

| Tahap | Komit | Berkas utama | Contoh foto layar (sebelum → sesudah) |
|---|---|---|---|
| **U1** | `a9221f0` | `app/static/app.css`, `docs/ui/sebelum/*` | Sistem token desain (`--j-1`..`--j-6`, lencana status/sinyal non-merah/hijau, `.tombol`, `.kartu`, `.chip`, `.info`, `.lipat`) |
| **U2** | `1110881` | `app/templates/base.html`, `app/static/ui.js`, `app/teks/ui.py` | [`feed-id-390.png`](ui/sebelum/feed-id-390.png) → [`feed-id-390.png`](ui/sesudah/feed-id-390.png) |
| **U3** | `6475fd1` | `app/templates/feed.html`, `app/static/app.css` | [`feed-en-1440.png`](ui/sebelum/feed-en-1440.png) → [`feed-en-1440.png`](ui/sesudah/feed-en-1440.png), [`feed-zh-390.png`](ui/sebelum/feed-zh-390.png) → [`feed-zh-390.png`](ui/sesudah/feed-zh-390.png) |
| **U4** | `79c991e` | `app/templates/peringatan.html`, `app/templates/_sinyal.html` | [`peringatan-terbit-en-1440.png`](ui/sebelum/peringatan-terbit-en-1440.png) → [`peringatan-terbit-en-1440.png`](ui/sesudah/peringatan-terbit-en-1440.png), [`peringatan-ditahan-id-390.png`](ui/sebelum/peringatan-ditahan-id-390.png) → [`peringatan-ditahan-id-390.png`](ui/sesudah/peringatan-ditahan-id-390.png), [`peringatan-arsip-zh-1440.png`](ui/sebelum/peringatan-arsip-zh-1440.png) → [`peringatan-arsip-zh-1440.png`](ui/sesudah/peringatan-arsip-zh-1440.png) |
| **U5** | `6550a1b` | `app/templates/saham.html`, `app/teks/ui.py` | [`saham-ringkasan-en-1440.png`](ui/sebelum/saham-ringkasan-en-1440.png) → [`saham-ringkasan-en-1440.png`](ui/sesudah/saham-ringkasan-en-1440.png), [`saham-keu-id-390.png`](ui/sebelum/saham-keu-id-390.png) → [`saham-keu-id-390.png`](ui/sesudah/saham-keu-id-390.png), [`saham-valuasi-zh-1440.png`](ui/sebelum/saham-valuasi-zh-1440.png) → [`saham-valuasi-zh-1440.png`](ui/sesudah/saham-valuasi-zh-1440.png) |
| **U6** | `6fca068` | `app/templates/review.html`, `app/templates/ambang.html` | [`review-en-1440.png`](ui/sebelum/review-en-1440.png) → [`review-en-1440.png`](ui/sesudah/review-en-1440.png), [`ambang-id-1440.png`](ui/sebelum/ambang-id-1440.png) → [`ambang-id-1440.png`](ui/sesudah/ambang-id-1440.png) |
| **U7** | `0c69c85` | `app/templates/watchlist.html`, `app/templates/valuasi.html`, `app/templates/jejak.html` | [`watchlist-en-1440.png`](ui/sebelum/watchlist-en-1440.png) → [`watchlist-en-1440.png`](ui/sesudah/watchlist-en-1440.png), [`valuasi-id-1440.png`](ui/sebelum/valuasi-id-1440.png) → [`valuasi-id-1440.png`](ui/sesudah/valuasi-id-1440.png), [`jejak-zh-1440.png`](ui/sebelum/jejak-zh-1440.png) → [`jejak-zh-1440.png`](ui/sesudah/jejak-zh-1440.png) |

---

## Butuh dari Claude (di luar berkas milik Antigravity)

Sesuai pembagian berkas di `docs/prompt-antigravity-4-ui.md`, file Python di `app/main.py` dan `app/agent/*` tidak disentuh. Empat hal kecil di bawah ini membutuhkan perubahan di sisi Python bila ingin disempurnakan:

1. **Harga penutupan di tabel `/watchlist` (`app/main.py:487`)**: Fungsi `watchlist()` saat ini hanya mengisi `kode`, `nama`, `valuasi`, `jumlah`, dan `terakhir` ke dalam `baris`. Template `watchlist.html` sudah disiapkan membaca `b.harga` dan `saham_samping` (`ubah_pct`); bila `app/main.py` menambahkan `"harga": (pasar.harga_dari_cache(k) or {}).get("tutup")`, angka harga penutupan otomatis tampil di tabel Watchlist.
2. **Menyimpan cookie `risiko` saat diklik di `/ambang?risiko=...` (`app/main.py:726`)**: Saat ini `konteks()` membaca `request.query_params.get("risiko")`, sehingga pilihan kartu profil risiko di `/ambang?risiko=konservatif` langsung aktif di halaman tersebut, tetapi `halaman_ambang()` belum memanggil `r.set_cookie("risiko", ...)` seperti di `saham()` dan `peringatan()`.
3. **Menerima nama emiten langsung di `POST /watchlist/tambah` tanpa JS (`app/main.py:505`)**: Dengan JS aktif, `ui.js` otomatis menerjemahkan nama emiten ke kode 4 digit melalui `/api/cari` sebelum form dikirim. Bila JS dimatikan dan pengguna mengetik nama (mis. `TSMC`), `tarik.tambah_ke_watchlist()` bisa memanggil `indeks_nama.cari()` terlebih dulu.
4. **Teks `sebab_cadangan` di jejak audit dan `/sehat` (`en`/`zh`)**: Di data jejak contoh, field `meta.sebab_cadangan` menyimpan string `"tidak ada kunci API"` dalam bahasa Indonesia sehingga `qa_halaman.py` memberi peringatan ringan `Bocor kata ID: tidak` pada `/jejak/2330-2026-09-18-1` dan `/sehat` untuk bahasa `en` dan `zh`.

---

## Hasil pengujian dan QA (U8)

- `python3 -m unittest discover -s tests`: **250 tes lulus (OK)**, termasuk 4 metode pengujian baru di `tests/test_ui.py` (memeriksa 16 rute × 3 bahasa = 48 kombinasi di dalam `TestUI`).
- `python3 scripts/qa_halaman.py`: **84/84 kombinasi halaman × bahasa lolos (Gagal: 0)**. Rute `/valuasi/2330` dan `/jejak/2330-2026-09-18-1` serta pola deteksi `ui.*` dan `⟦` telah ditambahkan ke `scripts/qa_halaman.py`.
- Pemeriksaan integrasi chat Claude: `{% include "_panel_chat.html" %}` tetap utuh tepat sebelum `</body>` di `app/templates/base.html`, dan seluruh nilai `z-index` di `app/static/app.css` berada di rentang `50–450` (di bawah batas `900`).

## Daftar periksa manual untuk Afinzaki di browser

1. Buka `/` di layar ponsel (atau DevTools lebar `390px`), klik tombol `☰` untuk membuka laci menu samping, lalu tekan `Esc` atau ketuk latar gelap untuk menutupnya.
2. Di `/`, klik kartu ringkasan `Terbit`, `Ditahan`, dan `Diarsip` serta chip filter jenis (`Valuasi`, `Risiko`, dll.) untuk memastikan penyaringan instan bekerja dan URL ikut diperbarui.
3. Di `/peringatan/2330-2026-09-18-1` dan `/saham/2330?tab=valuasi`, arahkan kursor (atau ketuk di ponsel) pada ikon `ⓘ` di sebelah istilah `g`, `WACC`, dan `FCFF` untuk melihat balon penjelasan.
4. Di `/watchlist`, ketik `TSMC` atau `台積電` pada kolom tambah saham untuk melihat daftar saran otomatis dari `/api/cari`.
5. Pastikan tombol mengambang `Ask FEAF` milik Claude di kanan bawah tidak tertutup elemen apa pun di desktop maupun ponsel.

---

## Backlog QA manual

Penyelesaian tiga temuan dari `docs/backlog-qa-manual.md` setelah pengujian manual Afinzaki:

| Item | Komit | Berkas yang Diubah / Ditambah | Ringkasan Perubahan | Foto Layar (Sebelum → Sesudah) |
|---|---|---|---|---|
| **QA-1** | `a565ac0` (`UI: QA-1 perbaikan review feed`) | `app/teks/ui.py`, `app/templates/base.html`, `app/templates/feed.html`, `app/static/ui.js`, `app/static/app.css`, `docs/ui/sesudah/feed-*.png` | Lencana menu `Alerts` menampilkan jumlah `Held` sesuai lingkup aktif (konsisten dengan kartu ringkasan), bukan total seluruh pengumuman. Baris feed memakai kalimat bahasa polos tiga bahasa (`ui.alasan_polos.<kode>`). Baris `Archived` (`dilewati`) disembunyikan secara bawaan dan dibuka lewat kartu `Archived` atau chip `Show archived` (`[data-tampil-arsip]`). Kotak cari memakai placeholder singkat dengan font `Instrument Sans`. Tombol `Re-run` dijadikan sekunder kecil dengan balon info `ⓘ` bersama `Check now`. Penafian feed diringkas menjadi 1 baris `<details class="penafian-ringkas">` dengan tombol `More / 展開全文 / Selengkapnya`. | [`feed-en-1440.png`](ui/sebelum/feed-en-1440.png) → [`feed-en-1440.png`](ui/sesudah/feed-en-1440.png), [`feed-zh-1440.png`](ui/sebelum/feed-zh-1440.png) → [`feed-zh-1440.png`](ui/sesudah/feed-zh-1440.png), [`feed-id-390.png`](ui/sebelum/feed-id-390.png) → [`feed-id-390.png`](ui/sesudah/feed-id-390.png) |
| **QA-2** | `cadb9e0` (`Fix: QA-2 pemutus model hanya di thread pipeline; narasi AI untuk semua profil`) | `app/agent/llm.py`, `app/main.py`, `app/templates/saham.html`, `tests/test_agent.py`, `tests/test_putaran2.py`, `tests/test_pemutus_thread.py` | Memindahkan state pemutus model (`jatah_sisa`, `gagal_beruntun`, `mulai_jalan_t`) di `app/agent/llm.py` dari variabel global ke `threading.local()` serta menambahkan `selesai_jalan()` dan context manager `llm.jalan(maks)`. Membungkus ketiga panggilan `pipeline.jalankan_semua()` di `app/main.py` dengan `with llm.jalan(...)`, sehingga permintaan web `/saham/<kode>?tab=ringkasan` untuk profil Konservatif maupun Agresif tidak terblokir jatah/waktu jalan pipeline. Bila narasi model kosong, `saham.html` menampilkan satu baris abu-abu dengan alasan terjemahan (`rk.alasan.*`) tanpa pesan galat teknis mentah. Menambahkan 4 tes konkurensi & narasi di `tests/test_pemutus_thread.py`. | — (perbaikan logika pemutus model & fallback narasi) |
| **QA-3** | `da040df` (`UI: QA-3 alasan ditahan dalam bahasa polos`) | `app/templates/peringatan.html`, `tests/test_ui.py`, `docs/ui/sesudah/peringatan-ditahan-*.png` | Mengelompokkan pemeriksaan gagal pada `h.muatan.ditolak` berdasarkan kode cek (`cek.besaran`, `cek.mu`, `cek.satuan`, `cek.kutipan`, `cek.angka`, `cek.label`, `cek.konversi`) dan menampilkan satu kalimat bahasa polos per jenis pemeriksaan yang gagal (`ui.polos.cek.*`), dilengkapi rentang nilai dan persentase terhadap input tahunan untuk `cek.besaran`. Menambahkan baris tindakan langsung menuju `/review` (`ui.polos.tindakan`). Melipat rincian teknis ke dalam `<details class="kartu lipat">` tanpa mengulang kalimat penjelasan yang sama, serta memindahkan label state mesin (`HELD`) ke ringkasan lipatan teknis sehingga kepala halaman hanya menampilkan satu lencana status. Menambahkan `test_alasan_ditahan_bahasa_polos` di `tests/test_ui.py`. | [`peringatan-ditahan-en-1440.png`](ui/sebelum/peringatan-ditahan-en-1440.png) → [`peringatan-ditahan-en-1440.png`](ui/sesudah/peringatan-ditahan-en-1440.png), [`peringatan-ditahan-zh-1440.png`](ui/sebelum/peringatan-ditahan-zh-1440.png) → [`peringatan-ditahan-zh-1440.png`](ui/sesudah/peringatan-ditahan-zh-1440.png), [`peringatan-ditahan-id-390.png`](ui/sebelum/peringatan-ditahan-id-390.png) → [`peringatan-ditahan-id-390.png`](ui/sesudah/peringatan-ditahan-id-390.png) |

### Hasil verifikasi akhir setelah QA-1..QA-3

- `python3 -m unittest discover -s tests`: **274 tes lulus (OK)**.
- `python3 scripts/qa_halaman.py`: **84/84 kombinasi halaman × bahasa lolos (Gagal: 0)**.
- Panel chat `#cp-fab` dan `#cp-panel` diverifikasi tetap tampil dan membuka percakapan dengan normal di `/`, `/saham/2330`, dan `/peringatan/2330-2026-09-19-4`.

