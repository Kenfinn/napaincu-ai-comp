# Prompt multi-agent Antigravity (putaran 2)

Untuk Afinzaki. Putaran 2 bisa dikerjakan tiga agent Antigravity sekaligus lewat Agent
Manager, di folder repo yang sama. Spesifikasi tiap item tetap di
[`prompt-antigravity-2.md`](./prompt-antigravity-2.md). Berkas ini hanya mengatur siapa
mengerjakan apa, urutannya, dan cara mereka tidak saling menimpa.

Kalau Agent Manager tidak tersedia, pakai satu agent dengan prompt
`prompt-antigravity-2.md`. Aturan "lanjut otomatis" di bagian 3 di bawah tetap berlaku.

## Cara menjalankan

1. Buka Agent Manager, buat tiga agent di workspace repo ini.
2. Tempel **Prompt bersama** ke ketiganya, lalu tambahkan **Prompt peran** yang sesuai
   (Agent DATA, Agent WEB, Agent QA) di bawahnya.
3. Jalankan ketiganya. Mereka berkoordinasi lewat `docs/papan-agen.md`. Kamu cukup
   memantau berkas itu dan `docs/rencana-dan-status.md`.
4. Selesai bila Agent QA menulis `docs/laporan-antigravity-2.md` dan papan menunjukkan
   semua item ✅ atau ❌ dengan alasan. Kirim laporan itu ke Claude.

## Pembagian

| Fase | Agent DATA | Agent WEB | Agent QA |
|---|---|---|---|
| 1 | R1 beta resmi | R2 penafian | R4 pengungkapan pihak ketiga |
| 2 | D-c utang lancar, lalu D-b 2330 otomatis | R3 kunci baca, lalu D-a semua emiten | Periksa item yang sudah ✅ dari fase 1 |
| 3 | B3 sitasi MOPS | Bantu QA: uji tiga bahasa semua halaman | Periksa fase 2–3, pemeriksaan akhir, laporan |

Kenapa dibagi begini: DATA hanya menyentuh berkas valuasi dan data, WEB hanya menyentuh
halaman, konfigurasi, dan penarik. Satu-satunya berkas yang disentuh berdua adalah
`app/templates/saham.html`, jadi ada aturan giliran untuk berkas itu (bagian 2).

---

````text
# PROMPT BERSAMA (tempel ke ketiga agent)

Kamu satu dari tiga agent Antigravity yang mengerjakan putaran 2 proyek FEAF bersamaan,
di folder dan branch yang sama (`main`). Claude bekerja di repo yang sama dari tempat lain
(chatbot dan evaluasi) dan push ke `main`.

## 1. Bacaan wajib sebelum mulai
docs/prompt-antigravity-2.md (spesifikasi item, aturan kerja bagian 1, pemeriksa, format
laporan bagian 5), docs/rencana-dan-status.md, docs/konteks-sesi.md, DESIGN.md.
Semua aturan di bagian 0, 1, dan 2 berkas itu berlaku untukmu. Pasang dan pakai skill
anti-slop (kode/UI, mode "during") dan humanizer (setiap berkas .md) seperti di bagian 0.1.

## 2. Aturan supaya tidak saling menimpa
- Kepemilikan berkas mengikuti tabel "Berkas per agent" di bawah. Jangan menyunting berkas
  milik agent lain. Butuh perubahan di sana? Tulis permintaan di docs/papan-agen.md bagian
  "Permintaan", pemiliknya yang mengerjakan.
- app/templates/saham.html dipakai DATA dan WEB. Sebelum menyunting, tulis baris
  "KUNCI saham.html: <agent> <waktu>" di papan; setelah commit, ganti jadi "LEPAS".
  Jangan menyunting saat agent lain memegang kunci; kerjakan hal lain dulu.
- Teks baru tiga bahasa: hanya di berkas milikmu app/teks/data.py (DATA), app/teks/web.py
  (WEB), app/teks/qa.py (QA). Format `T = {"kunci": ("English", "中文", "Indonesia")}`.
- Commit HANYA berkas milikmu: `git add <path> <path>`. DILARANG `git add -A`,
  `git add .`, `git commit -a`, `git stash`, `git checkout -- <berkas orang lain>`, atau
  `git reset --hard`. Folder kerja berisi perubahan agent lain yang belum di-commit.
- Push: `git pull --rebase origin main` lalu `git push origin main`. Kalau rebase bentrok
  di berkas yang bukan milikmu, `git rebase --abort`, tunggu 2 menit, ulangi. Jangan
  menyelesaikan bentrok di berkas orang lain.
