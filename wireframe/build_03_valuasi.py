import io
exec(io.open("build_common.py", encoding="utf-8").read())

def bar(w, cls="bar", mt=0):
    return f'<div class="{cls}" style="width: {w}; margin-top: {mt}px;"></div>'

topbar = lambda t, extra="": f'''
  <div style="border-bottom: 1px solid #C9CDD2; padding: 15px 24px; display: flex; align-items: center; gap: 12px;">
    <div class="z" style="width: 26px; height: 26px; border-radius: 5px;"></div>
    <span class="mono" style="font-size: 13px; font-weight: 600;">{t}</span>
    <div class="bard" style="width: 104px;"></div>{extra}
    <div style="margin-left: auto; display: flex; gap: 7px;">
      <div class="z" style="width: 96px; height: 26px; border-radius: 5px;"></div>
      <div style="width: 118px; height: 26px; border-radius: 5px; background: #59616B;"></div>
    </div>
  </div>'''

# ============================================================ 3 · VALUASI
def cell(hl=False):
    bg = "#EDE2CE" if hl else "#F3F4F6"
    return f'<td style="border: 1px solid #C9CDD2; background: {bg}; padding: 9px 0; text-align: center;"><div class="bar" style="width: 46px; margin: 0 auto;"></div></td>'

rows = "".join(
    '<tr><td style="border: 1px solid #C9CDD2; background: #FFFFFF; padding: 9px 12px;">'
    '<div class="bard" style="width: 54px;"></div></td>'
    + "".join(cell(hl=(r == 2 and c == 2)) for c in range(5)) + "</tr>"
    for r in range(5))

tile = lambda lab, val, accent=False: f'''
  <div class="{'z' if not accent else 'zf'}" style="flex: 1; border-radius: 7px; padding: 15px 16px;
       {'border-color: #A86A0B;' if accent else ''}">
    <div class="lbl">{lab}</div>
    <div class="mono" style="font-size: 26px; font-weight: 600; margin-top: 7px; {'color: #A86A0B;' if accent else ''}">{val}</div>
    <div style="margin-top: 9px;">{bar("72%")}</div>
  </div>'''

SLIDER_T = ('<div class="zf" style="border-radius: 7px; padding: 13px 14px;">'
  '<div style="display: flex; align-items: center; gap: 10px;">'
  '<div class="bar" style="flex: 1;"></div><div class="bard" style="width: 44px;"></div></div>'
  '<div style="margin-top: 11px; height: 4px; background: #C9CDD2; border-radius: 2px; position: relative;">'
  '<div style="position: absolute; left: %d%%; top: -5px; width: 14px; height: 14px; '
  'border-radius: 50%%; background: #59616B;"></div></div></div>')
SLIDERS = "".join(SLIDER_T % p for p in (38, 62, 47))

inner = topbar("2330") + f'''
<div style="flex: 1; display: flex; min-height: 0; background: #F6F7F8;">
  <div style="flex: 1; min-width: 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px;">

    <div class="z" style="border-radius: 7px; padding: 19px 21px;">
      <div style="display: flex; align-items: flex-start; gap: 10px;">
        {marker(1)}
        <div style="flex: 1;">
          <div class="hd" style="font-size: 19px; line-height: 1.35;">Pasar mengasumsikan pertumbuhan abadi 6,29% &#8212; di atas batas wajar 3,5%</div>
          <div class="txt" style="margin-top: 9px;">Kesimpulan ditulis sebagai kalimat. Angka telanjang tidak memberi tahu juri apa artinya.</div>
        </div>
      </div>
    </div>

    <div>
      <div style="display: flex; align-items: center; gap: 9px; margin-bottom: 11px;">
        {marker(2)}<span class="lbl">satu hasil hitungan kita, dua pembanding</span>
      </div>
      <div style="display: flex; gap: 14px;">
        {tile("g tersirat", "6,29%", True)}{tile("batas wajar", "3,50%")}{tile("rasio", "1,79&#215;")}
      </div>
    </div>

    <div class="z" style="border-radius: 7px; padding: 17px 19px;">
      <div style="display: flex; align-items: center; gap: 9px;">
        {marker(3)}<span class="lbl">sensitivitas &#8212; WACC &#215; g</span>
        <span class="lbl" style="margin-left: auto; color: #A86A0B;">juri menggeser di sini saat demo</span>
      </div>
      <table style="width: 100%; border-collapse: collapse; margin-top: 14px;">
        <tr><td style="padding: 0 0 8px;"></td>
          {"".join('<td style="padding: 0 0 8px; text-align: center;"><div class="lbl">g</div></td>' for _ in range(5))}</tr>
        {rows}
      </table>
    </div>
  </div>

  <div style="width: 352px; flex: none; border-left: 1px solid #C9CDD2; background: #FFFFFF; padding: 20px 18px; display: flex; flex-direction: column; gap: 15px;">
    <div style="display: flex; align-items: center; gap: 9px;">{marker(5)}<span class="lbl">asumsi &#8212; bisa digeser</span></div>
    {SLIDERS}

    <div class="z" style="border-radius: 7px; padding: 14px 15px;">
      <div style="display: flex; align-items: center; gap: 9px;">{marker(4)}<span class="lbl">sumber tiap angka</span></div>
      <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 10px;">
        {"".join('<div style="display: flex; gap: 9px; align-items: center;"><div class="bar" style="flex: 1;"></div><div class="zd" style="padding: 3px 7px;"><span class="lbl">tautan</span></div></div>' for _ in range(4))}
      </div>
    </div>
    <div class="zd" style="margin-top: auto; border-radius: 7px; padding: 13px 14px;">{bar("92%")}{bar("58%", "bar", 6)}</div>
  </div>
</div>
''' + legend([
 (1, "Kesimpulan ditulis sebagai kalimat yang bisa dibantah, bukan angka telanjang. “6,29%” tidak berarti apa-apa sampai dibandingkan dengan sesuatu."),
 (2, "Tiga ubin: g tersirat, batas wajar, dan rasio antara keduanya. Cuma yang pertama hasil hitungan kita — dua lainnya pembanding."),
 (3, "Tabel sensitivitas adalah momen demo. Juri menggeser WACC atau g, seluruh tabel bergerak di depan mereka. Satu gerakan ini menjawab “apakah angkanya bisa diverifikasi” lebih baik dari penjelasan apa pun."),
 (4, "Tiap asumsi punya tautan ke sumbernya. Angka tanpa sumber adalah tebakan yang diketik rapi."),
 (5, "Slider ada supaya juri bisa menguji asumsi kita, bukan supaya tampilannya interaktif. Kalau tidak ada yang berubah saat digeser, hapus saja."),
])
write("Valuasi", 1440, 820, inner)

