const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.3 x 7.5 in
pres.author = "Tim AAIC 2026";
pres.title = "Rapat Perdana AAIC 2026";

const INK = "1A1A1A";
const MUTED = "5A5A5A";
const ACCENT = "1F6F5C";
const LINE = "C9CFCC";
const BODY = "Calibri";

const M = 0.7;                           // margin kiri/kanan
const W = 13.3 - M * 2;                  // lebar konten

let n = 0;

function slide(opts = {}) {
  n += 1;
  const s = pres.addSlide();
  s.background = { color: "FFFFFF" };
  if (!opts.noNumber) {
    s.addText(String(n), {
      x: 13.3 - M - 0.6, y: 6.85, w: 0.6, h: 0.3,
      fontFace: BODY, fontSize: 10, color: MUTED, align: "right", isTextBox: true,
    });
  }
  return s;
}

function label(s, text) {
  s.addText(text, {
    x: M, y: 0.45, w: W, h: 0.3,
    fontFace: BODY, fontSize: 12, bold: true, color: ACCENT,
    charSpacing: 1.2, isTextBox: true, margin: 0,
  });
}

function title(s, text, y = 0.82) {
  s.addText(text, {
    x: M, y, w: W, h: 0.85,
    fontFace: BODY, fontSize: 32, bold: true, color: INK,
    isTextBox: true, margin: 0,
  });
}

function lead(s, text, y = 1.72) {
  s.addText(text, {
    x: M, y, w: W, h: 0.6,
    fontFace: BODY, fontSize: 16, color: MUTED,
    isTextBox: true, margin: 0,
  });
}

function bullets(s, items, opts = {}) {
  const runs = items.map((t, i) => ({
    text: typeof t === "string" ? t : t.text,
    options: {
      bullet: true,
      breakLine: i < items.length - 1,
      bold: typeof t === "object" && t.bold ? true : false,
      paraSpaceAfter: opts.gap === undefined ? 10 : opts.gap,
    },
  }));
  s.addText(runs, {
    x: opts.x === undefined ? M : opts.x,
    y: opts.y === undefined ? 2.4 : opts.y,
    w: opts.w === undefined ? W : opts.w,
    h: opts.h === undefined ? 4.1 : opts.h,
    fontFace: BODY, fontSize: opts.size === undefined ? 16 : opts.size,
    color: INK, isTextBox: true, valign: "top",
  });
}

function note(s, text, y = 6.25) {
  s.addText(text, {
    x: M, y, w: W - 0.8, h: 0.55,
    fontFace: BODY, fontSize: 13, italic: true, color: MUTED,
    isTextBox: true, margin: 0,
  });
}

function table(s, rows, opts = {}) {
  s.addTable(rows, {
    x: opts.x === undefined ? M : opts.x,
    y: opts.y === undefined ? 2.4 : opts.y,
    w: opts.w === undefined ? W : opts.w,
    colW: opts.colW,
    fontFace: BODY,
    fontSize: opts.size === undefined ? 15 : opts.size,
    color: INK,
    border: { type: "solid", pt: 0.75, color: LINE },
    autoPage: false,
    valign: "top",
  });
}

function head(cells) {
  return cells.map((t) => ({
    text: t,
    options: { bold: true, color: "FFFFFF", fill: { color: ACCENT }, margin: 6 },
  }));
}

function row(cells, opts = {}) {
  return cells.map((t, i) => ({
    text: t,
    options: {
      margin: 6,
      bold: opts.boldFirst && i === 0,
      fill: opts.fill ? { color: opts.fill } : undefined,
    },
  }));
}

