import io
exec(io.open("build_common.py", encoding="utf-8").read())

def bar(w, cls="bar", mt=0):
    return f'<div class="{cls}" style="width: {w}; margin-top: {mt}px;"></div>'

# ======================================================= 6 · JEJAK AUDIT
STEP = ('<div style="display: flex; gap: 13px; align-items: flex-start;">'
        '<div style="display: flex; flex-direction: column; align-items: center; flex: none; align-self: stretch;">'
        '<div style="width: 11px; height: 11px; border-radius: 50%; border: 2px solid @C@; background: #FFFFFF; flex: none;"></div>'
        '<div style="width: 2px; flex: 1; background: #D7DBDF; min-height: 26px;"></div></div>'
        '<div style="flex: 1; padding-bottom: 15px;">'
        '<div style="display: flex; align-items: center; gap: 10px;">'
        '<div class="bard" style="width: @W@;"></div>'
        '<div style="margin-left: auto;"><div class="bar" style="width: 46px;"></div></div></div>'
        '<div style="margin-top: 7px;">' + bar("64%") + '</div></div></div>')
STEPS = "".join(STEP.replace("@C@", "#AEB4BB").replace("@W@", w)
                for w in ("168px", "204px", "146px", "188px"))

REJECT = ('<div style="display: flex; gap: 13px; align-items: flex-start;">'
          '<div style="display: flex; flex-direction: column; align-items: center; flex: none; align-self: stretch;">'
          '<div style="width: 11px; height: 11px; border-radius: 50%; border: 2px solid #A86A0B; background: #A86A0B; flex: none;"></div>'
          '<div style="width: 2px; flex: 1; background: #D7DBDF; min-height: 26px;"></div></div>'
          '<div style="flex: 1; padding-bottom: 15px;">'
          '<div style="border: 1px solid #A86A0B; background: #FDF8EF; border-radius: 7px; padding: 14px 16px;">'
          '<div style="display: flex; align-items: center; gap: 9px;">'
          '<span class="lbl" style="color: #A86A0B;">verifier menolak draf</span>'
          '<div style="margin-left: auto;"><div class="bar" style="width: 46px;"></div></div></div>'
          '<div class="txt" style="margin-top: 9px; line-height: 1.5;">'
          'Angka yang dikutip draf tidak ditemukan di dokumen sumber. Peringatan dibatalkan, '
          'bukan diperbaiki diam-diam.</div></div></div></div>')

stat = lambda lab, val, accent=False: (
    f'<div class="{"zf" if accent else "z"}" style="flex: 1; border-radius: 7px; padding: 14px 15px;'
    f'{" border-color: #A86A0B;" if accent else ""}">'
    f'<div class="lbl">{lab}</div>'
    f'<div class="mono" style="font-size: 21px; font-weight: 600; margin-top: 6px;'
    f'{" color: #A86A0B;" if accent else ""}">{val}</div></div>')

inner = f'''
<div style="border-bottom: 1px solid #C9CDD2; padding: 15px 24px; display: flex; align-items: center; gap: 12px;">
  <div class="z" style="width: 26px; height: 26px; border-radius: 5px;"></div>
  <span class="hd" style="font-size: 14px;">Jejak Audit Agent</span>
  <div style="margin-left: auto; display: flex; gap: 7px;">
    <div class="z" style="width: 96px; height: 26px; border-radius: 5px;"></div>
    <div style="width: 118px; height: 26px; border-radius: 5px; background: #59616B;"></div>
  </div>
</div>
<div style="flex: 1; display: flex; min-height: 0; background: #F6F7F8;">
  <div style="flex: 1; min-width: 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px;">
    <div>
      <div style="display: flex; align-items: center; gap: 9px; margin-bottom: 11px;">
        {marker(1)}<span class="lbl">ringkasan satu kali jalan</span></div>
      <div style="display: flex; gap: 13px;">
        {stat("durasi", "11,4 dtk")}{stat("langkah", "7")}{stat("ditolak", "1", True)}{stat("dokumen", "184")}
      </div>
    </div>
    <div class="z" style="border-radius: 7px; padding: 18px 20px;">
      <div style="display: flex; align-items: center; gap: 9px; margin-bottom: 15px;">
        {marker(2)}<span class="lbl">urutan langkah</span></div>
      {STEPS}{REJECT}
    </div>
  </div>

  <div style="width: 356px; flex: none; border-left: 1px solid #C9CDD2; background: #FFFFFF; padding: 20px 18px; display: flex; flex-direction: column; gap: 15px;">
    <div style="border: 1px solid #A86A0B; background: #FDF8EF; border-radius: 7px; padding: 15px 16px;">
      <div style="display: flex; align-items: flex-start; gap: 10px;">
        {marker(3)}
        <div class="txt" style="line-height: 1.5;">Langkah penolakan ini adalah bukti paling langsung untuk kriteria <strong>Safety, Controllability &amp; Governance</strong>. Sistem yang tidak pernah menolak apa pun tidak punya bukti untuk ditunjukkan.</div>
      </div>
    </div>
    <div class="z" style="border-radius: 7px; padding: 15px 16px;">
      <div style="display: flex; align-items: center; gap: 9px;">{marker(4)}<span class="lbl">ekspor</span></div>
      <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 10px;">
        <div class="zd" style="padding: 10px 12px;"><span class="txt">Unduh jejak sebagai berkas</span></div>
        <div class="zd" style="padding: 10px 12px;"><span class="txt">Salin tautan ke run ini</span></div>
      </div>
    </div>
    <div class="zd" style="margin-top: auto; border-radius: 7px; padding: 13px 14px;">{bar("90%")}{bar("64%", "bar", 6)}</div>
  </div>
</div>
''' + legend([
 (1, "Ringkasan run ditampilkan sebagai angka, termasuk jumlah penolakan. Angka nol di sana justru mencurigakan."),
 (2, "Urutan langkah dengan timestamp. Appendix 2 mewajibkan operation trace — kita menampilkannya sebagai layar produk, bukan lampiran dokumen terpisah."),
 (3, "Satu langkah di mana verifier MENOLAK draf peringatan karena angkanya tidak ada di dokumen sumber. Ini elemen terpenting di seluruh wireframe."),
 (4, "Jejak bisa diekspor dan ditautkan. Juri harus bisa memeriksanya setelah demo selesai, bukan hanya saat kita menunjukkannya."),
])
write("JejakAudit", 1440, 900, inner)

