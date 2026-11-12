# Prompt Antigravity putaran 4: overhaul UI/UX (v1.1, untuk demo 21 Nov)

Untuk Afinzaki. Tempel **U1** ke Antigravity (satu agent, folder repo ini sebagai workspace).
Setiap prompt di akhirnya menyuruh Antigravity membuka prompt berikutnya di berkas ini, jadi
cukup tempel sekali. Kalau rantainya berhenti, tempel nomor berikutnya secara manual.

Sebelum ditinggal:
1. Laptop dicolok ke listrik, sleep dimatikan, Wi-Fi tersambung.
2. Di setelan Antigravity, izinkan perintah terminal dan sunting berkas tanpa persetujuan.
3. `git pull` dulu: versi 1.0.0 sudah dikunci di `main` (commit "Rilis 1.0.0").

Setelah selesai: kirim `docs/laporan-antigravity-4.md` ke Claude, plus hasil review kamu
sendiri. Claude meninjau sebelum kamu Deploy.

| No | Isi |
|---|---|
| U1 | Persiapan, foto layar "sebelum", sistem desain |
| U2 | Kerangka: menu samping, versi ponsel, komponen dasar |
| U3 | Feed peringatan |
| U4 | Detail peringatan |
| U5 | Halaman saham (6 tab) |
| U6 | Review dan Ambang |
| U7 | Watchlist, Valuasi, Jejak audit |
| U8 | QA tiga bahasa, foto layar "sesudah", laporan |

---

## Aturan yang berlaku untuk SEMUA prompt (baca sekali, patuhi terus)

**Tujuan.** Tampilan yang ramah untuk pengguna non-teknis: analis atau investor ritel di
Taiwan yang membuka aplikasi untuk pertama kali, dan juri lomba yang punya 5 menit. Pengguna
harus langsung paham **apa yang terjadi, kenapa penting, dan apa yang bisa dilakukan**,
tanpa membaca istilah teknis. Detail teknis (JSON, daftar cek lengkap, token) tetap ada,
tapi dilipat.

**Yang BOLEH diubah:**
- `app/templates/*.html` kecuali yang dimiliki Claude (lihat di bawah)
- `app/static/app.css`
- berkas baru `app/static/ui.js` (JavaScript biasa, tanpa framework, tanpa CDN baru)
- berkas baru `app/teks/ui.py` untuk semua teks baru (format sama dengan `app/teks/tata_kelola.py`:
  `"kunci": ("English", "繁體中文", "Bahasa Indonesia")`). Kunci yang sudah ada **tidak boleh
  ditimpa** (aplikasi menolak start kalau ditimpa); bikin kunci baru dengan awalan `ui.`
- `tests/test_ui.py` (baru) dan `scripts/qa_halaman.py` (boleh ditambah halaman)

**Yang TIDAK BOLEH disentuh:**
- `app/agent/*`, `app/*.py` selain `app/teks/ui.py` (logika, rute, data), `scripts/dcf.py`,
  `eval/*`, `valuation/*`
- Milik putaran chat (`docs/prompt-antigravity-5-chat.md`, bisa jalan paralel): `app/templates/_panel_chat.html`,
  `app/templates/chat.html`, `app/static/chat.js`, `app/static/chat.css`, `app/chat.py`,
  `app/teks/chat.py`
- Di `app/templates/base.html`, baris `{% include "_panel_chat.html" %}` tepat sebelum
  `</body>` **tidak boleh dipindah atau dihapus**. Panel chat akan muncul sebagai tombol
  bulat di pojok kanan bawah (56×56 px, jarak 20 px dari tepi) dan panel 400 px dari kanan.
  Jangan taruh elemen tetap (fixed/sticky) di pojok kanan bawah, dan jangan pakai `z-index`
  di atas 900.

Kalau sebuah perbaikan butuh data baru dari server (mis. angka yang belum dikirim ke
template), **jangan ubah Python**. Catat di laporan bagian "Butuh dari Claude" dan
lanjutkan dengan data yang ada.

**Aturan produk yang tidak boleh dilanggar:**
1. Tidak ada label beli/jual/target harga di mana pun. Penafian (`_penafian.html`) tetap tampil.
2. Merah = naik, hijau = turun (konvensi Taiwan), hanya untuk pergerakan harga. Status
   agent (terbit/ditahan/diarsip) dan tingkat sinyal (info/perhatian/serius) memakai warna
   lain yang tidak bisa tertukar dengan arah harga.
3. Tidak ada nama orang (pejabat, akuntan, juru bicara) yang ditampilkan.
4. Semua teks lewat i18n, tiga bahasa. Tidak ada teks Indonesia yang bocor ke EN/中文.
5. Tanpa jaringan baru: tidak ada CDN, font, atau gambar dari luar selain Google Fonts yang
   sudah dipakai.
