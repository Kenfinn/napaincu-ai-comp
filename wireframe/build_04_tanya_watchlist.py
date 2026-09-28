import io
exec(io.open("build_common.py", encoding="utf-8").read())

def bar(w, cls="bar", mt=0):
    return f'<div class="{cls}" style="width: {w}; margin-top: {mt}px;"></div>'

topbar = lambda t: f'''
  <div style="border-bottom: 1px solid #C9CDD2; padding: 15px 24px; display: flex; align-items: center; gap: 12px;">
    <div class="z" style="width: 26px; height: 26px; border-radius: 5px;"></div>
    <span class="hd" style="font-size: 14px;">{t}</span>
    <div style="margin-left: auto; display: flex; gap: 7px;">
      <div class="z" style="width: 96px; height: 26px; border-radius: 5px;"></div>
      <div style="width: 118px; height: 26px; border-radius: 5px; background: #59616B;"></div>
    </div>
  </div>'''

# ====================================================== 4 · TANYA JAWAB
ASK = ('<div style="display: flex; justify-content: flex-end;">'
       '<div style="max-width: 58%; background: #59616B; border-radius: 9px; padding: 13px 15px;">'
       '<div style="height: 9px; background: #939AA2; border-radius: 2px; width: 210px;"></div>'
       '<div style="height: 9px; background: #939AA2; border-radius: 2px; width: 140px; margin-top: 6px;"></div>'
       '</div></div>')

ANSWER = ('<div class="z" style="border-radius: 9px; padding: 15px 17px;">'
          + bar("94%", "bard") + bar("88%", "bar", 7) + bar("61%", "bar", 7)
          + '<div style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">'
          + '<div class="zd" style="padding: 5px 9px;"><span class="lbl">sitasi 1</span></div>'
          + '<div class="zd" style="padding: 5px 9px;"><span class="lbl">sitasi 2</span></div>'
          + '</div></div>')

inner = topbar("Tanya Jawab") + f'''
<div style="flex: 1; display: flex; min-height: 0; background: #F6F7F8;">
  <div style="flex: 1; min-width: 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px;">

    <div style="display: flex; align-items: center; gap: 9px;">{marker(2)}<span class="lbl">jawaban selalu membawa sitasi</span></div>
    {ASK}{ANSWER}{ASK}

    <div style="border: 1px solid #A86A0B; background: #FDF8EF; border-radius: 9px; padding: 15px 17px;">
      <div style="display: flex; align-items: flex-start; gap: 10px;">
        {marker(3)}
        <div style="flex: 1;">
          <div class="lbl" style="color: #A86A0B;">agen menolak menjawab</div>
          <div class="txt" style="margin-top: 8px; line-height: 1.5;">
            &#8220;Berapa harga 2330 bulan depan?&#8221; &#8212; di luar kemampuan sistem.
            Kami menghitung nilai wajar dari dokumen, bukan meramalkan harga.</div>
        </div>
      </div>
    </div>

    <div class="z" style="margin-top: auto; border-radius: 9px; padding: 14px 16px; display: flex; align-items: center; gap: 12px;">
      {marker(1)}
      <div class="bar" style="flex: 1;"></div>
      <div style="width: 36px; height: 30px; border-radius: 6px; background: #59616B;"></div>
    </div>
  </div>

  <div style="width: 336px; flex: none; border-left: 1px solid #C9CDD2; background: #FFFFFF; padding: 20px 18px; display: flex; flex-direction: column; gap: 14px;">
    <div style="display: flex; align-items: center; gap: 9px;">{marker(4)}<span class="lbl">pertanyaan contoh</span></div>
    {"".join('<div class="zd" style="border-radius: 7px; padding: 12px 13px;">' + bar("86%") + bar("58%", "bar", 6) + '</div>' for _ in range(4))}
    <div class="zf" style="margin-top: auto; border-radius: 7px; padding: 13px 14px;">
      <div class="lbl">yang tidak bisa dijawab</div>
      <div style="margin-top: 10px;">{bar("90%")}{bar("70%", "bar", 6)}</div>
    </div>
  </div>
</div>
''' + legend([
 (1, "Kotak input di bawah adalah alasan layar ini ada: juri mengetik test case mereka sendiri. Tim lain sering lupa menyediakannya dan hanya menyiapkan demo terpandu."),
 (2, "Tiap jawaban membawa sitasi ke dokumen. Jawaban tanpa sitasi tidak boleh keluar, meskipun benar."),
 (3, "Contoh pertanyaan yang agen MENOLAK jawab ditampilkan, tidak disembunyikan. Menunjukkan batas kemampuan lebih meyakinkan daripada berpura-pura bisa segalanya."),
 (4, "Pertanyaan contoh ada untuk memulai, bukan untuk mengarahkan. Juri tetap harus bisa mengetik apa pun."),
])
write("TanyaJawab", 1440, 860, inner)

