# Prompt induk Antigravity: kerja semalam tanpa pengawasan

Untuk Afinzaki, sebelum tidur:

1. Laptop dicolok ke listrik, mode tidur (sleep) dimatikan, Wi-Fi tetap tersambung.
2. Di setelan Antigravity, izinkan agent menjalankan perintah terminal dan menyunting
   berkas tanpa minta persetujuan (auto-execute / always proceed). Kalau tidak, agent
   akan berhenti menunggu klik di perintah pertama.
3. Buka satu agent di workspace repo ini, tempel isi kotak di bawah, jalankan.
4. Pagi hari: buka `docs/laporan-antigravity-2.md` dan kirim ke Claude.

Satu agent berurutan dipilih karena lebih tahan dijalankan tanpa pengawasan daripada tiga
agent paralel. Versi paralel tetap ada di `prompt-antigravity-multiagen.md` bila kamu
sedang bisa memantau.

---

````text
# Kerja semalam: baca dokumentasi, lalu kerjakan putaran 2 sampai selesai

Pemilik repo sedang tidur dan tidak bisa menjawab sampai pagi. Kerjakan semua langkah di
bawah berurutan tanpa berhenti untuk bertanya. Claude juga bekerja di repo ini malam ini
(chatbot dan evaluasi: app/chat.py, app/templates/chat.html, tests/test_chat.py,
scripts/evaluasi.py, docs/diagram*) dan push ke main. Jangan sentuh berkas itu.

## Aturan selama tidak diawasi
- Ikuti semua aturan di docs/prompt-antigravity-2.md bagian 0, 1, dan 2.
- Jangan pernah bertanya lalu menunggu. Kalau ada keraguan, pilih opsi yang paling hati-hati
  (tidak menerbitkan, tidak menghapus, tidak mengubah keputusan tim), catat di laporan
  bagian "Keputusan yang saya ambil sendiri", lalu lanjut.
- Dilarang: deploy ke server, menyentuh Dokploy, mengubah atau membaca kunci API,
  mengirim pesan ke siapa pun, push --force, menghapus tes, melonggarkan assert.
- Commit hanya berkas yang kamu ubah (`git add <path>`), jangan `git add -A`.
- Sebelum setiap push: `git pull --rebase origin main`, jalankan semua tes, lalu push.
  Rebase bentrok di berkas milik Claude: `git rebase --abort`, tunggu 3 menit, ulangi.
- Tes gagal di berkas milik Claude (yang terdaftar di atas): catat di laporan, jangan
  diperbaiki, lanjutkan item yang tidak bergantung padanya.
- Item gagal pemeriksa dua kali setelah diperbaiki: tandai ❌ dengan sebab, lanjut ke item
  berikutnya. Jangan menghabiskan lebih dari 90 menit pada satu item.

## Langkah 1: baca dokumentasi (tanpa mengubah kode)
git pull --rebase origin main, lalu jalankan semua tes dan catat hasilnya.
Baca urut: docs/rencana-dan-status.md, docs/konteks-sesi.md, docs/aaic-2026-ringkasan.md,
docs/rencana-finalis.md, DESIGN.md, docs/pemetaan-pasal.md, docs/valuasi-otomatis.md,
docs/laporan-serangan.md, docs/prompt-antigravity-2.md.
Tulis docs/pemahaman-antigravity.md (pakai /humanizer): jawab singkat 1) apa yang
dikerjakan dan sengaja tidak dikerjakan FEAF, 2) urutan state pengumuman, 3) kapan HELD
dan mana yang boleh disetujui manusia, 4) cara skor triase dan 👍/👎 bekerja, 5) data apa
yang dikirim ke Gemini, 6) aturan tiga bahasa dan app/teks/, 7) aturan git; lalu daftar
pertentangan antar-dokumen atau dengan kode. Bila ada pertentangan, yang berlaku urut:
kode dan tes > docs/rencana-dan-status.md > docs/konteks-sesi.md > dokumen lain.
Commit berkas itu, push. LANGSUNG lanjut ke langkah 2.

## Langkah 2: putaran 2
Kerjakan item di docs/prompt-antigravity-2.md bagian 3 dengan urutan ini (berbeda dari
urutan di berkas itu, supaya app/main.py tidak disunting bolak-balik):
R1 → R2 → R3 → D-a → D-c → D-b → B3 → R4.
Untuk setiap item: tandai 🔄 di baris status docs/rencana-dan-status.md → kerjakan →
jalankan semua pemeriksanya (tes + QA manual, catat angkanya) → tulis dokumen item
(pakai /humanizer) → commit dengan pesan "<ID>: <ringkasan>" → push → tandai ✅ atau ❌
→ LANGSUNG item berikutnya.
Pasang skill anti-slop dan humanizer seperti bagian 0.1 prompt itu sebelum R1. Kalau
pemasangan gagal, lanjut tanpa skill dan catat.
Server untuk QA manual: `uvicorn app.main:app --port 8001`, matikan setelah dipakai.

## Langkah 3: pemeriksaan akhir dan laporan
Jalankan pemeriksaan akhir bagian 4 docs/prompt-antigravity-2.md. Lalu tulis
docs/laporan-antigravity-2.md sesuai bagian 5 berkas itu, ditambah dua bagian:
- "Keputusan yang saya ambil sendiri" (apa, kenapa, berkas).
- "Linimasa" (jam mulai dan selesai tiap item).
Jalankan /humanizer pada laporan. Commit, push. Lalu berhenti. Jangan memulai pekerjaan
lain di luar daftar ini.
````