6. Semua tes lama tetap lulus: `python3 -m unittest discover -s tests`.

**Prinsip desain (pakai di setiap halaman):**
- **Satu kalimat di atas.** Setiap halaman detail dibuka dengan satu kalimat polos yang
  menjawab "apa artinya untuk saya", baru kemudian angka.
- **Lipat yang teknis.** Daftar pemeriksaan, JSON, token, dan versi prompt masuk
  `<details>` dengan ringkasan seperti "7 dari 7 pemeriksaan lolos".
- **Istilah dijelaskan di tempat.** Istilah seperti WACC, pertumbuhan tersirat, 背書保證,
  materialitas diberi tooltip kecil (ikon ⓘ, `title` + versi yang bisa disentuh di ponsel).
  Buat satu komponen dan pakai ulang.
- **Status selalu dengan arti.** Lencana "Ditahan" selalu disertai sebabnya dalam bahasa
  polos dan tindakan berikutnya ("Menunggu review analis → buka antrean").
- **Kosong bukan buntu.** Setiap keadaan kosong memberi langkah berikutnya (tombol).
- **Hierarki tipografi.** Teks isi minimal 14 px dengan Instrument Sans; IBM Plex Mono
  hanya untuk angka, kode saham, dan label kecil. Kurangi huruf kapital kecil (kicker).
- **Aksesibilitas.** Kontras minimal WCAG AA, fokus keyboard terlihat, semua tombol
  ikon punya `aria-label`, target sentuh minimal 40×40 px di ponsel.
- **Responsif.** Harus bisa dipakai di lebar 390 px (ponsel) dan 1440 px. Tabel lebar
  digeser horizontal di dalam kartunya, bukan seluruh halaman.
- **Konsisten.** Satu set komponen: tombol utama/sekunder/bahaya, lencana, kartu, chip
  filter, tooltip, keadaan kosong, tab. Didefinisikan sekali di `app.css` (bagian
  "Sistem desain") dan dipakai di semua halaman. Hapus `style="..."` inline sebanyak
  mungkin, pindahkan ke kelas.
- Token warna dari `design/README.md` tetap jadi dasar (navy, amber, naik, turun). Boleh
  menambah token netral.

**Cara bekerja:** commit per prompt dengan awalan `UI:` dan push ke `main`. Setelah tiap
prompt: jalankan tes, `python3 scripts/qa_halaman.py` (harus 100% lolos), dan ambil foto layar
halaman yang diubah. Lalu lanjut ke prompt berikutnya.

**Foto layar:** pakai Playwright (sudah terpasang di laptop? kalau belum: `pip install
playwright && playwright install chromium`). Jalankan server lokal dengan
`SENTINEL_SERTAKAN_CONTOH=1 uvicorn app.main:app --port 8000`, lalu ambil layar dengan
cookie `bahasa=en|zh|id` di lebar 1440 dan 390. Simpan ke `docs/ui/sebelum/` dan
`docs/ui/sesudah/` dengan nama `<halaman>-<bahasa>-<lebar>.png`.

---

## U1 · Persiapan

```
Baca docs/prompt-antigravity-4-ui.md bagian "Aturan yang berlaku untuk SEMUA prompt" sampai
habis. Patuhi aturan itu di semua langkah.

1. git pull, lalu jalankan python3 -m unittest discover -s tests dan
   python3 scripts/qa_halaman.py. Catat hasilnya.
2. Jalankan server lokal dengan contoh (SENTINEL_SERTAKAN_CONTOH=1) dan ambil foto layar
   "sebelum" untuk halaman: / , /peringatan/<satu id terbit>, /peringatan/<satu id ditahan>,
   /saham/2330 (tab ringkasan, stream, keu, valuasi), /review, /ambang, /watchlist,
   /valuasi/2330, /jejak/<satu id> — tiga bahasa, lebar 1440 dan 390. Simpan di
   docs/ui/sebelum/.
3. Lihat semua foto itu dan tulis di docs/laporan-antigravity-4.md bagian "Temuan awal":
   per halaman, 3–5 masalah keramahan yang paling mengganggu pengguna awam (bahasa teknis,
   hierarki, keadaan kosong, tampilan ponsel, kontras, dsb.).
4. Tambahkan bagian "Sistem desain" di awal app/static/app.css: token (warna, jarak 4/8/12/16/24/32,
   radius, bayangan, ukuran huruf), dan komponen: .tombol (utama, .sekunder, .bahaya),
   .lencana, .kartu, .chip (filter), .info (tooltip ⓘ), .kosong (keadaan kosong + tombol),
   .tab. Komponen lama yang sudah dipakai template jangan dihapus dulu; ganti pemakaiannya
   di prompt berikutnya, lalu hapus yang tidak terpakai di U8.
5. Commit "UI: U1 sistem desain + foto sebelum". Push.

Lalu buka docs/prompt-antigravity-4-ui.md dan kerjakan U2.
```