/* ------------------------------------------------------------------ */
/* 1 — Judul                                                           */
/* ------------------------------------------------------------------ */
{
  const s = slide({ noNumber: true });
  s.addText("Rapat Perdana", {
    x: M, y: 2.25, w: W, h: 0.95,
    fontFace: BODY, fontSize: 44, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addText("Agentic AI Campus Innovation Competition 2026", {
    x: M, y: 3.2, w: W, h: 0.5,
    fontFace: BODY, fontSize: 22, color: MUTED, isTextBox: true, margin: 0,
  });
  s.addShape(pres.ShapeType.line, {
    x: M, y: 3.95, w: 3.2, h: 0, line: { color: ACCENT, width: 2 },
  });
  s.addText("13 September 2026  ·  90 menit  ·  Tim 3 orang", {
    x: M, y: 4.2, w: W, h: 0.4,
    fontFace: BODY, fontSize: 15, color: MUTED, isTextBox: true, margin: 0,
  });
  s.addNotes("Buka dengan tanggal dan hadiah, jangan dengan teknis. Minta izin bicara 20 menit tanpa interupsi.");
}

/* ------------------------------------------------------------------ */
/* 2 — Tujuan rapat                                                    */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "TUJUAN");
  title(s, "Rapat ini berhasil kalau…");
  s.addText(
    "…di akhir, kita bertiga bisa menyebutkan sendiri apa yang kita kerjakan besok.",
    {
      x: M, y: 1.95, w: W - 1.5, h: 0.9,
      fontFace: BODY, fontSize: 24, bold: true, color: ACCENT, isTextBox: true, margin: 0,
    }
  );
  s.addText("Bukan kalau kita semua paham arsitekturnya.", {
    x: M, y: 2.85, w: W, h: 0.4,
    fontFace: BODY, fontSize: 17, color: MUTED, isTextBox: true, margin: 0,
  });

  s.addText("Susunan hari ini", {
    x: M, y: 3.6, w: W, h: 0.35,
    fontFace: BODY, fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  bullets(s, [
    "Fakta dasar lombanya — 10 menit",
    "Hal yang mengubah cara kita kerja — 10 menit",
    "Kita mau bikin apa — 20 menit",
    "Diskusi terbuka, giliran kalian — 15 menit",
    "Lima keputusan — 20 menit",
    "Pembagian tugas & penutup — 10 menit",
  ], { y: 4.0, h: 2.2, size: 15, gap: 6 });
  s.addNotes("Sebutkan bahwa target rapat cuma lima keputusan, bukan sepakat semua detail.");
}

/* ------------------------------------------------------------------ */
/* 3 — Lombanya apa                                                    */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 1 — FAKTA DASAR");
  title(s, "Lombanya apa");
  bullets(s, [
    "Lomba nasional Taiwan, dibina Kementerian Pendidikan (MOE)",
    "Diselenggarakan NAPAI, barengan konferensi AI nasional TAAI 2026",
    "Pesertanya mahasiswa aktif se-Taiwan, semua jurusan",
    "Tim 2–5 orang — kita bertiga sudah sah",
    "Temanya: bikin Agentic AI yang menyelesaikan masalah nyata",
  ], { y: 2.1, h: 2.6 });

  s.addText("Yang dimaksud \"Agentic AI\" di sini", {
    x: M, y: 4.75, w: W, h: 0.35,
    fontFace: BODY, fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addText(
    "Sistem yang punya tujuan, memecah tujuan itu jadi beberapa langkah, memanggil tool atau sistem lain, dan menyesuaikan langkah berikutnya berdasarkan hasil yang dia dapat. Bukan chatbot yang menjawab sekali lalu selesai.",
    {
      x: M, y: 5.1, w: W - 0.8, h: 1.0,
      fontFace: BODY, fontSize: 15, color: MUTED, isTextBox: true, margin: 0,
    }
  );
}

/* ------------------------------------------------------------------ */
/* 4 — Hadiah                                                          */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 1 — FAKTA DASAR");
  title(s, "Hadiah dan peluangnya");
  lead(s, "Total NT$150.000, dibagi rata ke dua kelompok. Kita di Kelompok B.");

  table(s, [
    head(["Penghargaan", "Tim per kelompok", "Per tim"]),
    row(["Juara 1", "1 tim", "NT$25.000"], { boldFirst: true }),
    row(["Juara 2", "1 tim", "NT$15.000"], { boldFirst: true }),
    row(["Juara 3", "1 tim", "NT$10.000"], { boldFirst: true }),
    row(["Honorable mention", "5 tim", "NT$5.000"], { boldFirst: true }),
  ], { y: 2.45, colW: [4.2, 4.0, 3.7], size: 16 });

  s.addText("8 tim menang per kelompok", {
    x: M, y: 5.2, w: W, h: 0.45,
    fontFace: BODY, fontSize: 20, bold: true, color: ACCENT, isTextBox: true, margin: 0,
  });
  note(s, "Peluangnya tidak kecil — ini bukan lomba dengan satu pemenang. Finalis dan pemenang sama-sama dapat sertifikat.", 5.7);
}

/* ------------------------------------------------------------------ */
/* 5 — Tanggal                                                         */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 1 — FAKTA DASAR");
  title(s, "Tanggal yang mengikat");

  table(s, [
    head(["Tanggal", "Apa yang terjadi"]),
    row(["18 Sep, 14:00", "Briefing & workshop dari panitia — kita bertiga hadir"], { boldFirst: true }),
    row(["16 Okt, 23:59", "Batas pendaftaran + submisi penyisihan"], { boldFirst: true, fill: "EDF3F1" }),
    row(["6 Nov", "Pengumuman finalis"], { boldFirst: true }),
    row(["13 Nov, 23:59", "Batas materi final (kalau lolos)"], { boldFirst: true }),
    row(["21 Nov", "Final & showcase di New Taipei"], { boldFirst: true, fill: "EDF3F1" }),
  ], { y: 2.1, colW: [3.2, 8.7], size: 15 });

  s.addText("Dari hari ini ke 16 Oktober: 33 hari.", {
    x: M, y: 5.5, w: W, h: 0.45,
    fontFace: BODY, fontSize: 20, bold: true, color: ACCENT, isTextBox: true, margin: 0,
  });
  note(s, "Briefing 18 September tinggal 5 hari lagi. Di situ panitia kemungkinan menjelaskan data dan kunci jawaban yang dipakai menilai.", 6.0);
}

/* ------------------------------------------------------------------ */
/* 6 — REFRAME: dua gerbang                                            */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 2 — INI YANG PALING PENTING");
  title(s, "Ada dua penilaian, bukan satu");
  lead(s, "Kalau cuma satu hal yang diingat dari rapat ini, ini orangnya.");

  table(s, [
    head(["", "GERBANG 1 — 16 Oktober", "GERBANG 2 — 13 & 21 November"]),
    row([
      "Bentuknya",
      "Review dokumen",
      "Sistem yang benar-benar jalan",
    ], { boldFirst: true }),
    row([
      "Yang dikumpulkan",
      "Deck 12 halaman\nVideo 4 menit\nBukti lapangan\nFormulir pendaftaran",
      "Prototipe + akun untuk juri\nRepo kode + dokumentasi\nAngka hasil pengujian\nDemo langsung di panggung",
    ], { boldFirst: true }),
    row([
      "Tidak diminta",
      "Sistem produksi\nAkurasi tinggi\nSource code",
      "—",
    ], { boldFirst: true }),
    row([
      "Berlaku untuk",
      "Semua peserta",
      "Hanya yang lolos finalis",
    ], { boldFirst: true, fill: "EDF3F1" }),
  ], { y: 2.35, colW: [2.3, 4.8, 4.8], size: 14 });

  s.addNotes("Berhenti sebentar setelah slide ini. Biasanya di sini orang mulai bertanya — itu bagus.");
}

