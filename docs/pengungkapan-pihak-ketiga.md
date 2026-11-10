# Pengungkapan Pihak Ketiga dan Alat AI

Dokumen ini disusun untuk memenuhi Pasal 13 aturan kompetisi NAPAI AAIC 2026.
Kami mengungkapkan seluruh sumber daya eksternal yang dipakai dalam pengembangan
dan pengoperasian sistem FEAF: model bahasa besar (LLM), API data pasar modal,
pustaka kode terbuka, dan alat bantu pengembangan kecerdasan buatan.

## 1. Daftar Pihak Ketiga, Layanan Data, dan Perangkat Lunak

| Nama | Jenis | Untuk apa | Lingkup data | Lisensi atau syarat pakai | Diverifikasi? |
|---|---|---|---|---|:---:|
| Claude Code (Anthropic) | Alat AI pembuat kode | Asisten pemrograman berpasangan dalam penulisan arsitektur, rute web, dan pengujian. | Potongan kode sumber aplikasi lokal, keluaran tes unit, dan berkas teks sesi. | [Anthropic Commercial Terms](https://www.anthropic.com/legal/commercial-terms): "Anthropic does not use Customer Content to train our models, unless explicitly agreed upon." | Ya |
| Antigravity (Google) | Alat AI pembuat kode | Asisten pemrograman berpasangan untuk kalkulasi DCF otomatis, uji ketahanan serangan, dan kepatuhan aturan. | Potongan kode sumber lokal, instruksi tugas, dan log eksekusi unit test. | [Google Cloud AI Terms](https://cloud.google.com/terms/service-terms): "Customer Data is not used to train models without customer permission." | Ya |
| Gemini API (Google) | Model di aplikasi | Ekstraksi entitas dari teks pengumuman publik dan verifikasi silang terhadap dokumen bursa. Menggunakan model `gemini-2.5-flash` (dengan cadangan otomatis `gemini-2.5-pro` bila kuota 429 atau layanan 5xx). | Hanya teks pengumuman MOPS publik dan angka publik yang dikirim. Tidak ada data pribadi, kunci API, atau kredensial yang dikirim ke model. | [Google AI Studio Terms of Service](https://ai.google.dev/terms): "Content submitted to the API is processed in accordance with Google APIs Terms of Service." | Ya |
| FinMind API | Data pasar modal | Penarikan data laporan keuangan kuartalan emiten Taiwan (neraca, laba rugi, dan arus kas). | Simbol saham dan data historis laporan keuangan publik. Akses dibatasi cache lokal 12 jam (300 permintaan/jam tanpa token). | [FinMind Open Data](https://finmind.github.io/): "Open financial data library for academic research and personal quantitative analysis." | Ya |
| TWSE OpenAPI | Data resmi pasar modal | Profil emiten terdaftar, data jumlah saham beredar (`t187ap03_L`), dan laporan keuangan resmi (`t187ap06_L_ci`, `t187ap07_L_ci`). | Data keterbukaan informasi publik pasar reguler Taiwan Stock Exchange. | [Taiwan Open Government Data License](https://openapi.twse.com.tw/): "The Open Government Data License allows commercial and non-commercial reuse with attribution." | Ya |
| TPEx OpenAPI | Data resmi pasar modal | Profil dan data pengumuman emiten pasar OTC (Taipei Exchange). | Data profil publik dan keterbukaan informasi emiten OTC. | [TPEx Open Data Terms](https://www.tpex.org.tw/web/about/opendata/): "Free public access and reproduction for financial technology innovation." | Ya |
| Situs Resmi TWSE & TPEx (R1) | Data pasar historis | Pengambilan deret harga harian historis penutupan saham dan indeks acuan pasar modal Taiwan (TAIEX). | Data harga penutupan harian publik selama 2 tahun terakhir untuk menghitung beta mingguan resmi. | [TWSE Website Terms](https://www.twse.com.tw/zh/page/terms.html): "Ketentuan keterbukaan informasi dan publikasi data pasar bursa resmi Taiwan." | Ya |
| MOPS (Market Observation Post System) | Data resmi keterbukaan informasi | Sumber primer sitasi laporan keuangan dan penarikan berkas pengumuman emiten. | Tautan URL sitasi langsung per kolom periode laporan keuangan dan pengumuman asli. Akses pengunduhan riwayat dibatasi jaringan Taiwan. | [MOPS TWSE](https://mops.twse.com.tw/): "Sistem pelaporan resmi keterbukaan pasar modal di bawah regulasi FSC Taiwan." | Ya |
| Yahoo Finance | Data pasar historis | Sempat dipakai untuk beta mingguan pada versi awal prototipe. | Tidak dipakai lagi sejak R1; seluruh estimasi beta telah dialihkan ke harga harian bursa resmi TWSE/TPEx. | [Yahoo Developer Terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html): "Tidak dipakai lagi sejak R1." | Ya |
| Damodaran Online (Aswath Damodaran, NYU Stern) | Data referensi akademis | Estimasi Equity Risk Premium (ERP) untuk pasar Taiwan ($5{,}01\%$). | Satu konstanta ERP negara Taiwan untuk masukan perhitungan WACC. | [Damodaran Online Data](https://pages.stern.nyu.edu/~adamodar/): "An open site for education and corporate finance analysis; free to use with citation." | Ya |
| Imbal Hasil Obligasi Pemerintah Taiwan 10 Tahun | Data referensi suku bunga | Tingkat bebas risiko ($R_f = 1{,}94\%$) untuk perhitungan biaya ekuitas WACC. | Satu konstanta suku bunga acuan obligasi pemerintah Taiwan tenor 10 tahun. | [Central Bank of the Republic of China (Taiwan)](https://www.cbc.gov.tw/): "Statistik resmi suku bunga obligasi pemerintah negara." | Ya |
| fastapi | Pustaka web framework | Kerangka kerja HTTP backend berbasis async Python. | Dependensi kode lokal di requirements.txt. | [MIT License](https://github.com/fastapi/fastapi/blob/master/LICENSE): "Permission is hereby granted, free of charge, to any person obtaining a copy..." | Ya |
| uvicorn | Pustaka server ASGI | Server HTTP berbasis antarmuka ASGI untuk menjalankan aplikasi FastAPI. | Dependensi runtime lokal di requirements.txt (uvicorn[standard]). | [BSD 3-Clause License](https://github.com/encode/uvicorn/blob/master/LICENSE.md): "Redistribution and use in source and binary forms, with or without modification..." | Ya |
| jinja2 | Pustaka mesin template | Mesin render template halaman HTML antarmuka pengguna. | Dependensi rendering lokal di requirements.txt. | [BSD 3-Clause License](https://github.com/pallets/jinja/blob/main/LICENSE.txt): "Redistribution and use in source and binary forms, with or without modification..." | Ya |
| httpx | Pustaka klien HTTP | Klien HTTP pengujian lokal untuk `fastapi.testclient.TestClient`. | Dependensi pengujian lokal di requirements.txt (hanya untuk pengujian otomatis tanpa jaringan). | [BSD 3-Clause License](https://github.com/encode/httpx/blob/master/LICENSE.md): "Redistribution and use in source and binary forms, with or without modification..." | Ya |
| Playwright (Microsoft) | Alat tangkapan layar | Otomasi browser headless untuk mengambil tangkapan layar halaman web, tidak diikutsertakan di paket aplikasi server. | Antarmuka browser lokal. | [Apache License 2.0](https://github.com/microsoft/playwright/blob/main/LICENSE): "Licensed under the Apache License, Version 2.0." | Ya |
| Mermaid | Alat diagram | Render diagram alur data dan arsitektur sistem di berkas markdown dokumentasi. | Sintaks teks diagram markdown lokal, tidak diimpor ke runtime aplikasi. | [MIT License](https://github.com/mermaid-js/mermaid/blob/develop/LICENSE): "Permission is hereby granted, free of charge..." | Ya |
| Skill humanizer | Skill AI | Penyuntingan gaya bahasa dokumentasi agar lugas, alami, dan bebas dari konstruksi kalimat klise AI. | Berkas teks markdown dokumentasi. | [MIT License](https://github.com/blader/humanizer/blob/main/LICENSE): "Permission is hereby granted, free of charge..." | Ya |
| Skill anti-slop | Skill AI | Audit kualitas komentar kode dan pembersihan teks komentar generik pada basis kode. | Analisis sintaks teks kode lokal. | [MIT License](https://github.com/miqdadbadjuber/anti-slop/blob/main/LICENSE): "Permission is hereby granted, free of charge..." | Ya |

---

## 2. Pembagian Kerja Tim

Tabel ini sengaja dikosongkan untuk diisi langsung oleh anggota tim FEAF:

| Bagian | Dikerjakan oleh | Peran AI |
|---|---|---|

---

## 3. Catatan Data Pribadi

Cache profil emiten TPEx di server sempat menyimpan nama pejabat dan alamat email kontak
perusahaan hingga perbaikan pada 10 November 2026 (commit `e4572d6`). Data tersebut
tidak pernah ditampilkan kepada pengguna publik. Penyaringan daftar izin (`PROFIL_DISIMPAN`)
secara otomatis membuang field pribadi tersebut saat berkas dibaca setelah deploy.
