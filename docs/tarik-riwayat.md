# Menarik riwayat pengumuman MOPS → server FEAF

**Kenapa perlu:** server hanya bisa menarik pengumuman **hari berjalan** (OpenAPI bursa).
Riwayat sebelumnya, yang dibutuhkan untuk gold set dan demo, hanya ada di MOPS, dan
MOPS **hanya bisa diakses dari jaringan Taiwan**. Jadi: laptop di Taiwan menarik,
lalu mengirim hasilnya ke server.

```
Laptop (wifi kampus / hotspot kartu Taiwan)          Server (feaf.example.com)
  spike_mops.py   → daftar pengumuman
  parse_mops.py   → alamat tiap pengumuman
  fetch_details.py→ isi lengkap (data pribadi dibuang)
  kirim_riwayat.py ─────────── HTTPS + kode akses ───►  /api/impor → digabung tanpa duplikat
```

Tidak perlu `pip install`: skrip penarik hanya memakai pustaka bawaan Python 3.9+.

---

## 0. Persiapan (2 menit)

- Laptop di **wifi kampus atau hotspot HP kartu Taiwan**. **VPN mati.**
- Repo terbaru:

```bash
git checkout main && git pull
```

## 1. Tarik daftar pengumuman (±1 menit)

Pakai kode yang ada di watchlist server:

```bash
python3 scripts/spike_mops.py --codes 2330 2454 2317 2881 1301
```

✅ Tiap emiten: `OK — N baris via mopsov.twse.com.tw`
❌ `diblokir`: jaringan bukan Taiwan, atau VPN masih menyala.
❌ `tidak menemukan tabel`: tampilan MOPS berubah. Kirim berkas `data/raw/*.html` yang disebut di pesan itu ke Claude.

## 2. Ambil alamat tiap pengumuman (detik)

```bash
python3 scripts/parse_mops.py --since 2026-06-01
```

Mulai dari Juni dulu supaya cepat. Bisa diulang dengan tanggal lebih awal nanti.

## 3. Tarik isi lengkap (±2,5 detik per pengumuman)

```bash
python3 scripts/fetch_details.py --since 2026-06-01 --all
```

Lima emiten sejak Juni ≈ 400 pengumuman ≈ **15–20 menit**. Biarkan berjalan; jedanya
sengaja lambat karena MOPS server publik. **Jangan diturunkan.**

Hasilnya **digabung** ke `data/parsed/details.json`, tidak menimpa. Kalau terputus di
tengah jalan, jalankan lagi; yang sudah ada dilewati.

## 4. Kirim ke server (±1 menit)

```bash
python3 scripts/kirim_riwayat.py --server https://feaf.example.com
```

Skrip menanyakan **kode akses** (isi `SENTINEL_KODE_AKSES` di Dokploy). Kode tidak
tampil saat diketik.

✅ `Selesai: N pengumuman baru masuk ke server`
❌ `HTTP 403`: kode akses salah, atau `SENTINEL_KODE_AKSES` belum diisi di Dokploy.

Mengirim dua kali aman: yang sudah ada di server dilewati.

## 5. Cek di web

Buka `https://feaf.example.com/?lang=en`. Riwayat muncul di **Alerts** dan di tab
**Stream** setiap halaman saham. Untuk pengumuman yang lolos saringan pasal, agent
memanggil Gemini **sekali per pengumuman**. Hasilnya disimpan, jadi pemeriksaan
berkala berikutnya tidak memanggil model lagi.

---

## Catatan

- **Data pribadi** (`發言人`, jabatan, telepon) dibuang di laptop oleh `fetch_details.py`,
  dan **dibuang sekali lagi** di server saat impor.
- **Folder `data/` tidak di-commit.** Jangan kirim `details.json` lewat chat atau git;
  pakai `kirim_riwayat.py`.
- Untuk menambah emiten lain nanti: ulangi langkah 1–4 dengan `--codes` yang baru.
  Pengumuman lama yang sudah terkirim tidak terduplikasi.