/* ------------------------------------------------------------------ */
/* 7 — Artinya buat kita                                               */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 2 — INI YANG PALING PENTING");
  title(s, "Artinya buat 33 hari ke depan");

  s.addText("Kita TIDAK sedang mengejar produk jadi.", {
    x: M, y: 2.0, w: W, h: 0.55,
    fontFace: BODY, fontSize: 26, bold: true, color: ACCENT, isTextBox: true, margin: 0,
  });
  s.addText("Yang dikejar sampai 16 Oktober cuma tiga hal:", {
    x: M, y: 2.7, w: W, h: 0.4,
    fontFace: BODY, fontSize: 17, color: MUTED, isTextBox: true, margin: 0,
  });

  bullets(s, [
    { text: "Bukti lapangan — wawancara calon pengguna, terdokumentasi", bold: true },
    { text: "Satu alur kecil yang benar-benar jalan — cukup untuk direkam 4 menit", bold: true },
    { text: "Argumen yang meyakinkan — kenapa masalah ini butuh agent, bukan chatbot", bold: true },
  ], { y: 3.25, h: 1.8, size: 18, gap: 14 });

  s.addText(
    "Dua dari tiga hal itu tidak butuh coding sama sekali. Itu sebabnya tim bertiga dengan satu orang teknis tetap punya peluang.",
    {
      x: M, y: 5.3, w: W - 0.8, h: 0.9,
      fontFace: BODY, fontSize: 16, color: INK, isTextBox: true, margin: 0,
    }
  );
}