## U2 · Kerangka dan versi ponsel

```
Kerjakan app/templates/base.html dan app.css (jangan sentuh baris include _panel_chat.html).

1. Menu samping dikelompokkan dengan judul kecil:
   - Pantau: Peringatan (feed), Watchlist
   - Tinjau: Review (dengan jumlah antrean), Ambang
   - Tanya FEAF
   - Lainnya: API
   Daftar "Saham saya" dan kotak status tetap ada; kotak status ditulis dalam bahasa
   polos ("Agent memakai Gemini 3.6 Flash · data terakhir ditarik 10 menit lalu").
2. Di bawah 900 px: menu samping berubah jadi bilah atas (logo, kotak cari, tombol ☰) dan
   menu muncul sebagai laci dari kiri. Kotak cari tetap mudah dijangkau.
3. Tambah "remah roti" (breadcrumb) kecil di atas judul halaman detail
   (Peringatan › 2330 › judul; Saham › 2330 › Valuasi).
4. Pita "data contoh" dan pesan kilat dibuat lebih jelas dengan ikon dan tombol tutup.
5. Uji: tes, QA, foto layar base di 1440 dan 390. Commit "UI: U2 kerangka + ponsel". Push.

Lalu kerjakan U3.
```

## U3 · Feed peringatan

```
Kerjakan app/templates/feed.html.

1. Ringkasan atas jadi tiga kartu yang bisa diklik dan berfungsi sebagai filter:
   Terbit · Ditahan (menunggu Anda) · Diarsip. Tiap kartu punya satu baris penjelasan polos.
2. Chip filter jenis: Valuasi, Risiko, Modal, Laporan kuartal, Tata kelola, Berat
   (pakai parameter URL di sisi klien bila server tidak mendukung; JANGAN ubah Python —
   filter di sisi klien dengan data-atribut pada baris sudah cukup).
3. Baris peringatan dibaca dalam satu tarikan mata: kode + nama emiten, judul, lalu satu
   kalimat "kenapa" (alasan yang sudah ada), lencana status dan tingkat sinyal di kanan.
   Baris ditahan menampilkan "Tindakan: review" yang menuju /review.
4. Tanggal dikelompokkan (Hari ini / Kemarin / tanggal).
5. Keadaan kosong: jelaskan dan beri tombol "Tambah saham ke watchlist" dan "Periksa sekarang".
6. Tooltip ⓘ pada "Kenapa sebagian besar diarsip?".
7. Uji, foto layar, commit "UI: U3 feed". Push.

Lalu kerjakan U4.
```

## U4 · Detail peringatan

```
Kerjakan app/templates/peringatan.html dan app/templates/_sinyal.html.

Urutan baru, dari atas:
1. Remah roti, kode + nama emiten, judul pengumuman, tanggal, lencana status besar.
2. Kotak "Artinya" — satu kalimat polos: untuk terbit, perubahan valuasi atau sinyal; untuk
   ditahan, kenapa dan apa yang ditunggu; untuk diarsip, kenapa tidak relevan. Pakai alasan
   yang sudah ada di data (tr(h.alasan_i18n)), jangan mengarang.
3. Angka kunci dalam 2–4 kartu kecil (mis. g tersirat sebelum → sesudah, nilai transaksi,
   rasio terhadap ekuitas). Pakai data yang sudah ada.
4. "Dari dokumen asli": kutipan + tautan MOPS.
5. Pemeriksaan: dilipat, ringkasan "7 dari 7 pemeriksaan lolos" atau "2 gagal: mata uang,
   satuan". Saat dibuka, cek yang gagal di atas.
6. Tombol: Lihat jejak audit, Buka halaman saham, (untuk ditahan) Buka antrean review.
7. Penafian tetap ada.
8. Uji dengan kasus terbit, ditahan (mata uang asing), dan arsip; tiga bahasa; ponsel.
   Commit "UI: U4 detail". Push.

Lalu kerjakan U5.
```

## U5 · Halaman saham

