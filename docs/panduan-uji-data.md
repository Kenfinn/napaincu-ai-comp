# Panduan Uji Akses Data — Dijalankan dari Jaringan Kampus

Tujuan: menjawab **satu** pertanyaan dengan bukti, bukan dugaan —
*apakah data MOPS/TWSE benar-benar bisa diambil dari jaringan kita?*

Ini penentu go / no-go untuk track SYSTEX. Targetnya: **minimal 20 pengumuman
dari 5 emiten**.

> **Wajib dijalankan dari Taiwan.** TWSE dan MOPS memblokir IP luar Taiwan dan IP
> datacenter — dan tetap mengembalikan HTTP 200, jadi blokirnya tidak terlihat seperti
> error. Matikan VPN sebelum mulai.

---

## Langkah 0 — Pastikan Python ada

```bash
python3 --version
```

Butuh 3.9 atau lebih baru. Kalau belum ada:

- **macOS** — `brew install python3`, atau unduh dari [python.org](https://www.python.org/downloads/)
- **Windows** — unduh dari [python.org](https://www.python.org/downloads/), centang
  **"Add Python to PATH"** saat instalasi. Di Windows perintahnya `python`, bukan `python3`.
- **Linux** — `sudo apt install python3`

Tidak perlu `pip install` apa pun. Kedua skrip hanya memakai pustaka bawaan Python.

## Langkah 1 — Ambil kodenya

```bash
git clone -b claude/aaic-2026-rules-6yy7gu https://github.com/Kenfinn/napaincu-ai-comp.git
cd napaincu-ai-comp
```

Kalau belum punya git: buka repo di browser, pilih branch `claude/aaic-2026-rules-6yy7gu`,
lalu **Code → Download ZIP**, dan ekstrak.

## Langkah 2 — Uji akses dasar

```bash
python3 scripts/probe_sources.py
```

Menguji enam sumber dan **memeriksa bentuk respons**, bukan status code — supaya halaman
blokir tidak salah terbaca sebagai sukses.

Yang diharapkan dari jaringan kampus:

| Sumber | Harapan |
|---|---|
| TWSE OpenAPI (2 endpoint) | OK |
| TPEx OpenAPI | OK |
| MOPS halaman indeks | OK |
| MOPS ajax_t163sb04 | OK |
| FinMind | OK (ini jalan dari mana saja) |

Kalau **semua kecuali FinMind gagal** dengan keterangan DIBLOKIR, berarti trafiknya masih
terbaca dari luar Taiwan. Cek VPN, lalu coba jaringan lain.

## Langkah 3 — Tarik pengumuman sungguhan

```bash
python3 scripts/spike_mops.py
```

Menarik 重大訊息 untuk lima emiten dari sektor berbeda: TSMC (2330), Hon Hai (2317),
Fubon Financial (2881), Formosa Plastics (1301), Chunghwa Telecom (2412).

Fubon sengaja masuk karena multi-lini bisnis — berguna kalau SOTP jadi dikerjakan nanti.

Butuh sekitar satu menit; ada jeda 2 detik antar request supaya sopan terhadap server publik.
**Jangan turunkan jedanya.**

Opsi lain:

```bash
python3 scripts/spike_mops.py --codes 2330 2454 3008   # emiten pilihan sendiri
python3 scripts/spike_mops.py --year 114               # tahun ROC lain (2025 = 114)
python3 scripts/spike_mops.py --report                 # keluaran ringkas
```

## Langkah 4 — Baca hasilnya

Skrip mencetak salah satu dari tiga kesimpulan:

- **LOLOS** — 20 pengumuman atau lebih terambil. Track SYSTEX aman, kabari tim.
- **SEBAGIAN** — ada yang masuk tapi kurang dari 20. Coba `--year` tahun sebelumnya
  atau tambah emiten.
- **BELUM LOLOS** — tidak ada yang terambil. Lihat bagian masalah umum di bawah.

Berkas yang dihasilkan:

```
data/raw/<kode>_<waktu>.html   HTML mentah — ini bukti sumber, jangan dihapus
data/parsed/<kode>.json        hasil ekstraksi + URL sumber + waktu pengambilan
data/spike-report.json         ringkasan seluruh percobaan
```

Seluruh isi `data/` sengaja tidak ikut di-commit (besar dan bisa dibuat ulang),
tapi **jangan dihapus dari komputer** — nanti dipakai untuk membangun parser yang presisi.

## Langkah 5 — Kirim balik hasilnya

Supaya parser presisi bisa ditulis, kirim tiga hal ini:

1. Isi `data/spike-report.json`
2. Baris `kolom :` dan `contoh :` yang tercetak di layar
3. Kalau ada yang gagal: 40 baris pertama salah satu berkas di `data/raw/`

```bash
cat data/spike-report.json
head -40 data/raw/*.html | head -60
```

Skrip ini sengaja **menemukan** struktur tabel MOPS, bukan mengasumsikannya — karena
struktur aslinya belum pernah dilihat langsung. Setelah hasilnya masuk, parser yang presisi
baru ditulis.

---

## Masalah umum

**Semuanya DIBLOKIR.** Trafik masih terbaca dari luar Taiwan. Matikan VPN; kalau pakai
Tailscale, Cloudflare WARP, atau proxy kampus, matikan juga. Sebagai pembanding, coba lewat
data seluler Taiwan — kalau lewat seluler jalan tapi wifi kampus tidak, berarti kampus yang
memfilter, dan itu perlu ditanyakan ke bagian IT.

**`python3: command not found` di Windows.** Pakai `python` saja, atau `py`.

**`CERTIFICATE_VERIFY_FAILED`.** Masalah trust store di komputer, bukan blokir server.
Di macOS jalankan `/Applications/Python\ 3.x/Install\ Certificates.command`.

**Terhubung tapi tidak menemukan tabel.** Bagus — artinya jaringannya lolos, tinggal
strukturnya beda dari dugaan. Kirim berkas `data/raw/` sesuai Langkah 5.

**Lambat.** Memang. Jeda 2 detik itu disengaja — MOPS membatasi laju request, dan tim yang
terlalu agresif berisiko diblokir sementara.