/* ------------------------------------------------------------------ */
/* 8 — Track mana                                                      */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 3 — KITA MAU BIKIN APA");
  title(s, "Dua pilihan topik di Kelompok B");
  lead(s, "Topiknya sudah ditentukan panitia bersama mitra perusahaan. Kita pilih satu.");

  table(s, [
    head(["", "SYSTEX — Agen Saham", "Ai3 — Agen Subsidi Pemerintah"]),
    row([
      "Masalahnya",
      "Investor kesulitan menyaring saham dan memahami risikonya dengan cepat",
      "Warga bingung apakah berhak dapat subsidi pengasuhan anak / sewa rumah",
    ], { boldFirst: true }),
    row([
      "Sumber data",
      "Situs bursa Taiwan: MOPS, TWSE, TPEx",
      "Situs resmi pemerintah Taipei, New Taipei, Taoyuan",
    ], { boldFirst: true }),
    row([
      "Enaknya",
      "Data melimpah, sumber jelas",
      "Aturannya terbatas dan stabil, lebih mudah diuji",
    ], { boldFirst: true }),
    row([
      "Sulitnya",
      "Angka finansial rawan salah, situs memblokir IP luar Taiwan",
      "Aturan subsidi bisa berubah",
    ], { boldFirst: true }),
  ], { y: 2.45, colW: [1.9, 5.0, 5.0], size: 13 });

  s.addText("Usulan: SYSTEX — tapi diputuskan hari ini setelah lihat hasil uji akses data.", {
    x: M, y: 6.1, w: W - 0.8, h: 0.5,
    fontFace: BODY, fontSize: 15, bold: true, color: ACCENT, isTextBox: true, margin: 0,
  });
}

/* ------------------------------------------------------------------ */
/* 9 — Perumpamaan                                                     */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 3 — KITA MAU BIKIN APA");
  title(s, "Bayangkan punya asisten riset pribadi");
  lead(s, "Tugasnya cuma satu: menjaga 20 saham yang kamu pilih.");

  bullets(s, [
    "Tiap hari dia baca semua pengumuman resmi dari perusahaan-perusahaan itu di situs bursa Taiwan. Bukan berita — pengumuman resmi yang wajib dipublikasi.",
    "Kalau ada yang penting buat KAMU khususnya — bukan penting secara umum — dia kirim memo pendek.",
    "Di memo selalu ada keterangan: \"ini saya ambil dari dokumen ini, tanggal ini\". Jadi kamu bisa cek sendiri.",
    "Sebelum memo dikirim, tiap angka dicocokkan ulang ke dokumen aslinya. Kalau tidak cocok, memo tidak jadi dikirim — dia lapor \"ada yang aneh, tolong dicek manusia\".",
    "Kalau kamu terus-terusan mengabaikan memo soal topik tertentu, dia belajar dan berhenti mengirim yang itu.",
  ], { y: 2.4, h: 3.7, size: 15, gap: 11 });

  s.addNotes("Jangan pakai diagram di sini. Diagram baru keluar kalau ada yang minta.");
}

