# Diagram alur FEAF

Tiga diagram spesifikasi dan alur chat multi-turn, disusun dari kode `v1.1.0` per 13 Nov 2026 (rincian teknis lengkap ada di [`docs/system-design.md`](system-design.md)).
Kalau kode berubah, diagram ini ikut diubah: diagram ini spesifikasi, bukan ilustrasi. Gambar statis versi awal ada di `docs/diagram/` dan perlu dirender ulang secara terpisah bila dipakai di luar Markdown.

1. [Alur sistem](#1-alur-sistem): data datang dari mana, lewat komponen apa, tampil di mana
2. [Flowchart agent](#2-flowchart-agent-satu-pengumuman): nasib satu pengumuman melalui jalur valuasi maupun jalur sinyal deterministik, plus alur Tanya FEAF
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
    PX["TWSE / TPEx Resmi & OpenAPI<br/>harga harian · TAIEX · PER/PBR · profil"]:::luar
    FM["FinMind<br/>laba rugi · neraca · arus kas"]:::luar
    MOPS["MOPS<br/>riwayat pengumuman<br/><i>hanya jaringan Taiwan</i>"]:::luar
  end

  subgraph LAPTOP["Relay di jaringan Taiwan"]
    SK["spike_mops -> parse_mops<br/>-> fetch_details"]:::inti
    KR["kirim_riwayat.py"]:::inti
  end

  subgraph SERVER["Server FEAF · FastAPI (uvicorn --workers 1)"]
    PM["Pemantau otomatis<br/>TARIK_OTOMATIS_DETIK (lantai 300 dtk)"]:::inti
    CN["Tombol Check now"]:::inti
    TK["Penarik (tarik.py)<br/>cek BLOCK_MARKERS · buang PII_LABELS · deduplikasi"]:::inti
    IM["/api/impor<br/>wajib KODE_AKSES · maks 5000"]:::inti
    DB[("/data (SENTINEL_DATA_DIR)<br/>parsed · watchlist · traces<br/>traces_chat · cache_model")]:::simpan
    MN[("valuation/inputs/*.json<br/>data/fixtures/")]:::simpan
    AG["Agent (6 jalur klausul)<br/>screen -> extract/sinyal -> triase<br/>-> verify -> recompute -> verify"]:::inti
    UB["Ambang per pasal<br/>umpan_balik.py · riwayat maks 500"]:::simpan
    RV["Keputusan review manusia<br/>keputusan_review.json"]:::simpan
    VO["Valuasi otomatis & Ringkasan<br/>FinMind + harga_resmi + beta latar + profil"]:::inti
    PS["Data pasar & cache TTL<br/>pasar.py · harga_resmi.py · indeks_nama.py"]:::inti
    CH["Tanya FEAF (chat.py)<br/>TOLAK · HMAC riwayat · 13 ALAT · periksa_jawaban"]:::inti
  end

  GM["Gemini (MODEL + MODEL_CADANGAN)<br/>ekstraksi klausul 20 · narasi opsional · Tanya FEAF<br/>tidak pernah menghitung angka"]:::model

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
  AG <-->|"klausul 20 / fallback aturan"| GM
  AG -->|"hasil + jejak"| DB
  AG -->|"klausul 31 memicu segarkan"| VO
  UB --> AG
  RV --> AG
  W5 -->|"👍/👎, setujui/arsipkan"| UB
  W5 --> RV
  PX --> PS
  FM --> PS
  PS --> VO --> AG
  MN --> VO
  PS --> W4
  VO --> W4
  CH <-->|"tool calling <= 5 langkah"| GM
  PS --> CH
  VO --> CH
  DB --> CH
  CH --> W6
  DB --> W1
  DB --> W2
  DB --> W3
  DB --> W4
```

| Kotak / Subsistem | Berkas Utama |
|---|---|
| Konfigurasi & versi | `app/config.py`, `app/versi.py` |
| Penarik, watchlist, impor, baca-simpan | `app/tarik.py`, `app/store.py`, `scripts/tarik.py` |
| Pemantau otomatis, middleware baca, rute web & API | `app/main.py` |
| Agent valuasi & 6 jalur sinyal | `app/agent/pipeline.py`, `screen.py`, `extract.py`, `sinyal.py`, `triase.py`, `verify.py`, `recompute.py` |
| Ambang 👍/👎, review manusia, profil risiko | `app/umpan_balik.py`, `app/review.py`, `app/ambang_profil.py` |
| Valuasi otomatis, harga resmi, ringkasan, sitasi | `app/valuasi_otomatis.py`, `app/harga_resmi.py`, `app/ringkasan.py`, `app/sitasi.py`, `scripts/dcf.py` |
| Data pasar & indeks pencarian emiten | `app/pasar.py`, `app/indeks_nama.py` |
| Tanya FEAF (server & UI browser) | `app/chat.py`, `app/static/chat.js`, `app/templates/_panel_chat.html` |
| Gemini + cache SHA-256 + circuit breaker | `app/agent/llm.py` |
| Riwayat dari laptop di jaringan Taiwan | `scripts/spike_mops.py`, `parse_mops.py`, `fetch_details.py`, `kirim_riwayat.py` |

**Catatan sumber data:** OpenAPI pengumuman harian TWSE/TPEx bisa diambil dari mana saja dengan jeda pembaruan berkala, sedangkan riwayat MOPS lama hanya bisa ditarik dari jaringan Taiwan lalu dikirim ke `/api/impor`.

---

## 2. Flowchart agent (satu pengumuman)

```mermaid
flowchart TD
  classDef akhir_ok fill:#1B3A5C,stroke:#1B3A5C,color:#FFFFFF
  classDef akhir_tahan fill:#FBF2E3,stroke:#C98A0B,color:#5F4409
  classDef akhir_lewat fill:#E3E6EA,stroke:#8A939E,color:#3A434D
  classDef akhir_tolak fill:#F9EAE8,stroke:#B3392B,color:#6B2620
  classDef model fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef kode fill:#FFFFFF,stroke:#8A9BB0,color:#1B2A3A
  classDef manusia fill:#F3EEFA,stroke:#7A5BB5,color:#2E1E4D

  A(["FETCHED · VALIDATED<br/>PII_LABELS dibuang · deduplikasi"]):::kode --> B{"SCREENED (screen.py)<br/>KLAUSA_RELEVAN + LABEL_CAPEX + _ANTAR_GRUP"}:::kode
  B -->|"Klausul 20 antargrup 100%"| X1(["ARCHIVED<br/>tersaring sebelum LLM"]):::akhir_lewat
  B -->|"Klausul 22/23 · 11/35 · 31 · 7/8 · 1/3/40"| S1["EXTRACTED · signal (sinyal.py)<br/>parser deterministik tanpa Gemini"]:::kode
  S1 --> S2["VERIFIED · source<br/>sinyal.periksa_kutipan()"]:::kode
  S2 --> S3{"Policy gating<br/>ambang_profil.py<br/>moderat hold / konservatif arsip"}:::kode
  S3 -->|terbit| P_SIG(["PUBLISHED<br/>kartu sinyal terverifikasi"]):::akhir_ok
  S3 -->|arsip| X_SIG(["ARCHIVED<br/>di bawah ambang materialitas"]):::akhir_lewat
  S3 -->|tahan| H_SIG(["HELD · sinyal / sinyal_rusak"]):::akhir_tahan

  B -->|"Klausul 20, LABEL_CAPEX, atau pasal ragu"| C{"llm.jalan(): ada kunci Gemini,<br/>kuota run & breaker sehat?"}:::kode
  C -->|tidak| R["Penalar aturan (_sari_aturan)<br/>LABEL_SAH · SATUAN · MATA_UANG"]:::kode
  C -->|ya| D["TRIAGED · EXTRACTED<br/>Gemini di pagar &lt;dokumen&gt; (atau cache SHA-256)<br/>PENANDA_INJEKSI mencatat telemetri"]:::model
  D -->|gagal / fallback| R
  D --> H
  R --> H{"Ada angka<br/>dengan kalimat sumbernya?"}:::kode
  H -->|tidak| X2(["HELD · tanpa_angka<br/>tidak bisa disetujui manual"]):::akhir_tahan
  H -->|ya| T{"TRIAGED · confidence<br/>DASAR 0,55 (0,45 tanpa pasal)<br/>+ 0,10 angka terbukti + PITA_MATERIAL"}:::kode
  T -->|"skor < ambang - 0,05"| X3(["ARCHIVED<br/>skor di bawah zona ragu"]):::akhir_lewat
  T -->|"zona ragu [ambang - 0,05, ambang)"| X4(["HELD · keyakinan rendah"]):::akhir_tahan
  T -->|"skor >= ambang"| I{"Ada model valuasi?<br/>manual atau otomatis"}:::kode
  I -->|tidak| X5(["HELD · tanpa valuasi"]):::akhir_tahan
  I -->|ya| J{"VERIFIED · source (7 cek)<br/>label · kutipan · angka · mu<br/>satuan · konversi · besaran"}:::kode
  J -->|semua lolos| L["VALUED<br/>recompute.py -> dcf.compute() sebelum vs sesudah"]:::kode
  L --> M{"VERIFIED · arithmetic<br/>drift <= 1e-6%?"}:::kode
  M -->|ya| X7(["PUBLISHED<br/>peringatan + sumber + delta DCF"]):::akhir_ok
  M -->|tidak| X_REJ(["REJECTED<br/>sirkularitas gagal"]):::akhir_tolak
  J -->|gagal| X6(["HELD · verifikasi<br/>ragu (CEK_RAGU) -> boleh disetujui<br/>non-ragu -> hanya arsip"]):::akhir_tahan

  H_SIG & X2 & X4 & X5 & X6 --> HR["HUMAN REVIEW (_terapkan_review)<br/>keyakinan disetujui -> tetap wajib lewat Stage 4"]:::manusia
  HR -->|setujui sah| P2(["PUBLISHED<br/>disetujui manusia, tercatat"]):::akhir_ok
  HR -->|arsipkan| A2(["ARCHIVED<br/>diarsipkan manusia, tercatat"]):::akhir_lewat
  X7 --> UB["👍/👎 investor (umpan_balik.py)<br/>clamp(0,55 + 0,05*👎 - 0,02*👍, 0,40, 0,90)"]:::manusia
```

Pada pipeline pengumuman, pemanggilan LLM dibatasi hanya pada ekstraksi jalur valuasi (Klausul 20, override `LABEL_CAPEX`, atau pasal tak terbaca) dengan fallback aturan deterministik. Jalur sinyal (`22/23`, `11/35`, `31`, `7/8`, `1/3/40`) bekerja sepenuhnya secara deterministik di `app/agent/sinyal.py`. Seluruh keputusan akhir dicatat ke `DATA_DIR/traces/<id>.json`.

### Alur Tanya FEAF (multi-turn, 13 alat)

```mermaid
flowchart LR
  Q["/api/tanya atau POST /tanya<br/>pertanyaan + riwayat sessionStorage (maks 12)"] --> LIM["Batas laju _jam<br/>60 permintaan/jam"]
  LIM --> REJ{"Pagar TOLAK<br/>prediksi / order / injeksi / PII?"}
  REJ -->|kena| T_REJ["Jawaban tolak deterministik + tanda()"]
  REJ -->|lolos| HIS["_bersihkan_riwayat()<br/>verifikasi HMAC tanda() (<= 6 dari 50 giliran)<br/>+ resolusi _kode_aktif() & _kalimat_konteks()"]
  HIS --> LOOP{"Recap / Gemini (<= 5 langkah)<br/>/ fallback _rencana_aturan"}
  LOOP <--> ALAT["13 alat read-only (ALAT)<br/>7 saham: harga · statistik · laporan · pengumuman · valuasi · ringkasan · cari<br/>6 menu: feed · peringatan · jejak · review · ambang · watchlist"]
  LOOP --> VER{"periksa_jawaban()<br/>angka ada di alat/tanya/riwayat HMAC?<br/>bebas kata TERLARANG?"}
  VER -->|lolos| OUT["Tanda HMAC 32-hex + traces_chat/<id>.json<br/>render via textContent"]
  VER -->|gagal| FB["_ringkas_template() dari hasil alat<br/>+ tanda HMAC + traces_chat/"]
```

---

## 3. Flowchart pengecekan aplikasi

Urutan cek setelah deploy, atau saat ada perilaku yang janggal. Ikuti dari atas.

```mermaid
flowchart TD
  classDef ok fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef salah fill:#F9EAE8,stroke:#B3392B,color:#6B2620
  classDef cek fill:#FFFFFF,stroke:#1B3A5C,color:#1B2A3A

  S(["Mulai"]):::cek --> A{"Buka /sehat<br/>keluar ok: true & VERSI_KODE?"}:::cek
  A -->|tidak| A1["Log container / server<br/>cari baris error terakhir<br/>cek port 8000 dan --workers 1"]:::salah
  A -->|ya| B{"Menu samping · Reasoning engine<br/>menampilkan nama model aktif (bukan rule-based)?"}:::cek
  B -->|tidak, rule-based reasoner| B1["Cek API key / env model<br/>lalu restart container"]:::salah
  B -->|ya| C{"Menu samping · Last fetch<br/>titik hijau dan ter-update?"}:::cek
  C -->|merah| C1["Watchlist -> lihat kotak status tarik<br/>kena BLOCK_MARKERS? -> cek jaringan"]:::salah
  C -->|belum pernah| C2["Cek SENTINEL_TARIK_OTOMATIS_DETIK<br/>(lantai 300 dtk) atau tekan Check now"]:::salah
  C -->|hijau| D{"/akses lalu Watchlist<br/>tambah emiten berhasil?"}:::cek
  D -->|terkunci| D1["Cek KODE_AKSES / KUNCI_BACA<br/>dan cookie akses HMAC"]:::salah
  D -->|ya| E{"Alerts · buka kasus contoh<br/>status PUBLISHED & 7/7 cek lolos?"}:::cek
  E -->|tidak tampil| E1["Cek SERTAKAN_CONTOH=1<br/>atau ketersediaan data/fixtures/"]:::salah
  E -->|ya| F{"Jejak audit /jejak/{id}<br/>Model calls >= 1 atau cache >= 1?"}:::cek
  F -->|0 dan mode cadangan: ya| F1["Cek status HTTP 400/401/402/403/404<br/>atau breaker di jejak & cache_model/"]:::salah
  F -->|ya| G{"Buka halaman saham 2330<br/>tab Financials & harga harian muncul?"}:::cek
  G -->|pesan FinMind / harga resmi| G1["Cek kuota FinMind atau jeda 2 dtk<br/>harga_resmi.py (HTTP 307/429)"]:::salah
  G -->|ya| V{"Tab Valuation emiten non-keuangan<br/>menampilkan DCF otomatis?"}:::cek
  V -->|tidak| V1["Cek status industri (17 = tidak_berlaku)<br/>atau FCFF <= 0 / TTL 12 jam"]:::salah
  V -->|ya| Q{"/tanya atau /api/tanya<br/>uji pertanyaan + lanjutan multi-turn?"}:::cek
  Q -->|gagal / fallback salah| Q1["Lihat /api/tanya/jejak/&lt;id&gt;<br/>dan berkas di traces_chat/"]:::salah
  Q -->|ya| H{"Ganti bahasa EN / 中文 / ID<br/>semua label ikut berganti?"}:::cek
  H -->|ya| Z(["Aplikasi jalan penuh"]):::ok
  H -->|tidak| H1["Cek template & kamus app/teks/"]:::salah
```