- Tes gagal: lihat berkas mana yang gagal. Kalau di area agent lain yang sedang bekerja,
  tulis di papan bagian "Galat" dan ulangi tes 5 menit kemudian. Jangan memperbaiki area
  orang lain. Commit milikmu boleh jalan bila semua tes di areamu lulus dan kegagalan lain
  sudah tercatat di papan.

## 3. Lanjut otomatis
Untuk setiap item di antreanmu, urut:
  a. tulis di papan: item → 🔄 (nama agent, waktu mulai)
  b. kerjakan sesuai spesifikasi di prompt-antigravity-2.md
  c. jalankan pemeriksa item itu (tes baru + QA manual); catat angka QA di papan
  d. tulis/ubah dokumen item itu (jalankan /humanizer pada .md)
  e. commit berkas milikmu, push
  f. tulis di papan: item → ✅ + hash commit, atau ❌ + sebab bila pemeriksa gagal dua kali
  g. LANGSUNG ambil item berikutnya di antreanmu. Jangan menunggu persetujuan pengguna.
Bila antreanmu habis, ambil item di bagian "Permintaan" papan yang ditujukan padamu.
Bila tidak ada, tulis "SELESAI <agent>" di papan dan berhenti.
Bertanya ke pengguna hanya bila spesifikasi bertentangan dengan kode atau aturan; tulis
pertanyaan di papan bagian "Pertanyaan" dan lanjutkan item lain sambil menunggu.

## 4. Papan koordinasi
docs/papan-agen.md dibuat oleh Agent QA di awal (lihat prompt QA). Semua agent boleh
menyunting papan, hanya di baris milik sendiri atau dengan menambah baris. Commit papan
bersama commit item (`git add docs/papan-agen.md`); bila papan bentrok saat rebase,
ambil versi remote lalu tambahkan barismu lagi.

## Berkas per agent
DATA: app/harga_resmi.py, app/valuasi_otomatis.py, app/sitasi.py, app/store.py,
      scripts/valuasi_otomatis.py, scripts/cek_finmind_resmi.py, scripts/dcf.py (satu
      baris D-c), valuation/inputs/2330.json (hanya teks sources, D-b),
      app/templates/valuasi.html, blok tab 'valuasi' dan 'keu' di saham.html (pakai
      kunci), app/teks/data.py, tests/test_putaran2_data.py, tests/data/harga_resmi_*,
      blok setUpModule D-b di tests/test_agent.py, docs/valuasi-otomatis.md.
WEB:  app/main.py (kecuali baris include_router milik Claude), app/config.py,
      app/tarik.py (periksa_sekarang), app/agent/llm.py (jatah per jalan),
      app/templates/_penafian.html, kunci.html, feed.html, review.html, peringatan.html,
      base.html, bagian saham.html di luar blok valuasi/keu (pakai kunci),
      app/static/app.css (tambah di akhir), app/i18n.py (hanya rk.p.hati dan rk.p.aman),
      app/teks/web.py, scripts/impor_arsip.py, tests/test_putaran2_web.py,
      docs/deploy-dokploy.md.
QA:   docs/papan-agen.md, docs/pengungkapan-pihak-ketiga.md, docs/laporan-antigravity-2.md,
      app/teks/qa.py, tests/test_putaran2_qa.py, baris status di docs/rencana-dan-status.md.
Nama tes di prompt-antigravity-2.md tetap dipakai, hanya berkasnya dipisah per agent
(test_r1_* dan test_dc_*/test_db_*/test_b3_* di _data; test_r2_*, test_r3_*, test_da_*
di _web; test_r4_* di _qa).
````

````text
# PROMPT PERAN: Agent DATA

Antrean (urut): R1 → D-c → D-b → B3.
- R1 tidak bergantung pada siapa pun. Mulai segera.
- D-c sebelum D-b, karena D-b mengisi field yang ditandai "tidak tersedia" oleh D-c.
- B3 menyunting blok 'keu' saham.html: minta kunci saham.html di papan dulu.
- Untuk QA manual yang butuh situs berjalan, jalankan `uvicorn app.main:app --port 8001`
  (port 8001, supaya tidak bentrok dengan agent lain) dan matikan setelah selesai.
````

````text
# PROMPT PERAN: Agent WEB