# ================================================= 3b · RIWAYAT NILAI WAJAR
EVENT_T = ('<div class="z" style="border-radius: 7px; padding: 13px 14px;">'
  '<div style="display: flex; align-items: center; gap: 9px;">'
  '<span class="mono" style="font-size: 11px; color: #A86A0B; font-weight: 600;">@N@</span>'
  '<div class="bard" style="width: 68px;"></div>'
  '<div style="margin-left: auto;"><div class="bar" style="width: 44px;"></div></div></div>'
  '<div style="margin-top: 10px;">' + bar("88%") + bar("56%", "bar", 6) + '</div>'
  '<div class="zd" style="margin-top: 10px; padding: 5px 9px; display: inline-block;">'
  '<span class="lbl">dokumen MOPS</span></div></div>')
EVENTS = "".join(EVENT_T.replace("@N@", str(i)) for i in (1, 2, 3))

inner = topbar("2330") + f'''
<div style="flex: 1; display: flex; min-height: 0; background: #F6F7F8;">
  <div style="flex: 1; min-width: 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px;">
    <div class="z" style="flex: 1; border-radius: 7px; padding: 19px 21px; display: flex; flex-direction: column; min-height: 0;">
      <div style="display: flex; align-items: center; gap: 9px;">
        {marker(1)}<span class="lbl">nilai wajar terhadap harga pasar</span>
      </div>
      <div style="flex: 1; margin-top: 16px; position: relative; min-height: 0;">
        <svg viewBox="0 0 900 330" style="width: 100%; height: 100%;">
          <line x1="40" y1="290" x2="880" y2="290" stroke="#C9CDD2" stroke-width="1"/>
          <line x1="40" y1="20" x2="40" y2="290" stroke="#C9CDD2" stroke-width="1"/>
          <path d="M40 250 L180 190 L320 215 L460 150 L600 110 L740 75 L880 55" fill="none" stroke="#8A929C" stroke-width="2.5"/>
          <path d="M40 235 L250 235 L250 175 L620 175 L620 130 L880 130" fill="none" stroke="#A86A0B" stroke-width="2.5"/>
          <circle cx="250" cy="175" r="6" fill="#A86A0B"/>
          <circle cx="620" cy="130" r="6" fill="#A86A0B"/>
          <circle cx="880" cy="130" r="6" fill="#A86A0B"/>
          <line x1="530" y1="20" x2="530" y2="290" stroke="#AEB4BB" stroke-width="1" stroke-dasharray="4 4"/>
          <circle cx="530" cy="139" r="7" fill="#FFFFFF" stroke="#59616B" stroke-width="2"/>
        </svg>
        <div style="position: absolute; left: 28%; top: 62%; display: flex; gap: 7px; align-items: center;">{marker(2)}</div>
        <div style="position: absolute; left: 56%; top: 8%; display: flex; gap: 7px; align-items: center;">{marker(3)}
          <span class="lbl">harga menyalip nilai wajar</span></div>
      </div>
      <div class="zd" style="margin-top: 14px; padding: 11px 14px;">
        <span class="txt">Tidak ada candlestick, tidak ada indikator teknikal &#8212; keduanya tidak bisa disitasi ke dokumen mana pun.</span>
      </div>
    </div>
  </div>

  <div style="width: 352px; flex: none; border-left: 1px solid #C9CDD2; background: #FFFFFF; padding: 20px 18px; display: flex; flex-direction: column; gap: 15px;">
    <div style="display: flex; align-items: center; gap: 9px;">{marker(4)}<span class="lbl">peristiwa perhitungan ulang</span></div>
    {EVENTS}
    <div class="zf" style="margin-top: auto; border-radius: 7px; padding: 14px 15px;">
      <div class="lbl">selisih terhadap harga</div>
      <div class="mono" style="font-size: 22px; font-weight: 600; margin-top: 7px;">+3,7%</div>
    </div>
  </div>
</div>
''' + legend([
 (1, "Dua garis saja. Menambah garis ketiga berarti ada yang tidak bisa dijelaskan dalam satu kalimat."),
 (2, "Garis nilai wajar berbentuk anak tangga karena memang hanya dihitung ulang saat ada dokumen baru — bukan karena gayanya begitu. Kurva mulus akan berbohong soal cara kerjanya."),
 (3, "Titik perpotongan diberi tanggal. Ini satu-satunya momen di grafik yang punya arti keputusan: harga menyalip nilai wajar."),
 (4, "Tiap anak tangga menunjuk ke dokumen yang memicunya. Grafik yang titik-titiknya bisa diklik ke sumber adalah hal yang tidak dimiliki aplikasi sekuritas mana pun."),
])
write("RiwayatNilaiWajar", 1440, 900, inner)
