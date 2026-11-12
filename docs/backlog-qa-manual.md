# Backlog QA manual (v1.1)

Temuan QA manual Afinzaki, dengan penyebab dan action plan untuk Antigravity (Gemini).
Kerjakan berurutan dari atas. Setiap item: kerjakan, jalankan `python3 -m unittest discover -s tests`
dan `python3 scripts/qa_halaman.py`, commit dengan judul yang disebut, `git pull --rebase`, push ke
`main`, lalu ubah status item di tabel ini.

**Cara menjalankan.** Tempel ke Antigravity:

```text
Baca docs/backlog-qa-manual.md. Kerjakan semua item berstatus "Belum" dari atas ke bawah, ikuti
action plan di tiap item, dan patuhi batas berkasnya. Setelah tiap item: tes, commit, git pull
--rebase, push, lalu ubah status item itu menjadi "Selesai (<hash commit>)" di tabel.
```

| No | Temuan | Status |
|---|---|---|
| QA-1 | Review feed: lencana jumlah, alasan teknis, arsip mendominasi, kotak cari, tombol, penafian | Belum |
| QA-2 | Narasi AI tab ringkasan tidak muncul untuk profil konservatif dan agresif | Belum |

---

## QA-1 · Review tampilan feed

Dari foto layar feed setelah U2–U3 (12 Nov). Batas: hanya template, `app/static/app.css`,
`app/static/ui.js`, `app/teks/ui.py`. Jangan ubah Python lain.

1. Lencana jumlah di menu "Alerts" harus konsisten dengan kartu ringkasan (sekarang menu 1094,
   kartu 1/5/13). Tampilkan jumlah Held untuk lingkup yang sama, bukan total semua pengumuman.