Antrean (urut): R2 → R3 → D-a → bantu QA.
- R2 menyunting banyak template termasuk saham.html: minta kunci saham.html di papan,
  kerjakan bagian saham.html dulu, lepas kunci secepatnya.
- R3 dan D-a sama-sama menyunting app/main.py; kerjakan berurutan, commit di antara.
- D-a langkah 4 menyunting app/agent/llm.py. Hanya fungsi `mulai_jalan` dan pengecekan
  jatah di `tanya()`; bagian lain llm.py milik Claude.
- Server untuk QA manual: `uvicorn app.main:app --port 8002`.
- "Bantu QA": setelah D-a ✅, buka semua halaman di tiga bahasa (daftar di bagian 4
  langkah 4 prompt-antigravity-2.md) dan tulis temuan di papan bagian "Temuan QA".
````

````text
# PROMPT PERAN: Agent QA

Kamu pemeriksa dan penulis laporan. Kamu tidak menyunting kode aplikasi.

Langkah pertama (sebelum agent lain mulai menulis papan): buat docs/papan-agen.md dengan
bagian berikut, commit, push:
  ## Status item (tabel: ID · Agent · Status · Mulai · Commit · Angka QA)
     isi awal: R1 DATA ⬜, D-c DATA ⬜, D-b DATA ⬜, B3 DATA ⬜, R2 WEB ⬜, R3 WEB ⬜,
     D-a WEB ⬜, R4 QA ⬜
  ## Kunci berkas (baris "KUNCI/LEPAS saham.html")
  ## Permintaan (dari · untuk · isi · status)
  ## Galat (waktu · tes · dugaan area · agent)
  ## Pertanyaan untuk pengguna
  ## Temuan QA
  ## Temuan untuk Claude

Antrean:
1. R4 (spesifikasi di prompt-antigravity-2.md).
2. Pemeriksaan silang: setiap kali sebuah item berubah jadi ✅ di papan, dalam 10 menit:
   - `git pull --rebase origin main`;
   - baca diff commit item itu (`git show <hash> --stat` lalu isi berkasnya);
   - cocokkan dengan langkah dan pemeriksa di prompt-antigravity-2.md: semua tes yang
     disebut ada dan lulus, tidak ada tes lama yang diubah di luar tempat yang diizinkan,
     tidak ada berkas di luar kepemilikan agent itu, angka QA tertulis;
   - jalankan ulang QA manual item itu sendiri bila memungkinkan;
   - hasil: tulis "terverifikasi QA" di kolom Status, atau pindahkan ke ❌ dengan
     penjelasan di "Temuan QA" dan tulis permintaan perbaikan ke agent pemilik.
3. Setelah semua item ✅ terverifikasi atau ❌ final: jalankan pemeriksaan akhir bagian 4
   prompt-antigravity-2.md (tes penuh, tes tanpa Wi-Fi, git grep, tiga bahasa, kunci baca).
4. Tulis docs/laporan-antigravity-2.md sesuai bagian 5 prompt-antigravity-2.md, ditambah
   satu bagian "Hasil pemeriksaan silang" (item, siapa memeriksa, apa yang dicocokkan,
   hasil). Jalankan /humanizer pada laporan dan papan. Perbarui baris status di
   docs/rencana-dan-status.md. Commit, push.
5. Tulis "SELESAI QA" di papan.

Kamu boleh menolak item. Item dianggap lulus hanya bila kamu sendiri sudah melihat tesnya
lulus. Jangan menyalin klaim agent lain ke laporan tanpa memeriksanya.
````

---

## Cara Afinzaki memantau dan mengecek

- Selama berjalan: buka `docs/papan-agen.md` (di folder lokal, atau setelah `git pull`).
  Kolom Status menunjukkan item mana yang sedang dikerjakan, selesai, atau gagal. Bagian
  "Pertanyaan untuk pengguna" berisi hal yang butuh jawabanmu.
- Bila satu agent diam lebih dari 20 menit tanpa mengubah papan, cek panelnya di Agent
  Manager. Biasanya tertahan oleh kunci saham.html atau tes milik agent lain.
- Setelah "SELESAI QA": ikuti bagian "Cara Afinzaki mengecek hasilnya" di
  `prompt-antigravity-2.md`, lalu kirim `docs/laporan-antigravity-2.md` ke Claude.

Tanda bahaya tambahan untuk multi-agent: commit yang berisi berkas milik agent lain,
`git add -A` di riwayat perintah, atau papan menunjukkan item ✅ tanpa "terverifikasi QA".