/* ------------------------------------------------------------------ */
/* 10 — Empat tahap                                                    */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 3 — KITA MAU BIKIN APA");
  title(s, "Kelima hal tadi bukan kebetulan");
  lead(s, "Panitia meminta alur kerja empat tahap. Kita rancang supaya persis cocok.");

  table(s, [
    head(["Yang diminta panitia", "Wujudnya di produk kita"]),
    row(["1. Personalized intelligence", "Watchlist dan profil risiko milik tiap investor"], { boldFirst: true }),
    row(["2. Proactive delivery", "Agent yang mengirim duluan, tanpa perlu ditanya"], { boldFirst: true }),
    row(["3. Behavioral feedback", "Sistem membaca reaksi: dibuka, diabaikan, ditandai penting"], { boldFirst: true }),
    row(["4. Continuous optimization", "Ambang relevansi disetel ulang dari reaksi itu"], { boldFirst: true }),
  ], { y: 2.5, colW: [4.6, 7.3], size: 15 });

  s.addText(
    "Kebanyakan tim kemungkinan berhenti di tahap 1 — bikin chat \"tanya saham, dapat ringkasan\". Tahap 2 dan 3 itu pembedanya.",
    {
      x: M, y: 5.5, w: W - 0.8, h: 0.9,
      fontFace: BODY, fontSize: 16, color: INK, isTextBox: true, margin: 0,
    }
  );
}

/* ------------------------------------------------------------------ */
/* 11 — Arsitektur                                                     */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 3 — KITA MAU BIKIN APA");
  title(s, "Kalau dilihat dari dalam: tiga lapis");

  const rows = [
    ["Lapis 1", "Arsip pengumuman", "Semua pengumuman resmi dikumpulkan dan dirapikan. Tiap dokumen selalu menyimpan alamat sumber dan tanggalnya — ini yang bikin sitasi bisa dibuktikan."],
    ["Lapis 2", "Si agent", "Yang mikir dan mutusin: cari, baca, nilai penting atau tidak, susun memo. Termasuk pengecek angka yang menolak memo kalau datanya tidak cocok."],
    ["Lapis 3", "Dua pintu keluar", "(a) Feed peringatan untuk pengguna. (b) Kolom tanya-jawab supaya juri bisa menguji dengan soal mereka sendiri."],
  ];

  let y = 2.25;
  rows.forEach(([tag, name, desc]) => {
    s.addText(tag, {
      x: M, y, w: 1.15, h: 0.4,
      fontFace: BODY, fontSize: 13, bold: true, color: ACCENT, isTextBox: true, margin: 0,
    });
    s.addText(name, {
      x: M + 1.25, y, w: 3.0, h: 0.4,
      fontFace: BODY, fontSize: 17, bold: true, color: INK, isTextBox: true, margin: 0,
    });
    s.addText(desc, {
      x: M + 4.35, y, w: W - 4.35, h: 1.1,
      fontFace: BODY, fontSize: 14, color: MUTED, isTextBox: true, margin: 0,
    });
    y += 1.35;
  });

  s.addText("Yang perlu kalian tahu cuma ini. Detail teknisnya urusan jalur Agent & Data.", {
    x: M, y: 6.2, w: W - 0.8, h: 0.45,
    fontFace: BODY, fontSize: 14, italic: true, color: MUTED, isTextBox: true, margin: 0,
  });
}

/* ------------------------------------------------------------------ */
/* 12 — Yang tidak dibangun                                            */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 3 — KITA MAU BIKIN APA");
  title(s, "Yang sengaja TIDAK kita bangun");
  lead(s, "Bukan karena tidak mampu — tapi karena aturannya melarang, dan menahan diri justru dinilai bagus.");

  table(s, [
    head(["Tidak dibangun", "Alasan"]),
    row(["Beli–jual saham otomatis", "Aturan melarang sistem melakukan transaksi tanpa persetujuan manusia"], { boldFirst: true }),
    row(["Ramalan harga saham", "Tidak bisa ditunjukkan sumbernya, jadi tidak bisa diverifikasi juri"], { boldFirst: true }),
    row(["Pengaturan portofolio", "Menambah pekerjaan tanpa menambah nilai penilaian"], { boldFirst: true }),
    row(["Chat serba bisa", "Melebar, dan justru melemahkan alasan kenapa ini harus agent"], { boldFirst: true }),
  ], { y: 2.75, colW: [4.3, 7.6], size: 15 });

  s.addText(
    "Aturan menyebut jelas: untuk urusan keuangan, adanya persetujuan manusia dan tombol berhenti DIHITUNG sebagai desain yang baik.",
    {
      x: M, y: 5.7, w: W - 0.8, h: 0.9,
      fontFace: BODY, fontSize: 16, bold: true, color: ACCENT, isTextBox: true, margin: 0,
    }
  );
}

