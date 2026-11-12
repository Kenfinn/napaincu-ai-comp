# Prompt gabungan Antigravity: chat sampai selesai, lalu backlog QA manual

Untuk Afinzaki. Satu prompt untuk semua pekerjaan yang tersisa, dijalankan di **satu agent saja**
(jangan dua agent bersamaan, karena chat dan backlog sama-sama menyentuh `app/main.py` dan template).
Sebelum menempel: `git pull`. Kalau agent chat yang sekarang masih berjalan, tunggu sampai berhenti dulu.

Tempel ke Antigravity:

```text
Kerjakan semua sisa pekerjaan v1.1 berurutan, di satu agent ini saja.

TAHAP A — Ask FEAF (chatbot):
1. git pull --rebase origin main, lalu lihat git log --oneline untuk commit berawalan "Chat:".
2. Baca docs/prompt-antigravity-5-chat.md dari awal sampai habis (bagian "Aturan" dan "Batas berkas" wajib dipatuhi).
3. Lanjutkan dari langkah C pertama yang BELUM ada commit-nya (C1 "API percakapan", C2 "lanjutan + recap", C3 "alat menu", C4 panel, C5 keamanan, C6 evaluasi, C7 dokumen + laporan) sampai C7 selesai. Jangan ulang langkah yang sudah di-commit, tapi baca kodenya dulu supaya lanjutannya cocok.
4. Pastikan sebelum lanjut ke tahap B: semua tes lulus, python3 scripts/evaluasi.py --chat tetap 52/52 di jalur aturan, --chat-percakapan tersimpan, dan docs/laporan-antigravity-5.md selesai.

TAHAP B — Backlog QA manual:
5. Baca docs/backlog-qa-manual.md. Kerjakan semua item berstatus "Belum" dari atas ke bawah (QA-1, QA-2, QA-3, dan item baru bila ada), ikuti action plan dan batas berkas tiap item.
6. QA-1 dan QA-3 memakai kalimat polos yang sama: buat kunci ui.polos.* / ui.alasan_polos.* sekali di app/teks/ui.py dan pakai ulang di feed dan detail.
7. Panel chat dari tahap A jangan sampai rusak: setelah tiap item, buka /, /saham/2330, /peringatan/<satu id> dan pastikan tombol panel chat masih muncul dan bisa dipakai.

ATURAN UNTUK SEMUA LANGKAH:
- Setelah tiap langkah/item: python3 -m unittest discover -s tests dan python3 scripts/qa_halaman.py harus lulus; commit dengan judul yang disebut di dokumennya; git pull --rebase; push ke main.
- Untuk item backlog, ubah statusnya di tabel docs/backlog-qa-manual.md menjadi "Selesai (<hash commit>)".
- Jangan ubah app/agent/* kecuali app/agent/llm.py untuk QA-2. Jangan ubah angka ambang, eval/gold*, valuation/*, scripts/dcf.py.
- Tidak ada label beli/jual, tidak ada nama orang, semua teks baru tiga bahasa (en, zh, id), tes tanpa jaringan.
- Kalau ada yang tidak bisa diselesaikan, catat di laporan dan lanjut ke item berikutnya; jangan berhenti.

PENUTUP:
8. Tambahkan bagian "Backlog QA manual" di docs/laporan-antigravity-4.md: per item QA, apa yang diubah, commit, hasil tes, foto layar sebelum/sesudah.
9. Commit "Docs: laporan v1.1", push, lalu beri tahu Afinzaki bahwa semuanya selesai dan sebutkan dua berkas laporan: docs/laporan-antigravity-4.md dan docs/laporan-antigravity-5.md.
```

Setelah selesai: kirim kedua laporan itu ke Claude untuk ditinjau sekaligus, lalu Deploy.