# ======================================================== 5 · WATCHLIST
ROW = ('<div class="z" style="border-radius: 7px; padding: 13px 16px; display: flex; align-items: center; gap: 13px;">'
       '<span class="mono" style="font-size: 13px; font-weight: 600;">@T@</span>'
       '<div class="bard" style="width: 96px;"></div>'
       '<div class="bar" style="flex: 1;"></div>'
       '<div class="bard" style="width: 52px;"></div>'
       '<div class="bar" style="width: 44px;"></div></div>')
ROWS = "".join(ROW.replace("@T@", t) for t in ("2330", "2317", "2881", "1301"))

TOGGLE = ('<div style="display: flex; align-items: center; gap: 11px;">'
          '<div class="bar" style="flex: 1;"></div>'
          '<div style="width: 34px; height: 19px; border-radius: 10px; background: @BG@; flex: none;"></div></div>')
TOGGLES = "".join(TOGGLE.replace("@BG@", c) for c in ("#59616B", "#59616B", "#D7DBDF"))

inner = topbar("Watchlist &amp; Profil Risiko") + f'''
<div style="flex: 1; display: flex; min-height: 0; background: #F6F7F8;">
  <div style="flex: 1; min-width: 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 12px;">
    <div style="display: flex; align-items: center; gap: 9px;">{marker(1)}<span class="lbl">emiten yang dipantau</span></div>
    {ROWS}
    <div class="zd" style="border-radius: 7px; padding: 13px 16px; display: flex; align-items: center; justify-content: center;">
      <span class="txt">+ tambah emiten</span>
    </div>
  </div>

  <div style="width: 392px; flex: none; border-left: 1px solid #C9CDD2; background: #FFFFFF; padding: 20px 18px; display: flex; flex-direction: column; gap: 16px;">
    <div class="zf" style="border-radius: 7px; padding: 15px 16px;">
      <div style="display: flex; align-items: center; gap: 9px;">{marker(2)}<span class="lbl">profil risiko</span></div>
      <div style="margin-top: 13px; display: flex; flex-direction: column; gap: 11px;">
        {"".join('<div class="z" style="border-radius: 6px; padding: 11px 12px; display: flex; align-items: center; gap: 10px;"><div style="width: 13px; height: 13px; border-radius: 50%; border: 1px solid #AEB4BB; flex: none;"></div>' + bar("70%") + '</div>' for _ in range(3))}
      </div>
      <div class="txt" style="margin-top: 13px; line-height: 1.5;">Profil ini yang menentukan ambang relevansi &#8212; bukan preferensi tampilan.</div>
    </div>

    <div class="z" style="border-radius: 7px; padding: 15px 16px;">
      <div style="display: flex; align-items: center; gap: 9px;">{marker(3)}<span class="lbl">saluran pengiriman</span></div>
      <div style="margin-top: 13px; display: flex; flex-direction: column; gap: 12px;">{TOGGLES}</div>
    </div>

    <div style="border: 1px solid #A86A0B; background: #FDF8EF; border-radius: 7px; padding: 15px 16px;">
      <div style="display: flex; align-items: flex-start; gap: 10px;">
        {marker(4)}
        <div class="txt" style="line-height: 1.5;">Ambang naik otomatis setelah tiga peringatan berturut-turut diabaikan. Sistem belajar dari perilaku, tanpa perlu diatur manual.</div>
      </div>
    </div>
    <div class="zd" style="margin-top: auto; border-radius: 7px; padding: 13px 14px;">{bar("88%")}{bar("62%", "bar", 6)}</div>
  </div>
</div>
''' + legend([
 (1, "Daftar emiten sengaja pendek. Agen yang memantau 20 emiten dengan alasan jelas lebih meyakinkan daripada yang mengklaim memantau seluruh bursa."),
 (2, "Profil risiko bukan pengaturan tampilan — ini yang menentukan pengumuman mana yang lolos jadi peringatan. Karena itu letaknya di layar utama, bukan di halaman Pengaturan."),
 (3, "Saluran pengiriman menentukan apakah sistem ini proaktif atau cuma dashboard. Panitia meminta pengiriman proaktif sebagai tahap kedua dari empat."),
 (4, "Ambang berubah sendiri dari perilaku pengguna. Ini tahap ketiga: sistem yang belajar, bukan sekadar menjalankan aturan tetap."),
])
write("Watchlist", 1440, 780, inner)
