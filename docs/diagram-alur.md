# Diagram alur FEAF

Tiga diagram, disusun dari kode per 11 Nov 2026 dini hari (setelah A2, B2, C1, D3, D4). Gambarnya ada di `docs/diagram/`.
Kalau kode berubah, diagram ini ikut diubah: diagram ini spesifikasi, bukan ilustrasi.

1. [Alur sistem](#1-alur-sistem): data datang dari mana, lewat komponen apa, tampil di mana
2. [Flowchart agent](#2-flowchart-agent-satu-pengumuman): nasib satu pengumuman dari awal sampai akhir
3. [Flowchart pengecekan](#3-flowchart-pengecekan-aplikasi): urutan cek bahwa aplikasi di server benar-benar jalan

---

## 1. Alur sistem

```mermaid
flowchart LR
  classDef luar fill:#EEF2F6,stroke:#8A9BB0,color:#1B2A3A
  classDef model fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef inti fill:#FFF6E0,stroke:#C98A0B,color:#4A3305
  classDef simpan fill:#F3EEFA,stroke:#7A5BB5,color:#2E1E4D
  classDef layar fill:#1B3A5C,stroke:#1B3A5C,color:#FFFFFF

  subgraph SUMBER["Sumber data"]
    OA["OpenAPI TWSE / TPEx<br/>pengumuman harian 重大訊息<br/><i>bisa dari mana saja</i>"]:::luar
    PX["OpenAPI TWSE / TPEx<br/>harga · PER/PBR · profil"]:::luar
    FM["FinMind<br/>laba rugi · neraca · arus kas"]:::luar
    MOPS["MOPS<br/>riwayat pengumuman<br/><i>hanya jaringan Taiwan</i>"]:::luar
  end

  subgraph LAPTOP["Laptop di jaringan Taiwan"]
    SK["spike_mops → parse_mops<br/>→ fetch_details"]:::inti
    KR["kirim_riwayat.py"]:::inti
  end

  subgraph SERVER["Server Dokploy · feaf.afinzaki.my.id"]
    PM["Pemantau otomatis<br/>tiap 10 menit"]:::inti
    CN["Tombol Check now"]:::inti
    TK["Penarik<br/>validasi bentuk · buang data pribadi<br/>watchlist (semua emiten setelah D-a)"]:::inti
    IM["/api/impor<br/>wajib kode akses"]:::inti
    DB[("/data<br/>details.json · watchlist<br/>traces · cache")]:::simpan
    AG["Agent<br/>saring → pilah/sari → triase keyakinan<br/>→ periksa → hitung ulang → periksa"]:::inti
    UB["Ambang per pasal<br/>dari 👍/👎"]:::simpan
    RV["Keputusan review manusia"]:::simpan
    VO["Valuasi otomatis<br/>FinMind + harga + beta"]:::inti
    PS["Data pasar + cache"]:::inti
    CH["Tanya FEAF<br/>penjaga → alat → pemeriksa angka"]:::inti
  end

  GM["Gemini (model flash yang tersedia)<br/>pilah/sari · narasi ringkasan · Tanya FEAF<br/>tidak pernah menghitung angka"]:::model

  subgraph LAYAR["Web · EN / 中文 / ID"]
    W1["Watchlist"]:::layar
    W2["Alerts + detail"]:::layar
    W3["Jejak audit"]:::layar
    W4["Halaman saham<br/>Ringkasan · Stream · Key Stats<br/>Financials · Valuation · Profile"]:::layar
    W5["Review · Ambang"]:::layar
    W6["Tanya FEAF"]:::layar
  end

  MOPS --> SK --> KR -->|HTTPS| IM --> DB
  PM --> TK
  CN --> TK
  OA --> TK --> DB
  DB --> AG
  AG <-->|bila ada kunci API| GM
  AG -->|hasil + jejak| DB
  UB --> AG
  RV --> AG
  W5 -->|👍/👎, setujui/arsipkan| UB
  W5 --> RV
  PX --> PS
  FM --> PS
  PS --> VO --> AG
  PS --> W4
  VO --> W4
  CH <-->|function calling| GM
  PS --> CH
  DB --> CH
  CH --> W6
  DB --> W1
  DB --> W2
  DB --> W3
  DB --> W4
```

| Kotak | Berkas |
|---|---|
| Penarik, watchlist, impor | `app/tarik.py`, `scripts/tarik.py` |
| Pemantau otomatis, rute web | `app/main.py` |
| Agent | `app/agent/pipeline.py`, `screen.py`, `extract.py`, `triase.py`, `verify.py`, `recompute.py` |
| Ambang 👍/👎, review | `app/umpan_balik.py`, `app/review.py` |
| Valuasi otomatis | `app/valuasi_otomatis.py`, `scripts/dcf.py` |
| Tanya FEAF | `app/chat.py` |
| Gemini + cache jawaban | `app/agent/llm.py` |
| Data pasar | `app/pasar.py` |
| Riwayat dari laptop | `scripts/spike_mops.py`, `parse_mops.py`, `fetch_details.py`, `kirim_riwayat.py` |

**Yang perlu diingat:** OpenAPI pengumuman diperbarui sekitar sekali sehari (berisi
pengumuman hari sebelumnya). Riwayat lama dan pengumuman real-time hanya ada di MOPS,
yang hanya bisa diakses dari jaringan Taiwan.

---

## 2. Flowchart agent (satu pengumuman)

```mermaid
flowchart TD
  classDef akhir_ok fill:#1B3A5C,stroke:#1B3A5C,color:#FFFFFF
  classDef akhir_tahan fill:#FBF2E3,stroke:#C98A0B,color:#5F4409
  classDef akhir_lewat fill:#E3E6EA,stroke:#8A939E,color:#3A434D
  classDef model fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef kode fill:#FFFFFF,stroke:#8A9BB0,color:#1B2A3A
  classDef manusia fill:#F3EEFA,stroke:#7A5BB5,color:#2E1E4D

  A(["FETCHED · VALIDATED<br/>pengumuman tersimpan, data pribadi dibuang"]):::kode --> B{"SCREENED<br/>pasal 符合條款 di daftar?<br/>(11 · 20 · 22 · 2, menunggu B1)"}:::kode
  B -->|tidak| X1(["ARCHIVED<br/>tidak sampai ke model"]):::akhir_lewat
  B -->|ya, atau pasal tak terbaca| C{"Ada kunci Gemini<br/>dan jatah?"}:::kode
  C -->|tidak| R["Penalar aturan<br/>label sah · total transaksi · satuan"]:::kode
  C -->|ya| D["TRIAGED · EXTRACTED<br/>Gemini: input mana, angka berapa,<br/>kalimat mana (cache bila pernah)"]:::model
  D -->|gagal| R
  D --> H
  R --> H{"Ada angka<br/>dengan kalimat sumbernya?"}:::kode
  H -->|tidak| X2(["HELD · tanpa angka<br/>hanya bisa diarsipkan"]):::akhir_tahan
  H -->|ya| T{"TRIAGED · confidence<br/>skor = dasar pasal + angka terbukti<br/>+ materialitas vs kapitalisasi"}:::kode
  T -->|"skor < ambang − 0,05"| X3(["ARCHIVED<br/>skor dan ambang sebagai alasan"]):::akhir_lewat
  T -->|"zona ragu"| X4(["HELD · keyakinan rendah"]):::akhir_tahan
  T -->|"skor ≥ ambang"| I{"Ada model valuasi?<br/>manual atau otomatis"}:::kode
  I -->|tidak| X5(["HELD · tanpa valuasi<br/>boleh disetujui"]):::akhir_tahan
  I -->|ya| J{"VERIFIED · sumber, 7 cek<br/>label · kutipan · angka · mata uang<br/>satuan tertulis · konversi · besaran"}:::kode
  J -->|semua lolos| L["VALUED<br/>hitung ulang DCF sebelum vs sesudah"]:::kode
  L --> M{"VERIFIED · hitungan<br/>sirkularitas utuh?"}:::kode
  M -->|ya| X7(["PUBLISHED<br/>peringatan + sumber + dampak"]):::akhir_ok
  J -->|gagal| X6(["HELD · verifikasi<br/>ragu → boleh disetujui<br/>karangan → hanya arsip"]):::akhir_tahan
  M -->|tidak| X6
  X2 & X4 & X5 & X6 --> HR["HUMAN REVIEW di /review<br/>keyakinan rendah disetujui → lanjut ke pemeriksa"]:::manusia
  HR -->|setujui, kasus ragu| P2(["PUBLISHED<br/>disetujui manusia, tercatat"]):::akhir_ok
  HR -->|arsipkan| A2(["ARCHIVED<br/>diarsipkan manusia, tercatat"]):::akhir_lewat
  X7 --> UB["👍/👎 investor<br/>ambang pasal +0,05 per 👎, −0,02 per 👍<br/>batas 0,40–0,90, dipakai di triase berikutnya"]:::manusia
```

Model hanya dipakai di **satu** kotak hijau. Semua keputusan terbit, tahan, atau arsip
diambil kode yang bisa diperiksa, dan setiap langkah tercatat di jejak audit
(`data/traces/<id>.json`) dengan nama state brief hal. 7.

Tanya FEAF (chatbot) punya alurnya sendiri: penjaga menolak prediksi, order, dan data
pribadi → Gemini memanggil alat data, maksimal 5 langkah → pemeriksa memastikan setiap
angka ada di hasil alat dan tidak ada kata beli/jual → bila ditolak, jawaban template
dari hasil alat yang sama. Jejaknya di `data/traces_chat/`.

---

## 3. Flowchart pengecekan aplikasi

Urutan cek setelah deploy, atau saat ada yang terasa tidak beres. Ikuti dari atas.

```mermaid
flowchart TD
  classDef ok fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef salah fill:#F9EAE8,stroke:#B3392B,color:#6B2620
  classDef cek fill:#FFFFFF,stroke:#1B3A5C,color:#1B2A3A

  S(["Mulai"]):::cek --> A{"Buka /sehat<br/>keluar ok: true ?"}:::cek
  A -->|tidak| A1["Dokploy → Logs<br/>cari baris error terakhir<br/>cek Domain port 8000"]:::salah
  A -->|ya| B{"Menu samping · Reasoning engine<br/>menampilkan gemini-3.6-flash ?"}:::cek
  B -->|tidak, rule-based reasoner| B1["Cek nama env persis GEMINI_API_KEY<br/>lalu Deploy ulang"]:::salah
  B -->|ya| C{"Menu samping · Last fetch<br/>titik hijau, jam ≤ 10 menit lalu ?"}:::cek
  C -->|merah| C1["Watchlist → lihat kotak bawah<br/>diblokir? galat? → cek jaringan server"]:::salah
  C -->|belum pernah| C2["Cek SENTINEL_TARIK_OTOMATIS_DETIK<br/>atau tekan Check now"]:::salah
  C -->|hijau| D{"/akses?kode=… lalu Watchlist<br/>tambah 2330 berhasil ?"}:::cek
  D -->|perlu kode akses| D1["Cek SENTINEL_KODE_AKSES<br/>dan kode di tautan"]:::salah
  D -->|ya| E{"Alerts · buka kasus contoh 2330 18 Sep<br/>TERBIT, 8/8 cek lolos ?"}:::cek
  E -->|tidak tampil| E1["Cek SENTINEL_SERTAKAN_CONTOH=1"]:::salah
  E -->|ya| F{"Jejak audit kasus itu<br/>Model calls ≥ 1 atau cache ≥ 1 ?"}:::cek
  F -->|0 dan mode cadangan: ya| F1["Kunci Gemini belum terbaca,<br/>atau kuota/kunci ditolak:<br/>lihat sebab cadangan di jejak"]:::salah
  F -->|ya| G{"Cari 2330 di menu samping<br/>tab Financials menampilkan tabel ?"}:::cek
  G -->|pesan FinMind| G1["Kuota habis: isi FINMIND_TOKEN<br/>atau tunggu 1 jam"]:::salah
  G -->|ya| V{"Tab Valuation emiten selain 2330<br/>menampilkan DCF otomatis ?"}:::cek
  V -->|tidak| V1["Tekan Check now untuk memanaskan<br/>valuasi watchlist, cek log FinMind"]:::salah
  V -->|ya| Q{"/tanya: 'What is the latest price of 2330?'<br/>jawaban bersumber ?"}:::cek
  Q -->|tidak| Q1["Lihat /api/tanya/jejak/&lt;id&gt;"]:::salah
  Q -->|ya| H{"Ganti bahasa EN / 中文 / ID<br/>semua teks ikut berganti ?"}:::cek
  H -->|ya| Z(["Aplikasi jalan penuh ✔"]):::ok
  H -->|tidak| H1["Laporkan halaman yang bermasalah"]:::salah
```
