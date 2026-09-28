exec(io.open("build_common.py").read()) if False else None
import io
exec(io.open("build_common.py", encoding="utf-8").read())

def bar(w, cls="bar", mt=0):
    return f'<div class="{cls}" style="width: {w}; margin-top: {mt}px;"></div>'

# ---------------------------------------------------------------- 1 · FEED
rail_item = lambda t, on=False: (
    f'<div style="display: flex; align-items: center; gap: 10px; padding: 9px 12px; '
    f'border-radius: 5px; background: {"#E4E7EA" if on else "transparent"};">'
    f'<div style="width: 14px; height: 14px; border: 1px solid #AEB4BB; border-radius: 3px; flex: none;"></div>'
    f'<span class="txt" style="font-weight: {600 if on else 400};">{t}</span></div>')

def alert_card(ticker, delta):
    body = f'''
      <div style="display: flex; align-items: center; gap: 9px;">
        <span class="mono" style="font-size: 13px; font-weight: 600;">{ticker}</span>
        <div class="bard" style="width: 96px;"></div>
        <div class="zf" style="padding: 2px 8px; border-radius: 3px;"><span class="lbl">符合條款 · jenis</span></div>
        <div style="margin-left: auto;"><div class="bar" style="width: 74px;"></div></div>
      </div>
      <div style="margin-top: 11px;">{bar("74%", "bard")}{bar("52%", "bard", 7)}</div>
      <div class="zf" style="margin-top: 13px; padding: 12px 14px; display: flex; gap: 16px; align-items: center;">
        {marker(4)}
        <div style="flex: none;"><div class="lbl">nilai wajar</div>
          <div class="mono" style="font-size: 15px; font-weight: 600; margin-top: 4px;">{delta}</div></div>
        <div style="width: 1px; height: 30px; background: #C9CDD2;"></div>
        <div style="flex: 1;">{bar("88%")}{bar("61%", "bar", 6)}</div>
      </div>
      <div style="margin-top: 13px; display: flex; align-items: center; gap: 10px;">
        {marker(5)}
        <div class="zd" style="flex: 1; padding: 7px 10px;"><span class="lbl">tautan &#8594; dokumen MOPS asli</span></div>
        <div class="z" style="width: 84px; height: 30px; border-radius: 5px;"></div>
        <div class="z" style="width: 84px; height: 30px; border-radius: 5px;"></div>
        <div style="width: 108px; height: 30px; border-radius: 5px; background: #59616B;"></div>
      </div>'''
    return f'<div class="z" style="border-radius: 7px; padding: 15px 17px;">{body}</div>'

