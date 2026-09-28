import io
exec(io.open("build_common.py", encoding="utf-8").read())

def bar(w, cls="bar", mt=0):
    return f'<div class="{cls}" style="width: {w}; margin-top: {mt}px;"></div>'

topbar = lambda title: f'''
  <div style="border-bottom: 1px solid #C9CDD2; padding: 15px 24px; display: flex; align-items: center; gap: 12px;">
    <div class="z" style="width: 26px; height: 26px; border-radius: 5px;"></div>
    <span class="mono" style="font-size: 13px; font-weight: 600;">{title}</span>
    <div class="bard" style="width: 104px;"></div>
    <div style="margin-left: auto; display: flex; gap: 7px;">
      <div class="z" style="width: 96px; height: 26px; border-radius: 5px;"></div>
      <div style="width: 118px; height: 26px; border-radius: 5px; background: #59616B;"></div>
    </div>
  </div>'''

# ------------------------------------------------- 2 · DETAIL + SITASI
step = lambda n, wide: f'''
  <div style="display: flex; gap: 11px; align-items: flex-start;">
    <span class="mono" style="font-size: 11px; color: #7A828C; flex: none; padding-top: 2px;">{n}.</span>
    <div style="flex: 1;">{bar(wide, "bard")}{bar("62%", "bar", 6)}
      <div class="zd" style="margin-top: 8px; padding: 6px 9px; display: inline-block;">
        <span class="lbl">kutipan dokumen sumber</span></div>
    </div>
  </div>'''

inner = topbar("2881") + f'''
<div style="flex: 1; display: flex; min-height: 0; background: #F6F7F8;">
  <div style="flex: 1; min-width: 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 15px;">

    <div class="z" style="border-radius: 7px; padding: 17px 19px;">
      <div style="display: flex; align-items: center; gap: 9px;">
        {marker(1)}
        <div class="zf" style="padding: 2px 8px; border-radius: 3px;"><span class="lbl">符合條款 第 24 款</span></div>
        <span class="lbl">klasifikasi dari regulator, bukan dari model kita</span>
      </div>
      <div style="margin-top: 13px;">{bar("92%", "bard")}{bar("66%", "bard", 7)}</div>
    </div>

    <div class="z" style="border-radius: 7px; padding: 17px 19px; display: flex; flex-direction: column; gap: 15px;">
      <div style="display: flex; align-items: center; gap: 9px;">{marker(2)}<span class="lbl">langkah penalaran</span></div>
      {step(1, "88%")}{step(2, "79%")}{step(3, "84%")}{step(4, "71%")}
    </div>

    <div class="zd" style="margin-top: auto; border-radius: 7px; padding: 14px 17px; display: flex; align-items: center; gap: 11px;">
      {marker(5)}
      <span class="txt">Buka dokumen MOPS asli &#8212; URL lengkap terlihat, bisa disalin</span>
    </div>
  </div>

  <div style="width: 372px; flex: none; border-left: 1px solid #C9CDD2; background: #FFFFFF; padding: 20px 18px; display: flex; flex-direction: column; gap: 15px;">
    <div class="zf" style="border-radius: 7px; padding: 15px 16px;">
      <div style="display: flex; align-items: center; gap: 9px;">{marker(3)}<span class="lbl">dampak valuasi</span></div>
      <div style="margin-top: 14px; display: flex; align-items: center; gap: 13px;">
        <div style="flex: 1;"><div class="lbl">sebelum</div>
          <div class="mono" style="font-size: 19px; font-weight: 600; margin-top: 4px; color: #7A828C;">92,4</div></div>
        <span class="mono" style="color: #7A828C;">&#8594;</span>
        <div style="flex: 1;"><div class="lbl">sesudah</div>
          <div class="mono" style="font-size: 19px; font-weight: 600; margin-top: 4px;">88,1</div></div>
      </div>
      <div style="margin-top: 13px; padding-top: 12px; border-top: 1px solid #C9CDD2;">
        {bar("84%")}{bar("57%", "bar", 6)}</div>
    </div>

    <div class="z" style="border-radius: 7px; padding: 15px 16px;">
      <div class="lbl">asumsi yang ikut berubah</div>
      <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 11px;">
        {"".join(f'<div style="display: flex; gap: 10px; align-items: center;"><div class="bar" style="flex: 1;"></div><div class="bard" style="width: 46px;"></div></div>' for _ in range(3))}
      </div>
    </div>

    <div style="border: 1px solid #A86A0B; border-radius: 7px; padding: 15px 16px; background: #FDF8EF;">
      <div style="display: flex; align-items: flex-start; gap: 10px;">
        {marker(4)}
        <div><div class="lbl" style="color: #A86A0B;">data pribadi dibuang</div>
          <div class="txt" style="margin-top: 7px; line-height: 1.5;">Nama, jabatan, dan telepon juru bicara ada di halaman MOPS &#8212; tidak disimpan di sistem kami.</div>
          <div class="mono" style="font-size: 10.5px; color: #7A828C; margin-top: 8px;">Pasal 14.1</div></div>
      </div>
    </div>

    <div class="zd" style="margin-top: auto; border-radius: 7px; padding: 13px 14px;">{bar("90%")}{bar("64%", "bar", 6)}</div>
  </div>
</div>
''' + legend([
 (1, "Jenis peristiwa datang dari nomor pasal yang sudah ditetapkan regulator (符合條款). Kita tidak mengklasifikasikan sendiri — jadi tidak ada yang perlu dibela saat juri bertanya “akurasinya berapa?”."),
 (2, "Penalaran ditampilkan sebagai langkah bernomor, tiap langkah menunjuk kalimat di dokumen sumber. Ini yang membuat kesimpulan bisa diperiksa, bukan dipercaya."),
 (3, "Dampak valuasi pakai angka yang sama persis dengan kertas kerja. Kalau juri membuka spreadsheet, angkanya harus cocok."),
 (4, "Halaman MOPS memuat nama, jabatan, dan telepon juru bicara. Kita menyatakan di UI bahwa ketiganya dibuang — minimisasi data yang terlihat, bukan cuma tertulis di dokumen."),
 (5, "URL dokumen asli terlihat penuh dan bisa disalin. Juri tidak perlu percaya tautan yang disingkat."),
])

write("DetailPeringatan", 1440, 840, inner)