/* ------------------------------------------------------------------ */
/* 13 — Cara nilai dihitung                                            */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 3 — KITA MAU BIKIN APA");
  title(s, "Cara juri menghitung nilai");
  lead(s, "Berguna supaya kita tahu ke mana energi diarahkan.");

  table(s, [
    head(["Penyisihan — 16 Okt", "%", "Final — 21 Nov", "%"]),
    row(["Bukti masalah & lapangan", "20", "Tugas selesai & stabil", "25"]),
    row(["Ketepatan desain agent", "20", "Dampak lapangan & validasi", "20"]),
    row(["Rencana teknis & data", "20", "Kedalaman teknis agent", "20"]),
    row(["Prototipe & rencana uji", "15", "Keamanan & kontrol", "15"]),
    row(["Inovasi & daya sebar", "15", "Inovasi & daya sebar", "10"]),
    row(["Keamanan & etika", "10", "Demo & tanya jawab", "10"]),
  ], { y: 2.5, colW: [4.4, 1.0, 4.5, 1.0], size: 14 });

  s.addText(
    "Dua kriteria teratas penyisihan = 40% nilai, dan tidak satu pun butuh baris kode.",
    {
      x: M, y: 6.0, w: W - 0.8, h: 0.5,
      fontFace: BODY, fontSize: 16, bold: true, color: ACCENT, isTextBox: true, margin: 0,
    }
  );
}

/* ------------------------------------------------------------------ */
/* 14 — Tiga jalur                                                     */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 4 — PEMBAGIAN KERJA");
  title(s, "Tiga jalur yang jalan bersamaan");
  lead(s, "Bukan tiga tahap berurutan. Ketiganya dikerjakan paralel dari minggu ini.");

  table(s, [
    head(["Jalur", "Isinya", "Target 16 Oktober"]),
    row([
      "Agent & Data",
      "Ambil data, bangun agent, bikin alur yang jalan",
      "Satu saham, satu kejadian, satu peringatan bersitasi — jalan dari awal sampai akhir",
    ], { boldFirst: true }),
    row([
      "Lapangan & Bukti",
      "Wawancara calon pengguna, kumpulkan bukti, susun soal uji",
      "6–8 wawancara terdokumentasi + 30–50 soal berlabel beserta sumber jawabannya",
    ], { boldFirst: true }),
    row([
      "Produk & Submisi",
      "Deck, video, pendaftaran, tenggat",
      "Semua berkas terkirim 15 Oktober — sehari sebelum tenggat",
    ], { boldFirst: true }),
  ], { y: 2.55, colW: [2.6, 4.3, 5.0], size: 14 });

  note(s, "Jalur mana yang kalian ambil, kita putuskan nanti di bagian keputusan.", 6.2);
}

/* ------------------------------------------------------------------ */
/* 15 — Timeline                                                       */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 4 — PEMBAGIAN KERJA");
  title(s, "Peta 33 hari");

  table(s, [
    head(["Kapan", "Fokusnya"]),
    row(["13–18 Sep", "Kunci arah: uji akses data, tentukan scope, hadir briefing"], { boldFirst: true, fill: "EDF3F1" }),
    row(["19–27 Sep", "Wawancara calon pengguna + mulai kumpulkan data"], { boldFirst: true }),
    row(["28 Sep – 8 Okt", "Bikin satu alur yang jalan + susun soal uji"], { boldFirst: true }),
    row(["9–14 Okt", "Produksi deck 12 halaman dan video 4 menit"], { boldFirst: true }),
    row(["15–16 Okt", "Kirim berkas penyisihan"], { boldFirst: true, fill: "EDF3F1" }),
    row(["17 Okt – 21 Nov", "Kalau lolos: perkuat sistem, latihan demo, final"], { boldFirst: true }),
  ], { y: 2.1, colW: [3.3, 8.6], size: 15 });

  note(s, "Minggu ini targetnya cuma satu: memastikan datanya benar-benar bisa diambil.", 6.1);
}