2. Alasan di baris feed jangan teknis (contoh sekarang: "Magnitude plausible — 60,400 vs 1,272,410
   NT$ million = 0.05× (OUTSIDE the 0.20–3× band)…", "Confidence 0.45 is below the threshold 0.55 for
   clause 20 (0 👎, 0 👍)"). Buat kunci baru di `app/teks/ui.py` `ui.alasan_polos.<kode>` untuk kode
   alasan yang paling sering (lihat `alasan_i18n.kode`: cek.besaran, akhir.di_bawah_ambang,
   saring.di_luar, tahan.tanpa_angka, tahan.tanpa_valuasi, cek.mu, akhir.modal_kecil,
   saring.antar_grup, sinyal risiko serius) berisi satu kalimat polos tiga bahasa. Tampilkan itu di
   feed; alasan teknis asli hanya di halaman detail. Bila kode tidak dikenal, pakai alasan asli.
3. Bawaan feed hanya menampilkan Published dan Held; Archived disembunyikan dan bisa dibuka dengan
   klik kartu Archived atau chip "Tampilkan yang diarsip" (sisi klien).
4. Kotak cari: placeholder pendek ("Search code or name" / "搜尋代號或名稱" / "Cari kode atau nama"),
   huruf Instrument Sans, tidak terpotong.
5. Tombol Re-run dan Check now diberi penjelasan singkat (tooltip ⓘ atau teks kecil): Re-run =
   proses ulang data yang sudah ada, Check now = tarik pengumuman baru dari bursa. Re-run jadi
   tombol sekunder yang lebih kecil.
6. Penafian di feed dibuat satu baris dengan tautan "selengkapnya" yang membuka teks lengkap.
7. Foto layar ulang feed (tiga bahasa, 1440 dan 390) ke `docs/ui/sesudah/`.

Commit: `UI: QA-1 perbaikan review feed`.

## QA-2 · Narasi AI tidak muncul untuk konservatif dan agresif

**Gejala.** Di `/saham/<kode>?tab=ringkasan`, memilih Conservative atau Aggressive tidak
menampilkan kotak narasi AI. Moderate muncul.

**Penyebab (dipastikan dari kode).** Narasi dibuat Gemini dari fakta + kalimat kecocokan profil,
jadi tiap profil butuh panggilan baru; moderat muncul karena sudah ada di cache.
`app/agent/llm.py` `mulai_jalan(maks)` mengisi variabel GLOBAL `_jatah_sisa`, `_gagal_beruntun`,
`_mulai_jalan_t` untuk membatasi satu jalan pipeline (40 panggilan, 90 detik, 3 gagal beruntun),
dan tidak pernah dilepas setelah pipeline selesai. Setiap `llm.tanya()` berikutnya dari permintaan
web (`app/ringkasan.py` `narasi()`) ditolak pemutus ("batas waktu model per jalan habis", atau jatah
0 setelah `_hasil_awal_tanpa_model`). `narasi()` mengembalikan teks None dan `saham.html`
menyembunyikan kotak narasi tanpa alasan. Chat tidak terkena (memakai `chat._gemini`).

**Action plan.**
1. `app/agent/llm.py`: status pemutus jadi milik THREAD yang menjalankan pipeline. Pakai
   `threading.local()` untuk jatah_sisa, gagal_beruntun, mulai_jalan_t. Tambah `selesai_jalan()`
   yang mengosongkan ketiganya, dan context manager `jalan(maks)` yang memanggil `mulai_jalan` lalu
   `selesai_jalan` di `finally`. Panggilan dari thread lain tidak terkena jatah pipeline.
2. `app/main.py`: di tiga tempat yang memanggil `llm.mulai_jalan(...)` lalu
   `pipeline.jalankan_semua()` (`_hasil_awal_tanpa_model` dan dua cabang di `hasil()`), ganti dengan
   `with llm.jalan(...)`. Jangan ubah logika lain.
3. `app/templates/saham.html` tab ringkasan: bila `rk.narasi.teks` kosong tetapi
   `rk.narasi.alasan_kode` ada, tampilkan satu baris kecil abu-abu di tempat kotak narasi:
   `t(rk.narasi.alasan_kode)` (kunci `rk.alasan.tanpa_model` / `rk.alasan.gagal` /
   `rk.alasan.ditolak`; pastikan ada di tiga bahasa, tambahkan di `app/teks/ui.py` bila belum ada).
   Jangan tampilkan isi teknis `rk.narasi.alasan`.
4. Tes baru `tests/test_pemutus_thread.py` (tanpa jaringan, mock fungsi panggilan Gemini yang dipakai
   `llm.tanya`):
   a. Thread A: `with llm.jalan(0)`: `llm.tanya` → `GagalModel`. Setelah blok selesai, `llm.tanya`
      di thread yang sama berhasil.
   b. Saat thread A masih di dalam `with llm.jalan(0)`, `llm.tanya` dari thread B berhasil.
   c. Setelah `with llm.jalan(40)` yang dimulai >90 detik lalu (patch `time.monotonic`), panggilan
      dari thread lain tetap berhasil.
   d. `ringkasan.susun("2330", "en", "agresif", ...)` dengan model di-mock mengembalikan
      `{"ringkasan": "..."}` yang lolos `periksa_narasi` → `rk["narasi"]["sumber"] == "model"`.
   e. `tests/test_agent.py` `test_pemutus_setelah_tiga_gagal_beruntun` tetap lulus (sesuaikan hanya
      bila perlu memakai `llm.jalan`).
5. Tes semua + QA halaman harus lulus.

**Batas.** Jangan ubah `app/chat.py`, `app/agent/pipeline.py`, atau angka ambang mana pun.

Commit: `Fix: QA-2 pemutus model hanya di thread pipeline; narasi AI untuk semua profil`.

**Cek setelah deploy.** `/saham/2330?tab=ringkasan` → Conservative lalu Aggressive: kotak narasi
muncul (panggilan pertama ±5 detik). Ulangi di emiten lain. Bila tetap tidak muncul, baris
penjelasan sebab sekarang tampil; kirim isinya ke Claude.