# ==================================================== 7 · NOTIFIKASI PONSEL
inner = f'''
<div style="flex: 1; background: #EDEFF1; padding: 52px 12px 12px; display: flex; flex-direction: column; gap: 15px; min-height: 0;">

  <div class="z" style="border-radius: 13px; padding: 13px 14px; display: flex; flex-direction: column; gap: 8px;">
    <div style="display: flex; align-items: center; gap: 8px;">
      {marker(1)}
      <div class="bard" style="width: 62px;"></div>
      <div style="margin-left: auto;"><div class="bar" style="width: 36px;"></div></div>
    </div>
    <div class="bard" style="width: 78%;"></div>
    {bar("94%")}{bar("66%")}
  </div>

  <div class="z" style="flex: 1; border-radius: 13px; padding: 16px 15px; display: flex; flex-direction: column; gap: 14px; min-height: 0;">
    <div style="display: flex; align-items: center; gap: 8px;">
      <span class="mono" style="font-size: 12px; font-weight: 600;">2881</span>
      <div class="bard" style="width: 54px;"></div>
      <div class="zf" style="padding: 2px 6px; border-radius: 3px;"><span class="lbl">第 24 款</span></div>
    </div>
    <div>{bar("96%", "bard")}{bar("72%", "bard", 6)}</div>

    <div class="zf" style="border-radius: 8px; padding: 13px; display: flex; align-items: center; gap: 11px;">
      {marker(2)}
      <div style="flex: 1;"><div class="lbl">sebelum</div>
        <div class="mono" style="font-size: 17px; font-weight: 600; color: #7A828C; margin-top: 3px;">92,4</div></div>
      <span class="mono" style="color: #7A828C;">&#8594;</span>
      <div style="flex: 1;"><div class="lbl">sekarang</div>
        <div class="mono" style="font-size: 17px; font-weight: 600; margin-top: 3px;">88,1</div></div>
    </div>

    <div>
      <div style="display: flex; align-items: center; gap: 8px;">{marker(3)}<span class="lbl">kenapa berubah</span></div>
      <div style="margin-top: 9px;">{bar("92%")}{bar("58%", "bar", 6)}</div>
    </div>

    <div class="zd" style="border-radius: 8px; padding: 10px 12px;"><span class="lbl">buka dokumen MOPS</span></div>

    <div style="margin-top: auto; display: flex; flex-direction: column; gap: 9px;">
      <div style="display: flex; align-items: center; gap: 8px;">{marker(4)}<span class="lbl">peringatan ini berguna?</span></div>
      <div style="display: flex; gap: 9px;">
        <div class="z" style="flex: 1; height: 46px; border-radius: 9px;"></div>
        <div class="z" style="flex: 1; height: 46px; border-radius: 9px;"></div>
      </div>
      <div style="height: 46px; border-radius: 9px; background: #59616B;"></div>
    </div>
  </div>
</div>
''' + legend([
 (1, "Push menyatakan bahwa kesimpulan BERUBAH, bukan bahwa ada berita baru. Notifikasi yang tidak menyebut perubahan akan diabaikan setelah minggu pertama."),
 (2, "Angka sebelum→sesudah ada di notifikasi, bukan cuma di aplikasi. Pengguna harus bisa memutuskan tanpa membuka apa pun."),
 (3, "Satu baris alasan. Kalau tidak muat satu baris, berarti kita belum paham sendiri penyebabnya."),
 (4, "Tombol Ya/Tidak adalah umpan balik perilaku — tahap ketiga dari empat tahap yang diminta panitia. Ruang atas sengaja dibiarkan kosong: status bar asli ponsel yang mengisinya, jangan digambar palsu."),
], cols=1)
write("NotifPonsel", 390, 1080, inner)