/* ------------------------------------------------------------------ */
/* 16 — LIMA KEPUTUSAN                                                 */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 5 — INTI RAPAT");
  title(s, "Lima keputusan yang harus keluar hari ini");
  lead(s, "Semua sudah ada usulannya. Usulan, bukan keputusan — silakan dibantah.");

  table(s, [
    head(["#", "Pertanyaan", "Usulan"]),
    row(["1", "Kita ambil track yang mana?", "SYSTEX, kalau uji akses data lolos"]),
    row(["2", "Scope-nya apa, dalam satu kalimat?", "Agen pemantau 20 saham dengan peringatan bersitasi"]),
    row(["3", "Siapa pegang jalur apa?", "Ditawarkan, bukan ditunjuk"]),
    row(["4", "Ritme kerjanya bagaimana?", "2× seminggu, 30 menit, hari tetap"]),
    row(["5", "Siapa mendaftarkan tim, kapan?", "Jalur Produk & Submisi, sebelum 18 September"]),
  ], { y: 2.5, colW: [0.7, 5.4, 5.8], size: 15 });

  s.addText("Jangan ada satu pun yang mengambang ke rapat berikutnya.", {
    x: M, y: 6.0, w: W - 0.8, h: 0.5,
    fontFace: BODY, fontSize: 16, bold: true, color: ACCENT, isTextBox: true, margin: 0,
  });
}

/* ------------------------------------------------------------------ */
/* 17 — Tidak dibahas                                                  */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "BAGIAN 5 — INTI RAPAT");
  title(s, "Yang sengaja tidak dibahas hari ini");

  bullets(s, [
    "Nama tim, logo, nama produk",
    "Desain tampilan dan pilihan warna",
    "Bahasa pemrograman dan framework",
    "Model AI mana yang dipakai",
    "Cara bagi hadiah kalau menang",
  ], { y: 2.15, h: 2.2, size: 18, gap: 10 });

  s.addText(
    "Semuanya terasa penting dan menyenangkan dibahas — tapi tidak satu pun mengubah apa yang kita kerjakan besok. Rapat pertama yang habis membahas nama tim adalah pola kegagalan yang sangat umum.",
    {
      x: M, y: 4.6, w: W - 1.2, h: 1.1,
      fontFace: BODY, fontSize: 16, color: INK, isTextBox: true, margin: 0,
    }
  );
  s.addText("Kalau terangkat, kita catat di daftar tunda dan lanjut.", {
    x: M, y: 5.75, w: W - 1.2, h: 0.45,
    fontFace: BODY, fontSize: 15, italic: true, color: MUTED, isTextBox: true, margin: 0,
  });
}

/* ------------------------------------------------------------------ */
/* 18 — Bawa pulang                                                    */
/* ------------------------------------------------------------------ */
{
  const s = slide();
  label(s, "PENUTUP");
  title(s, "Yang kita bawa pulang hari ini");
  lead(s, "Sebelum bubar, masing-masing menyebutkan ini dengan kalimat sendiri.");

  table(s, [
    head(["Jalur", "Tugas sampai rapat berikutnya"]),
    row(["Agent & Data", "Uji ambil pengumuman untuk 5 saham. Target: bisa bilang \"bisa\" atau \"tidak bisa\" dengan bukti, bukan dugaan."], { boldFirst: true }),
    row(["Lapangan & Bukti", "Susun daftar 12 calon narasumber, kirim pesan ke 5 orang pertama. Target: 2 wawancara terjadwal sebelum 20 September."], { boldFirst: true }),
    row(["Produk & Submisi", "Daftarkan tim, dan siapkan kerangka kosong 12 halaman deck. Target: siap diisi sebelum 20 September."], { boldFirst: true }),
    row(["Bertiga", "Hadir briefing 18 September 14:00. Masing-masing siapkan satu pertanyaan untuk panitia."], { boldFirst: true, fill: "EDF3F1" }),
  ], { y: 2.5, colW: [2.9, 9.0], size: 14 });

  s.addText("Rapat berikutnya: ____________________", {
    x: M, y: 6.1, w: W - 0.8, h: 0.5,
    fontFace: BODY, fontSize: 17, bold: true, color: INK, isTextBox: true, margin: 0,
  });
}

pres.writeFile({ fileName: "Rapat-Perdana-AAIC-2026.pptx" }).then((f) => {
  console.log("Tersimpan:", f, "—", n, "slide");
});
