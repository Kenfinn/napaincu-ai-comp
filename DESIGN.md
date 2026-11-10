# DESIGN.md: arah tampilan FEAF

Dibaca oleh agent pembuat kode (anti-slop) sebelum mengubah tampilan. Tampilan FEAF sudah
ada; pekerjaan baru mengikuti gaya ini, tidak membuat gaya baru.

## Untuk siapa

Investor ritel dan analis di Taiwan, juri lomba, dan tim. Mereka membaca angka dan
sumbernya. Layar harus padat informasi, tenang, dan mudah dicocokkan dengan dokumen asli.

## Bahan yang sudah ada (pakai, jangan ganti)

- Warna di `app/static/app.css` `:root`: `--navy` untuk menu dan tombol utama, `--naik`
  merah untuk harga naik, `--turun` hijau untuk harga turun (konvensi bursa Taiwan),
  `--amber` untuk status ditahan atau peringatan, `--tolak` untuk gagal, abu untuk teks
  sekunder.
- Huruf: Instrument Sans untuk teks, IBM Plex Mono untuk angka, kode saham, dan data.
- Komponen: `.kartu` (blok isi), `.kv` (baris label dan nilai), `.cek` (baris
  pemeriksaan ✓/✕), `.lencana` (status), `.pita` (pemberitahuan; `.fixture` kuning,
  `.nyata` hijau, `.bahaya` merah), `.tombol`, `.tombol.tipis`, `.tombol.abu`, tabel `.wl`.
- Server-rendered Jinja2. Tanpa framework JavaScript, tanpa build step, tanpa CDN baru.

## Aturan

- Angka selalu rata kanan dan memakai huruf mono. Format angka lewat filter `rb` dan `pct`
  (mengikuti bahasa).
- Setiap angka yang berasal dari sumber luar punya tautan atau keterangan sumber di dekatnya.
- Status memakai nama state brief: PUBLISHED, HELD, ARCHIVED.
- Semua teks lewat `t()` di `app/i18n.py`, tiga bahasa.
- Tidak ada gradien, bayangan tebal, ikon dekoratif, atau animasi. Emoji hanya 👍/👎 yang
  sudah dipakai.
- Halaman baru meniru struktur halaman yang ada: `.kepala` (kicker + judul), lalu kartu.
- Penafian riset tampil sebagai `.pita.fixture` di halaman analisis.
