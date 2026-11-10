# Diagram alur FEAF

Tiga diagram, disusun dari kode per 10 Nov 2026. Gambarnya ada di `docs/diagram/`.
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
    TK["Penarik<br/>validasi bentuk · saring watchlist<br/>buang data pribadi"]:::inti
    IM["/api/impor<br/>wajib kode akses"]:::inti
    DB[("/data<br/>details.json · watchlist<br/>traces · cache")]:::simpan
    AG["Agent 5 tahap<br/>saring → pilah/sari → periksa<br/>→ hitung ulang → periksa"]:::inti
    PS["Data pasar + cache"]:::inti
  end

  GM["Gemini 2.5 Flash<br/>hanya tahap pilah/sari<br/>jawaban di-cache"]:::model

  subgraph LAYAR["Web · EN / 中文 / ID"]
    W1["Watchlist"]:::layar
    W2["Alerts + detail"]:::layar
    W3["Jejak audit"]:::layar
    W4["Halaman saham<br/>Stream · Key Stats · Financials<br/>Valuation · Profile"]:::layar
  end

  MOPS --> SK --> KR -->|HTTPS| IM --> DB
  PM --> TK
  CN --> TK
  OA --> TK --> DB
  DB --> AG
  AG <-->|bila ada kunci API| GM
  AG -->|hasil + jejak| DB
  PX --> PS
  FM --> PS
  PS --> W4
  DB --> W1
  DB --> W2
  DB --> W3
  DB --> W4
```

| Kotak | Berkas |
|---|---|
| Penarik, watchlist, impor | `app/tarik.py`, `scripts/tarik.py` |
| Pemantau otomatis, rute web | `app/main.py` |
| Agent | `app/agent/pipeline.py`, `screen.py`, `extract.py`, `verify.py`, `recompute.py` |
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
  classDef akhir_tolak fill:#F9EAE8,stroke:#B3392B,color:#6B2620
  classDef akhir_lewat fill:#E3E6EA,stroke:#8A939E,color:#3A434D
  classDef model fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef kode fill:#FFFFFF,stroke:#8A9BB0,color:#1B2A3A

  A(["Pengumuman baru tersimpan"]):::kode --> B{"Tahap 0 · Saringan pasal<br/>符合條款 ada di daftar<br/>11 · 20 · 22 · 2 ?"}:::kode
  B -->|tidak| X1(["DILEWATI<br/>tidak pernah sampai ke model"]):::akhir_lewat
  B -->|ya, atau nomor pasal tidak terbaca| C{"Ada kunci<br/>Gemini?"}:::kode

  C -->|tidak| R["Penalar aturan<br/>cari label butir yang sah"]:::kode
  C -->|ya| D{"Jawaban untuk dokumen ini<br/>sudah ada di cache?"}:::model
  D -->|ya| E["Pakai jawaban cache<br/>tidak dihitung panggilan model"]:::model
  D -->|tidak| F["Tahap 1–2 · Gemini<br/>input mana? angka berapa?<br/>dari kalimat mana?"]:::model
  F -->|gagal setelah 2 kali ulang| R
  F -->|berhasil| E2["Simpan ke cache"]:::model

  E --> G
  E2 --> G
  R --> G
  G["Catat bila ada teks<br/>menyerupai perintah (injeksi)"]:::kode --> H{"Ada angka lengkap<br/>dengan kalimat sumbernya?"}:::kode
  H -->|tidak| X2(["DITAHAN<br/>antre ke manusia"]):::akhir_tahan
  H -->|ya| I{"Ada berkas valuasi<br/>untuk emiten ini?"}:::kode
  I -->|tidak| X3(["DITAHAN<br/>belum ada model valuasi"]):::akhir_tahan
  I -->|ya| J{"Tahap 4a · Pemeriksa, 7 cek<br/>label sah · kutipan ada · angka ada<br/>mata uang NTD · satuan dikenali<br/>konversi ada · besaran 0,2–3×"}:::kode
  J -->|ada yang gagal| K["Temuan ditolak<br/>alasan tercatat"]:::kode
  J -->|semua lolos| L["Tahap 3 · Hitung ulang DCF<br/>sebelum vs sesudah"]:::kode
  L --> M{"Tahap 4b · Sirkularitas utuh?"}:::kode
  M -->|tidak| K
  M -->|ya| N["Temuan diterima"]:::kode
  K --> O{"Ada temuan<br/>yang diterima?"}:::kode
  N --> O
  O -->|tidak| X4(["DITOLAK<br/>tidak diterbitkan"]):::akhir_tolak
  O -->|ya| X5(["TERBIT<br/>peringatan + sumber + dampak"]):::akhir_ok

  X1 & X2 & X3 & X4 & X5 --> T[("Jejak audit<br/>data/traces/&lt;id&gt;.json")]:::kode
```

Model hanya dipakai di **satu** kotak hijau (tahap 1–2). Semua keputusan terbit atau
tidak diambil oleh kode yang bisa diperiksa.

**Status di kode vs di brief hal. 7:** kode sekarang memakai `dilewati / ditahan /
ditolak / terbit`. Brief memakai ARCHIVED / HELD FOR REVIEW / REJECTED / PUBLISHED, dan
di brief verifier yang gagal masuk **HELD**, bukan ditolak. Penyamaan ini ada di daftar
tugas berikutnya; diagram ini akan diperbarui bersamanya.

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
  A -->|ya| B{"Menu samping · Reasoning engine<br/>menampilkan gemini-2.5-flash ?"}:::cek
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
  G -->|ya| H{"Ganti bahasa EN / 中文 / ID<br/>semua teks ikut berganti ?"}:::cek
  H -->|ya| Z(["Aplikasi jalan penuh ✔"]):::ok
  H -->|tidak| H1["Laporkan halaman yang bermasalah"]:::salah
```