inner = f'''
<div style="flex: 1; display: flex; min-height: 0;">

  <!-- RAIL KIRI -->
  <div style="width: 218px; flex: none; background: #EDEFF1; border-right: 1px solid #C9CDD2; padding: 18px 13px; display: flex; flex-direction: column; gap: 7px;">
    <div style="display: flex; align-items: center; gap: 9px; padding: 0 12px 16px;">
      <div style="width: 20px; height: 20px; border: 1px solid #AEB4BB; border-radius: 4px;"></div>
      <div class="bard" style="width: 72px;"></div>
      <div style="margin-left: auto;">{marker(1)}</div>
    </div>
    {rail_item("Peringatan", True)}
    {rail_item("Watchlist")}
    {rail_item("Tanya Jawab")}
    {rail_item("Jejak Audit")}
    <div style="margin-top: auto;" class="zd">
      <div style="padding: 11px 12px;"><div class="lbl">status pemantauan</div>
      <div style="margin-top: 7px;">{bar("80%")}{bar("58%", "bar", 5)}</div></div>
    </div>
  </div>

  <!-- KOLOM UTAMA -->
  <div style="flex: 1; min-width: 0; display: flex; flex-direction: column;">
    <div style="border-bottom: 1px solid #C9CDD2; padding: 17px 24px; display: flex; align-items: center; gap: 14px;">
      <div style="flex: 1;">
        <div class="hd">Peringatan hari ini</div>
        <div style="display: flex; align-items: center; gap: 9px; margin-top: 7px;">
          {marker(2)}
          <span class="txt">Dari 26 pengumuman, 4 dinilai mengubah kesimpulan valuasi</span>
        </div>
      </div>
      <div style="display: flex; gap: 7px;">
        <div style="width: 78px; height: 28px; border-radius: 5px; background: #59616B;"></div>
        <div class="z" style="width: 92px; height: 28px; border-radius: 5px;"></div>
        <div class="z" style="width: 78px; height: 28px; border-radius: 5px;"></div>
      </div>
    </div>

    <div style="flex: 1; padding: 18px 24px; display: flex; flex-direction: column; gap: 13px; background: #F6F7F8; min-height: 0;">
      <div style="display: flex; align-items: flex-start; gap: 9px;">
        {marker(3)}
        <span class="lbl" style="padding-top: 3px;">mengubah kesimpulan &#8212; kartu penuh</span>
      </div>
      {alert_card("2330", "2.302 &#8594; 2.294")}
      {alert_card("2881", "92,4 &#8594; 88,1")}

      <div class="lbl" style="margin-top: 4px;">tidak mengubah kesimpulan &#8212; baris ringkas</div>
      <div class="z" style="border-radius: 7px; padding: 13px 17px; display: flex; align-items: center; gap: 12px;">
        <span class="mono" style="font-size: 13px; font-weight: 600;">2317</span>
        <div class="bard" style="width: 82px;"></div><div class="bar" style="width: 250px;"></div>
        <div style="margin-left: auto;"><div class="bar" style="width: 54px;"></div></div>
      </div>
      <div class="z" style="border-radius: 7px; padding: 13px 17px; display: flex; align-items: center; gap: 12px;">
        <span class="mono" style="font-size: 13px; font-weight: 600;">1301</span>
        <div class="bard" style="width: 82px;"></div><div class="bar" style="width: 210px;"></div>
        <div style="margin-left: auto;"><div class="bar" style="width: 54px;"></div></div>
      </div>

      <div class="zd" style="margin-top: 4px; padding: 15px; display: flex; align-items: center; justify-content: center; gap: 10px; border-radius: 7px;">
        {marker(6)}
        <span class="txt">22 pengumuman lain dinilai tidak relevan &#8212; <strong>lihat alasannya</strong></span>
      </div>
    </div>
  </div>

  <!-- RAIL KANAN -->
  <div style="width: 298px; flex: none; border-left: 1px solid #C9CDD2; padding: 18px 16px; display: flex; flex-direction: column; gap: 14px; background: #FAFBFB;">
    <div class="z" style="border-radius: 7px; padding: 13px 14px;">
      <div class="lbl">ringkasan watchlist</div>
      <div style="margin-top: 11px; display: flex; flex-direction: column; gap: 9px;">
        {"".join(f'<div style="display: flex; align-items: center; gap: 10px;"><span class="mono" style="font-size: 12px;">{t}</span><div class="bar" style="flex: 1;"></div><div class="bar" style="width: 42px;"></div></div>' for t in ("2330","2317","2881","1301"))}
      </div>
    </div>
    <div class="z" style="border-radius: 7px; padding: 13px 14px;">
      <div style="display: flex; align-items: center; gap: 8px;">{marker(7)}<span class="lbl">kinerja agen &#183; 7 hari</span></div>
      <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 10px;">
        {"".join(f'<div style="display: flex; align-items: center; gap: 10px;"><div class="bar" style="flex: 1;"></div><div class="bard" style="width: 30px;"></div></div>' for _ in range(3))}
        <div style="display: flex; align-items: center; gap: 10px; padding-top: 9px; border-top: 1px solid #E4E7EA;">
          <span class="txt" style="flex: 1;">ditolak verifier angka</span>
          <span class="mono" style="font-size: 13px; font-weight: 600; color: #A86A0B;">2</span>
        </div>
      </div>
    </div>
    <div class="zd" style="border-radius: 7px; padding: 12px 13px;">{bar("94%")}{bar("88%", "bar", 6)}{bar("46%", "bar", 6)}</div>
  </div>
</div>
''' + legend([
 (1, "Empat destinasi, tidak lebih. Tiap destinasi memetakan satu kriteria penilaian lomba — tidak ada halaman yang ada cuma karena aplikasi biasanya punya."),
 (2, "Judul menyatakan hasil penyaringan, bukan jumlah mentah. “Dari 26 → 4” adalah klaim bahwa agen membuang; itu yang membedakannya dari feed berita."),
 (3, "Hanya pengumuman yang mengubah kesimpulan valuasi yang dapat kartu penuh. Sisanya jadi baris ringkas — hierarki ini keputusan produk, bukan gaya."),
 (4, "Delta nilai wajar wajib ada di kartu, bukan disembunyikan di detail. Tanpa angka sebelum→sesudah, ini cuma notifikasi."),
 (5, "Tautan sitasi ada di setiap kartu. Juri harus bisa sampai ke dokumen asli dalam satu klik, dari mana pun."),
 (6, "Blok “22 lain tidak relevan” beserta alasannya. Menampilkan yang dibuang sama pentingnya dengan menampilkan yang lolos."),
 (7, "Kinerja agen menampilkan “ditolak verifier” sebagai angka tersendiri. Menunjukkan kegagalan sendiri adalah bukti untuk kriteria Safety."),
])

write("Main", 1440, 1040, inner)
