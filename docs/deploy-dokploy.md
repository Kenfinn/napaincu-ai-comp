# Deploy FEAF ke Dokploy

Repo ini sudah punya `Dockerfile`. Dokploy cukup membangunnya dari GitHub. Kira-kira
15 menit untuk pertama kali.

Image-nya sudah diuji (8 Nov): build, health check, kode akses, penarik otomatis,
dan data yang tetap ada setelah container dibuat ulang.

> Variabel environment tetap berawalan `SENTINEL_` (nama kode internal), walau nama produknya FEAF.
>
> Nama menu di bawah mengikuti Dokploy versi umum. Kalau versimu sedikit berbeda,
> cari padanannya. Isinya sama: sumber Git, tipe build Dockerfile, environment,
> volume, dan domain.

---

## 0. Sebelum mulai

- Dokploy sudah jalan di servermu, dan kamu bisa login ke dashboard-nya.
- Dokploy punya akses ke repo `Kenfinn/napaincu-ai-comp`. Repo ini privat, jadi:
  **Settings → Git → GitHub**, sambungkan GitHub App, lalu beri akses ke repo itu.
- Siapkan satu **kode akses** acak untuk tombol ubah, misalnya hasil perintah ini:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(12))"
```

- Cek dulu bahwa servermu bisa menjangkau OpenAPI bursa. Jalankan di terminal server:

```bash
curl -s https://openapi.twse.com.tw/v1/opendata/t187ap04_L | head -c 200
```

  Harus keluar teks JSON yang diawali `[ {"出表日期"`. Kalau yang keluar halaman
  "FOR SECURITY REASONS", server ini diblokir, dan penarikan harus dari laptop di
  Taiwan.

## 1. Buat aplikasi

1. **Projects → Create Project**, beri nama `feaf`.
2. Di dalam project: **Create Service → Application**, beri nama `feaf-web`.

## 2. Sumber kode

Tab **General**, bagian **Provider**:

| Isian | Nilai |
|---|---|
| Provider | GitHub |
| Repository | `Kenfinn/napaincu-ai-comp` |
| Branch | `claude/blissful-clarke-9iuasr` (atau `main` setelah digabung) |
| Build Path | `/` |

Bagian **Build Type**: pilih **Dockerfile**, dengan Docker File `Dockerfile`.
Jangan pilih Nixpacks.

## 3. Environment

Tab **Environment**, tempel lalu sesuaikan:

```
SENTINEL_KODE_AKSES=isi-dengan-kode-acak-tadi
SENTINEL_SERTAKAN_CONTOH=1
SENTINEL_TARIK_OTOMATIS_DETIK=600
```

| Variabel | Gunanya |
|---|---|
| `SENTINEL_KODE_AKSES` | Tanpa kode ini, pengunjung hanya bisa melihat. Tombol tambah/hapus watchlist dan *Check now* hanya jalan setelah membuka `/akses?kode=...` sekali |
| `SENTINEL_SERTAKAN_CONTOH` | `1` = empat kasus contoh (terbit, injeksi, USD, dilewati) tetap tampil di samping data asli, berlabel "sample" |
| `SENTINEL_TARIK_OTOMATIS_DETIK` | Periksa pengumuman tiap N detik (minimal 300). `600` = tiap 10 menit, 24 jam, supaya riwayat terkumpul sendiri |
| `GEMINI_API_KEY` | **Opsional.** Tanpa ini, agent memakai penalar aturan. Isi di sini, **jangan pernah** di kode |

## 4. Volume (wajib)

Tab **Advanced → Volumes / Mounts → Add Volume**:

| Isian | Nilai |
|---|---|
| Mount Type | Volume |
| Volume Name | `feaf-data` |
| Mount Path | `/data` |

Tanpa ini, watchlist dan semua riwayat pengumuman **hilang setiap kali redeploy**.

## 5. Domain

Tab **Domains → Add Domain**:

| Isian | Nilai |
|---|---|
| Host | subdomain milikmu, mis. `feaf.domainmu.com` (atau tombol generate domain dari Dokploy) |
| Container Port | `8000` |
| HTTPS | aktif, Let's Encrypt |

Kalau memakai subdomain sendiri, buat dulu DNS record `A` ke IP server.

## 6. Deploy

Tekan **Deploy**, lalu buka tab **Deployments/Logs**. Build pertama sekitar 1–2 menit.
Tanda berhasil di log:

```
Uvicorn running on http://0.0.0.0:8000
```

Lalu buka di browser:

| Alamat | Harus tampil |
|---|---|
| `https://feaf.domainmu.com/sehat` | `{"ok":true, ...}` |
| `https://feaf.domainmu.com/` | Halaman Alerts, menu bahasa EN / 中文 / ID |
| `https://feaf.domainmu.com/akses?kode=<kodemu>` | Pesan "Access granted", lalu tombol-tombol bisa dipakai |

Beberapa menit setelah menyala, kotak **Last fetch** di menu samping terisi jam
penarikan otomatis pertama.

## 7. Update berikutnya

Setiap ada commit baru di branch tadi, tekan **Deploy** lagi. Bisa juga aktifkan
**Auto Deploy** di tab General. Data di volume tetap aman.

---

## Yang dibagikan ke teman-teman

Kirim dua tautan:

1. **Untuk melihat saja:** `https://feaf.domainmu.com/?lang=en` (atau `lang=zh` / `lang=id`)
2. **Untuk mencoba tombol:** `https://feaf.domainmu.com/akses?kode=<kodemu>`.
   Bagikan hanya ke tim. Siapa pun yang punya tautan ini bisa mengubah watchlist.

### Daftar uji untuk teman-teman

| # | Coba | Yang diharapkan |
|---|---|---|
| 1 | Ganti bahasa EN → 中文 → ID | Semua teks berganti, termasuk alasan dan hasil pemeriksaan agent |
| 2 | Buka kasus contoh **2330 · 2026-09-18** | Terbit, 8/8 pemeriksaan lolos, dampak ke valuasi |
| 3 | Buka kasus contoh **2330 · 2026-09-22** (injeksi) | Peringatan "teks menyerupai perintah", tapi angka yang terbit tetap benar |
| 4 | Buka kasus contoh **2330 · 2026-09-19** (USD) | Ditolak, karena mata uang asing tidak dikonversi diam-diam |
| 5 | Buka **Jejak audit** salah satu kasus | Semua langkah tercatat: durasi, panggilan model, token, alasan |
| 6 | Watchlist: tambah kode yang salah, mis. `12;ab` | Ditolak dengan pesan |
| 7 | Watchlist: tambah saham yang sedang aktif mengumumkan, lalu **Check now** | Pengumuman asli hari itu masuk ke Alerts |
| 8 | Buka **Valuation 2330** | Reverse DCF, WACC, sensitivitas |

### Yang memang belum ada (jangan dilaporkan sebagai bug)

- **Model AI belum aktif** kalau `GEMINI_API_KEY` belum diisi. Layar menyebutnya
  terus terang ("rule-based reasoner").
- **Pengumuman asli kebanyakan berakhir "skipped".** Daftar pasal yang dianggap
  menyentuh valuasi masih sementara dan menunggu verifikasi tim keuangan
  (`app/agent/screen.py`).
- **Valuasi baru ada untuk 2330.** Emiten lain ditandai "figures only".
- **Riwayat hanya mulai dari hari deploy.** OpenAPI bursa hanya memuat pengumuman
  hari berjalan. Riwayat lama harus ditarik dari laptop di jaringan Taiwan.
- **Antrean review manusia** belum dibangun.
