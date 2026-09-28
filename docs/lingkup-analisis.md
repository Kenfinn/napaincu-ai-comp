# Lingkup Analisis Finansial — Keputusan Setelah Diskusi 13–14 Sep

Versi lengkap: https://claude.ai/code/artifact/7113b076-3a91-4e3b-b271-a30bc6dfc484

---

## 1. Valuasi tetap dibangun

Pertanyaan yang muncul: kalau ramalan harga tidak perlu dibangun, apakah valuasi juga tidak perlu?

**Perlu.** Deskripsi tantangan menyebut *"investment models"* secara eksplisit sebagai bagian
yang harus diintegrasikan. Batasnya bukan antara meramal dan tidak meramal, tapi antara
**angka yang bisa ditelusuri juri** dan angka yang tidak.

| Bisa diverifikasi | Tidak bisa diverifikasi |
|---|---|
| Input dari laporan MOPS, tiap angka bisa diklik ke sumbernya | "Harga akan naik ke NT$120 bulan depan" |
| Asumsi (growth, WACC, terminal multiple) tampil di layar dan bisa diubah | Model ML yang mengeluarkan target harga tanpa asumsi terbaca |
| Output berupa rentang nilai wajar | Sinyal beli/jual tanpa penjelasan |
| Sensitivity analysis menunjukkan kerapuhan hasil | Skor gabungan dengan bobot tak diungkap |

Tiga syarat yang membuatnya aman:

1. Setiap input model wajib membawa sitasi ke dokumen sumbernya.
2. Asumsi harus terlihat dan bisa diubah — DCF dengan asumsi tersembunyi itu ramalan yang menyamar.
3. Jangan keluarkan kata "BELI" telanjang. Keluarkan rentang nilai wajar versus harga pasar,
   asumsi yang menghasilkannya, dan apa yang harus terjadi supaya kesimpulan itu salah.

### Monte Carlo — penyebutan menentukan

- ❌ "72% kemungkinan saham ini naik." → pernyataan tentang masa depan, tidak bisa dibuktikan.
- ✅ "Dengan sebaran asumsi ini, nilai wajar melampaui harga pasar pada 72% dari 10.000 simulasi."
  → pernyataan tentang model, bisa direproduksi dan diaudit.

---

## 2. Dua arah produk harus disatukan

Setelah diskusi, ada dua produk berbeda di kepala tim:

- **Arah A** — agen pemantau: memantau pengumuman, kirim peringatan. Dipicu peristiwa.
- **Arah B** — agen riset ekuitas: hitung rasio dan valuasi mendalam. Dipicu pertanyaan.

Dalam 32 hari dengan satu orang teknis, dua-duanya tidak mungkin. Penyatuannya:

> **Valuasi jadi mesinnya. Pemantauan jadi pemicunya.** Ketika ada pengumuman material untuk
> saham di watchlist, agent menghitung ulang valuasinya dan memberi tahu apakah kesimpulan
> undervalued/overvalued *berubah* — dan asumsi mana yang bergeser.

```
pengumuman baru → tarik angka terbaru → hitung ulang valuasi
  → bandingkan dengan kesimpulan lama → [berubah?] → kirim peringatan bersitasi
  → reaksi user → setel ambang
```

Kalimat scope yang diperbarui:

> "Agen yang menilai kewajaran harga saham dari laporan keuangan resmi, memantau pengumuman
> baru, dan memberi tahu investor ketika ada kejadian yang mengubah kesimpulan itu — lengkap
> dengan sumber dan asumsinya."

Ini juga menjawab "kenapa bukan Excel?" dengan telak: Excel tidak tahu kapan harus dihitung ulang.

---

## 3. Prioritas analisis sampai 16 Oktober

