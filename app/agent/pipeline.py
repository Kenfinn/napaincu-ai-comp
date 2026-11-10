"""Orkestrasi lima tahap, dan pencatat jejaknya.

Jejak bukan pelengkap. Pra-final butir 4 mewajibkan **minimal satu operation trace**,
dan Appendix 2 meminta latensi, biaya, jumlah retry, tingkat intervensi manusia, serta
kategori error. Dengan menuliskannya sebagai bagian dari pemakaian biasa, berkas itu
lahir sendiri dari sistem yang jalan — bukan dikarang menjelang tenggat.

Empat akhir yang mungkin, dan tiga di antaranya bukan "terbit":

    dilewati  pasal tidak menyentuh valuasi, tidak pernah sampai ke model
    ditahan   tidak ada angka yang bisa ditarik dengan sumbernya — antre ke manusia
    ditolak   pemeriksa menggagalkan klaim — alasannya tercatat, peringatan tidak terbit
    terbit    lolos seluruh pemeriksaan

Kemampuan berhenti inilah yang membedakan agent dari pipeline kaku, dan itu butir 3
gerbang kelayakan Pasal 4.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

from .. import config, review, store
from . import extract, recompute, screen, verify
from ..i18n import pesan

# Nama state di brief hal. 7. Status internal tetap berbahasa Indonesia supaya jejak
# lama tetap terbaca; yang tampil ke pengguna dan juri adalah nama state brief.
STATE = {"terbit": "PUBLISHED", "ditahan": "HELD", "dilewati": "ARCHIVED", "ditolak": "REJECTED"}


def _sekarang() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Jejak:
    """Pencatat langkah. Satu baris per tahap, selalu, termasuk saat berhenti."""

    def __init__(self, pengenal: str):
        self.pengenal = pengenal
        self.langkah: list[dict] = []
        self.mulai = time.monotonic()
        self.mulai_iso = _sekarang()

    def catat(self, nama: str, status: str, masukan, keluaran, meta: dict | None = None,
              t0: float | None = None, i18n: dict | None = None, state: str | None = None) -> None:
        self.langkah.append({
            "tahap_i18n": i18n,
            "state": state,
            "urutan": len(self.langkah),
            "tahap": nama,
            "status": status,
            "waktu": _sekarang(),
            "durasi_ms": int((time.monotonic() - (t0 if t0 is not None else self.mulai)) * 1000),
            "masukan": masukan,
            "keluaran": keluaran,
            "meta": meta or {},
        })

    def ringkas(self) -> dict:
        tokens_in = sum(l["meta"].get("token_masuk", 0) for l in self.langkah)
        tokens_out = sum(l["meta"].get("token_keluar", 0) for l in self.langkah)
        return {
            "durasi_total_ms": int((time.monotonic() - self.mulai) * 1000),
            "langkah": len(self.langkah),
            "token_masuk": tokens_in,
            "token_keluar": tokens_out,
            "biaya_usd": sum(l["meta"].get("biaya_usd", 0.0) for l in self.langkah),
            "retry": sum(l["meta"].get("retry", 0) for l in self.langkah),
            "pakai_cadangan": any(l["meta"].get("cadangan") for l in self.langkah),
            "panggilan_model": sum(1 for l in self.langkah
                                   if l["meta"].get("penyedia") not in (None, "aturan")
                                   and not l["meta"].get("cache")),
            "jawaban_cache": sum(1 for l in self.langkah if l["meta"].get("cache")),
        }


def jalankan(detail: dict, d_valuasi: dict | None) -> dict:
    """Proses satu pengumuman dari ujung ke ujung."""
    pengenal = store.id_pengumuman(detail)
    j = Jejak(pengenal)

    ringkas_dok = {
        "kode": detail.get("code"), "nama": detail.get("name"),
        "tanggal": detail.get("date"), "judul": detail.get("subject"),
        "pasal": detail.get("clause"), "sumber": detail.get("source_url"),
    }

    # --- FETCHED · VALIDATED: terjadi di penarik, dicatat ulang di sini --------
    # supaya satu jejak memuat seluruh perjalanan pengumuman, sejak diambil.
    j.catat("Ambil dari sumber", "lolos",
            {"sumber": detail.get("sumber_data") or "MOPS"},
            {"ditarik": detail.get("fetched_at"), "sumber_url": detail.get("source_url")},
            i18n=pesan("tahap.ambil"), state="FETCHED")
    j.catat("Validasi bentuk", "lolos", {},
            {"butir": len(detail.get("items") or []), "pasal": detail.get("clause_raw"),
             "data_pribadi_dibuang": detail.get("dropped_pii", [])},
            i18n=pesan("tahap.validasi"), state="VALIDATED")

    # --- tahap 0 -----------------------------------------------------------
    t0 = time.monotonic()
    hasil_saring = screen.saring(detail)
    j.catat("0 · Saringan pasal", "lolos" if hasil_saring["lolos"] else "berhenti",
            ringkas_dok, hasil_saring, t0=t0, i18n=pesan("tahap.saring"), state="SCREENED")

    if not hasil_saring["lolos"]:
        return _selesai(j, "dilewati", detail, None, hasil_saring["alasan"],
                        hasil_saring.get("alasan_i18n"))

    # --- tahap 1 & 2 -------------------------------------------------------
    # Pemilah dan penyari digabung dalam satu panggilan: pertanyaan "input mana yang
    # tersentuh" dan "angkanya berapa" dijawab dari dokumen yang sama, dan memisahnya
    # jadi dua panggilan menggandakan biaya tanpa menambah ketepatan.
    t0 = time.monotonic()
    temuan, meta = extract.sari(detail, hasil_saring["input_mungkin"])
    status = "lolos" if temuan else "berhenti"
    j.catat("1–2 · Pemilah & penyari", status,
            {"kandidat_input": hasil_saring["input_mungkin"]},
            {"jumlah_temuan": len(temuan), "temuan": temuan}, meta, t0=t0,
            i18n=pesan("tahap.pilah_sari"), state="TRIAGED · EXTRACTED")

    if meta.get("injeksi_terdeteksi"):
        j.catat("· Penanda injeksi", "tercatat",
                {"penanda": meta["injeksi_terdeteksi"]},
                {"tindakan": "Tidak mengubah perilaku. Teks dokumen adalah data, "
                             "bukan perintah. Dicatat untuk ditinjau manusia."},
                i18n=pesan("tahap.injeksi"))

    if not temuan:
        # Tidak ada yang bisa diterbitkan: manusia hanya bisa mengarsipkan.
        return _selesai(j, "ditahan", detail, {"tahan": {"jenis": "tanpa_angka", "boleh_setujui": False}},
                        "Tidak ada angka yang bisa ditarik lengkap dengan kalimat sumbernya.",
                        pesan("akhir.tanpa_angka"))

    if d_valuasi is None:
        return _selesai(j, "ditahan", detail,
                        {"tahan": {"jenis": "tanpa_valuasi", "boleh_setujui": True}, "temuan": temuan},
                        f"Belum ada berkas valuasi untuk emiten {detail.get('code')}. "
                        f"Angka tertarik, tapi tidak ada model untuk menghitung ulang.",
                        pesan("akhir.tanpa_valuasi", kode=detail.get("code")))

    # --- tahap 3 & 4 per temuan -------------------------------------------
    diterima, ditolak = [], []
    for t in temuan:
        t0 = time.monotonic()
        cek_awal = verify.periksa(t, detail, d_valuasi)
        v_awal = verify.vonis(cek_awal)
        j.catat(f"4a · Pemeriksa pra-hitung ({t['input']})",
                "lolos" if v_awal["lolos"] else "tolak",
                {"temuan": t}, {"cek": cek_awal, "vonis": v_awal}, t0=t0,
                i18n=pesan("tahap.periksa_awal", input=t["input"]), state="VERIFIED · sumber")

        if not v_awal["lolos"]:
            ditolak.append({"temuan": t, "sebab": v_awal["sebab"],
                            "sebab_i18n": v_awal["sebab_i18n"], "gagal_kode": _gagal_kode(cek_awal)})
            continue

        t0 = time.monotonic()
        hasil = recompute.hitung_ulang(d_valuasi, t["input"], t["nilai_juta_ntd"])
        j.catat(f"3 · Penghitung ({t['input']})", "lolos",
                {"input": t["input"], "nilai_baru": t["nilai_juta_ntd"]},
                _ringkas_hitung(hasil), t0=t0, i18n=pesan("tahap.hitung", input=t["input"]),
                state="VALUED")

        t0 = time.monotonic()
        cek_akhir = verify.periksa_hasil(hasil)
        v_akhir = verify.vonis(cek_akhir)
        j.catat(f"4b · Pemeriksa pasca-hitung ({t['input']})",
                "lolos" if v_akhir["lolos"] else "tolak",
                {"input": t["input"]}, {"cek": cek_akhir, "vonis": v_akhir}, t0=t0,
                i18n=pesan("tahap.periksa_akhir", input=t["input"]), state="VERIFIED · hitungan")

        if v_akhir["lolos"]:
            diterima.append({"temuan": t, "hasil": hasil, "cek": cek_awal + cek_akhir})
        else:
            ditolak.append({"temuan": t, "sebab": v_akhir["sebab"],
                            "sebab_i18n": v_akhir["sebab_i18n"], "gagal_kode": _gagal_kode(cek_akhir)})

    if not diterima:
        # Dua temuan sering gagal dengan sebab yang sama persis (mis. satu mata uang
        # asing menyentuh dua input). Diulang apa adanya, ringkasannya jadi dinding
        # teks yang tidak terbaca, jadi disaring unik dengan urutan tetap dijaga.
        unik = list(dict.fromkeys(s for d in ditolak for s in d["sebab"]))
        unik_i18n, lihat = [], set()
        for d in ditolak:
            for s in d["sebab_i18n"]:
                k = repr(s)
                if k not in lihat:
                    lihat.add(k)
                    unik_i18n.append(s)
        # Brief hal. 7: angka yang gagal verifikasi → HELD FOR REVIEW, manusia memutuskan.
        # Boleh disetujui hanya bila semua kegagalannya berupa keraguan (lihat review.py).
        boleh = all(review.boleh_setujui_temuan(d["gagal_kode"]) for d in ditolak)
        return _selesai(j, "ditahan", detail,
                        {"ditolak": ditolak, "tahan": {"jenis": "verifikasi", "boleh_setujui": boleh}},
                        "; ".join(unik), unik_i18n)

    return _selesai(j, "terbit", detail,
                    {"diterima": diterima, "ditolak": ditolak},
                    f"{len(diterima)} temuan lolos seluruh pemeriksaan.",
                    pesan("akhir.terbit", n=len(diterima)))


def _gagal_kode(cek: list[dict]) -> list[str]:
    return [(c.get("nama_i18n") or {}).get("kode") or c["nama"] for c in cek if not c["lolos"]]


def _ringkas_hitung(h: dict) -> dict:
    """Simpan yang perlu dibaca manusia di jejak, bukan seluruh keluaran kalkulator."""
    def wajar(r):
        return (r.get("forward") or {}).get("fair_value")
    return {
        "arti": h["arti"],
        "nilai_lama": h["nilai_lama"], "nilai_baru": h["nilai_baru"],
        "g_skenario": h["g_skenario"],
        "fcff0_sebelum": h["sebelum"]["fcff0"], "fcff0_sesudah": h["sesudah"]["fcff0"],
        "g_sebelum": h["sebelum"]["implied_growth"], "g_sesudah": h["sesudah"]["implied_growth"],
        "wajar_sebelum": wajar(h["sebelum"]), "wajar_sesudah": wajar(h["sesudah"]),
        "harga_pasar": h["sebelum"]["price_per_share"],
        "melampaui_batas": h["melampaui_batas"],
    }


def _terapkan_review(j: Jejak, status: str, muatan, alasan: str, alasan_i18n):
    """Keputusan manusia atas kasus HELD diterapkan sebagai langkah terakhir."""
    if status != "ditahan":
        return status, muatan, alasan, alasan_i18n, None
    kep = review.baca().get(j.pengenal)
    if not kep:
        return status, muatan, alasan, alasan_i18n, None
    tahan = (muatan or {}).get("tahan") or {}
    if kep["keputusan"] == "setujui" and tahan.get("boleh_setujui"):
        disetujui = (muatan.get("temuan") or [d["temuan"] for d in muatan.get("ditolak", [])])
        muatan = dict(muatan, disetujui=disetujui)
        hasil = ("terbit", muatan, f"Disetujui manusia: {kep['catatan']}",
                 pesan("akhir.disetujui", catatan=kep["catatan"]))
    elif kep["keputusan"] == "arsipkan":
        hasil = ("dilewati", muatan, f"Diarsipkan manusia: {kep['catatan']}",
                 pesan("akhir.diarsipkan", catatan=kep["catatan"]))
    else:
        # Disetujui padahal tidak boleh (mis. data berubah sejak keputusan): diabaikan.
        j.catat("· Tinjauan manusia", "berhenti", {"keputusan": kep},
                {"tindakan": "Keputusan setujui diabaikan: kasus ini hanya boleh diarsipkan."},
                i18n=pesan("tahap.review_abaikan"), state="HUMAN REVIEW")
        return status, muatan, alasan, alasan_i18n, kep
    j.catat("· Tinjauan manusia", "lolos", {"keputusan": kep},
            {"status_baru": STATE[hasil[0]]}, i18n=pesan("tahap.review"), state="HUMAN REVIEW")
    return (*hasil, kep)


def _selesai(j: Jejak, status: str, detail: dict, muatan, alasan: str,
             alasan_i18n=None) -> dict:
    status, muatan, alasan, alasan_i18n, kep = _terapkan_review(j, status, muatan, alasan, alasan_i18n)
    j.catat("· Selesai", status, {}, {"alasan": alasan}, i18n=pesan("tahap.selesai"),
            state=STATE.get(status))
    hasil = {
        "state": STATE.get(status),
        "keputusan_manusia": kep,
        "id": j.pengenal,
        "contoh": bool(detail.get("_fixture")),
        "status": status,
        "alasan": alasan,
        "alasan_i18n": alasan_i18n,
        "emiten": {"kode": detail.get("code"), "nama": detail.get("name")},
        "judul": detail.get("subject"),
        "tanggal": detail.get("date"),
        "sumber_url": detail.get("source_url"),
        "mops_url": detail.get("mops_url"),
        "sumber_data": detail.get("sumber_data"),
        "jam": detail.get("time"),
        "pii_dibuang": detail.get("dropped_pii", []),
        "muatan": muatan,
        "jejak": j.langkah,
        "ringkasan": j.ringkas(),
        "mulai": j.mulai_iso,
    }
    _simpan_jejak(hasil)
    return hasil


def _simpan_jejak(hasil: dict) -> None:
    os.makedirs(config.TRACE_DIR, exist_ok=True)
    path = os.path.join(config.TRACE_DIR, f"{hasil['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=2)


def jalankan_semua() -> list[dict]:
    """Proses seluruh pengumuman yang tersedia. Dipakai aplikasi web dan CLI."""
    detail, _ = store.muat_detail()
    keluar = []
    for d in detail:
        keluar.append(jalankan(d, store.muat_valuasi(d.get("code", ""))))
    return keluar


def muat_jejak(pengenal: str) -> dict | None:
    path = os.path.join(config.TRACE_DIR, f"{pengenal}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)