```
Kerjakan app/templates/saham.html (6 tab: ringkasan, stream, stats, keu, valuasi, profil).

1. Kepala: kode, nama, harga besar dengan perubahan (merah naik / hijau turun), tanggal data,
   tombol "+ Watchlist" bila belum dipantau.
2. Tab lengket (sticky) saat menggulir; di ponsel tab bisa digeser.
3. Tab ringkasan: kesimpulan di atas dalam kartu, lalu "Kekuatan" dan "Perlu diperhatikan"
   sebagai dua kolom (satu kolom di ponsel). Tingkat sinyal dengan lencana yang sama
   seperti feed.
4. Tab keu: tabel tetap, tapi kolom pertama lengket, angka rata kanan, baris total tebal,
   tombol periode lebih jelas. Tooltip ⓘ untuk istilah (EPS, ROE, arus kas bebas).
5. Tab valuasi: mulai dengan satu kalimat "Harga sekarang mengasumsikan pertumbuhan X% per
   tahun selamanya" lalu angka; tooltip WACC, g tersirat; sensitivitas tetap.
6. Keadaan memuat (valuasi beta) dan galat FinMind ditulis polos dengan langkah berikutnya.
7. Uji 2330 dan satu emiten TPEx, tiga bahasa, ponsel. Commit "UI: U5 saham". Push.

Lalu kerjakan U6.
```

## U6 · Review dan Ambang

```
Kerjakan app/templates/review.html dan app/templates/ambang.html.

Review:
1. Satu kartu per pengumuman yang ditahan: judul, sebab dalam bahasa polos, angka yang
   ditarik + kutipan, tautan dokumen.
2. Dua tombol jelas: "Setujui & terbitkan" (utama) dan "Tolak / arsipkan" (sekunder), dengan
   kalimat konsekuensinya di bawah tombol. Isian alasan tetap ada (jangan ubah nama field
   form dan action-nya).
3. Filter jenis sebab di atas (chip, sisi klien).
4. Riwayat keputusan dilipat di bawah.

Ambang:
1. Jelaskan di atas dalam 2 kalimat apa itu ambang dan bagaimana 👍/👎 mengubahnya.
2. Tabel per pasal dengan nama pasal polos, nilai ambang sebagai bar kecil 0–1, dan
   riwayat perubahan dilipat.
3. Pemilih profil risiko (konservatif/moderat/agresif) dengan penjelasan satu kalimat per profil.

Jangan ubah nama field form, method, atau action. Uji, commit "UI: U6 review + ambang". Push.

Lalu kerjakan U7.
```

## U7 · Watchlist, Valuasi, Jejak audit

```
Watchlist (watchlist.html):
1. Isian tambah saham menerima nama atau kode, dengan saran otomatis dari GET /api/cari?q=
   (sudah ada) memakai app/static/ui.js. Tetap berfungsi tanpa JavaScript.
2. Tabel: kode, nama, harga, perubahan, jumlah peringatan, tombol hapus (dengan konfirmasi).
3. Keadaan kosong dengan contoh: 2330 台積電, 2317 鴻海, 2454 聯發科.

Valuasi (valuasi.html): sama dengan tab valuasi di U5 (pakai ulang komponennya), sumber
tiap input tetap terlihat.

Jejak audit (jejak.html):
1. Ringkasan atas dalam bahasa polos: "Agent menyelesaikan 9 langkah dalam 1,2 detik,
   memanggil model 1 kali, dan menahan pengumuman ini karena …".
2. Langkah sebagai garis waktu vertikal dengan ikon status (lolos/ditolak/berhenti).
3. Data JSON tetap dilipat (filter `jejak_bahasa` dan `state` jangan dihapus).

Uji, commit "UI: U7 watchlist + valuasi + jejak". Push.

Lalu kerjakan U8.
```

## U8 · QA dan laporan

```
1. Hapus kelas CSS lama yang tidak terpakai lagi (cek dengan grep di templates).
2. Tambahkan halaman baru yang belum dicek ke scripts/qa_halaman.py bila ada. Jalankan:
   python3 -m unittest discover -s tests, python3 scripts/qa_halaman.py (harus 100%).
3. Tulis tests/test_ui.py: semua halaman utama 200 di tiga bahasa, tidak ada "⟦",
   tidak ada kata "beli/jual/buy/sell" di luar penafian, baris include _panel_chat.html
   masih ada di base.html.
4. Ambil foto layar "sesudah" untuk halaman yang sama dengan U1 (tiga bahasa, 1440 dan 390)
   ke docs/ui/sesudah/.
5. Lengkapi docs/laporan-antigravity-4.md:
   - Ringkasan perubahan per halaman (sebelum → sesudah, tautan foto layar)
   - Temuan awal mana yang sudah dan belum teratasi
   - "Butuh dari Claude": data atau rute yang perlu ditambah di Python
   - Hasil tes dan QA
   - Hal yang perlu dicek manual oleh Afinzaki
6. Commit "UI: U8 QA + laporan". Push. Selesai — beri tahu Afinzaki.
```