| Prioritas | Yang dibangun | Alasan |
|---|---|---|
| **Wajib** | CAGR, EBIT margin, D/E, ROA, ROE, dividend payout & yield | Dihitung langsung dari baris laporan. Deterministik, bisa disitasi, cepat. |
| **Wajib** | Unlevered DCF 2-stage | Satu model valuasi cukup membuktikan konsep. Paling detail dan paling bisa dipertahankan. |
| **Wajib** | Sensitivity analysis (WACC × terminal growth) | Murah dihitung, dan elemen demo paling meyakinkan. |
| Kalau sempat | Exit multiple sebagai terminal value kedua, dirata-rata dengan perpetuity | Murah ditambahkan setelah DCF jalan. |
| Kalau sempat | Monte Carlo | Efek naratif besar, tapi hanya dengan penyebutan yang benar. |
| **Tunda** | SOTP | Butuh data per segmen yang sulit diambil dari MOPS, hanya berlaku untuk perusahaan multi-lini. Masukkan ke halaman "pengembangan ke depan" di deck. |

### Poin arsitektur

Semua perhitungan di atas adalah **kalkulator deterministik**, bukan keluaran AI. Akibatnya:

1. Tidak ada risiko halusinasi pada angkanya — masalah verifikasi sebagian besar hilang.
2. Ceritanya justru lebih agentic: tugas agent bukan berhitung, tapi *memilih* analisis mana yang
   dijalankan, *mengumpulkan dan memvalidasi* inputnya, *menafsirkan*, dan *menjelaskan*.

Pengetahuan finansial masuk sebagai **tool yang dikodekan**, bukan sebagai prompt.

---

## 4. Koreksi metodologi wawancara

Rencana wawancara yang disusun untuk membenarkan rencana produk menghasilkan bukti lemah.
Kriteria yang dinilai adalah *kualitas validasi kebutuhan*, dan wawancara yang menggiring mudah
dikenali juri.

**Cara bertanya:**
- Mulai terbuka sebelum menyebut konsep apa pun: "Ceritakan terakhir kali kamu mempertimbangkan
  beli saham. Apa yang kamu cari? Di mana? Berapa lama?"
- Jangan sebut kata "rasio" sampai mereka yang menyebut duluan.
- Tanya apa yang bikin mereka *batal* beli — biasanya di situ pain point sebenarnya.
- Catat juga jawaban yang tidak cocok dengan rencana.

**Bukti paling kuat:** tunjukkan satu hal yang diubah gara-gara wawancara. Satu slide seperti itu
mengalahkan sepuluh kutipan yang kebetulan setuju.

**Soal narasumber:** utamakan orang yang benar-benar pernah membeli saham, sekecil apa pun
nominalnya. Narasumber yang tidak pernah berinvestasi menjawab secara hipotetis.

Dua catatan administratif: tim yang melakukan validasi lapangan nyata wajib menunjuk
**field liaison**, dan bukti wawancara di deck harus sudah di-de-identifikasi karena penilaian
penyisihan bersifat anonim.

---

## 5. Jawaban singkat untuk pertanyaan lain

**Bentuk output — 50/50 fundamental dan analytics?** Jangan dibagi berdasarkan teknik, bagi
berdasarkan urutan pengambilan keputusan: (1) kesimpulan undervalued/overvalued berikut
rentangnya; (2) kenapa — 3–4 rasio penentu, masing-masing bersitasi; (3) apa yang bisa
mengubahnya — sensitivity dan asumsi paling rapuh; (4) apa yang sedang terjadi — pengumuman
terbaru yang menyentuh kesimpulan itu.

**Fisher-Yates?** Tidak ada tempatnya sebagai fitur — itu algoritma pengacak urutan. Kegunaan sah
di sini: mengacak urutan soal uji supaya evaluasi tidak bias urutan, atau sampling untuk uji
holdout. Layak satu baris di metodologi, jangan masuk deck sebagai teknik.

**Fuzzy logic?** Bisa dipakai mengubah rasio kontinu jadi label ("margin sehat"), dan itu sah.
Tapi ambang batas eksplisit melakukan pekerjaan yang sama, lebih mudah dijelaskan saat tanya
jawab, dan asal angkanya bisa disitasi ke wawancara atau tolok ukur industri. Pakai ambang
eksplisit dulu.

**5 emiten yang beda-beda.** Setuju beda sektor, tambah tiga syarat: laporannya lengkap dan
formatnya konsisten; minimal satu punya pengumuman material yang baru terbit (supaya demo
pemantauan ada isinya); minimal satu perusahaan multi-lini kalau SOTP disimpan sebagai rencana
lanjutan.
