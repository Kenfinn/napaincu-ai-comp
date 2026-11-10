# Draf pemetaan pasal 重大訊息 → aksi agent

**Status: DRAF, menunggu verifikasi Ferry & Patrice.** Disusun Claude, 10 Nov 2026.
Setelah disetujui, isinya dipindah ke `app/agent/screen.py` (`KLAUSA_RELEVAN`) dan label
butirnya ke `app/agent/extract.py` (`LABEL_SAH`).

## Kenapa perlu diubah

Daftar sekarang (11, 20, 22, 2) ditebak sebelum ada data asli. Data asli 9 Nov
(578 pengumuman TWSE + TPEx) menunjukkan:

1. **Pasal 31 (laporan keuangan kuartal) berjumlah 177 (31%) dan selama ini DILEWATI**,
   padahal paling relevan untuk valuasi.
2. **Pasal 11 bukan belanja modal.** Isinya penerbitan/konversi obligasi, pengurangan
   modal, dan pembatalan saham treasuri: yang berubah adalah **jumlah saham**.
3. **Pasal 22/23 (penjaminan/pinjaman dana ke pihak lain) bukan utang perusahaan**, jadi
   tidak tepat dipakai mengganti utang jangka panjang di DCF.
4. **Pasal 2 tidak muncul sama sekali.** Gagal bayar obligasi justru muncul di **pasal 1**.
5. **Label butir yang dicari pemeriksa tidak ada di pengumuman asli** (mis. `交易金額`).
   Label aslinya tercantum di kolom terakhir tabel bukti di bawah.
6. Penomoran TWSE dan TPEx sama untuk hampir semua pasal, **kecuali "lain-lain"**:
   TWSE pasal 51, TPEx pasal 53.

Dua perbaikan teknis sudah dikerjakan (tidak perlu diverifikasi): satuan seperti
`(仟元)` kini dibaca dari label, dan sub-butir `(1)(2)(3)…` diurai terpisah.

## Usulan

Empat jenis aksi:
- **Valuasi**: angka mengubah input DCF, dihitung ulang
- **Laporan**: laporan kuartal memicu pembaruan fundamental dan DCF (jalur baru, B2)
- **Sinyal risiko**: tidak mengubah DCF, tapi diterbitkan sebagai peringatan risiko
  dengan angkanya; yang berat langsung HELD untuk manusia
- **Dilewati**: diarsipkan dengan alasan, tidak sampai ke model

| Pasal | Isi (dari data asli) | Sekarang | **Usulan** | Input / aksi | Label butir yang dipakai |
|---|---|---|---|---|---|
| **31** | Laporan keuangan kuartal disetujui direksi | dilewati | **Laporan** | Pendapatan, laba usaha, laba bersih YTD, total aset/liabilitas/ekuitas → bandingkan dengan YTD tahun lalu, perbarui DCF | `1月1日累計至本期止營業收入(仟元)` dst., `期末總資產(仟元)`, `期末總負債(仟元)` |
| **20** | Perolehan/pelepasan aset (mesin, gedung, hak guna, produk investasi) | capex, cash | **Valuasi** | capex (aset tetap, hak guna) atau kas (produk investasi, pelepasan); model memilah | `交易單位數量、每單位價格及交易總金額` (teks bebas, perlu model) |
| **11** | Penerbitan/konversi obligasi, pengurangan modal, saham treasuri dibatalkan | capex ❌ | **Valuasi** | **Jumlah saham** (input baru), bukan capex | `全案發行總金額及股數`, `減資金額`, `發行總額` |
| **35** | Pembelian kembali saham | dilewati | **Valuasi** | Kas keluar + jumlah saham | `本次已買回股份總金額(元)` |
| **10** | Kontrak penting (mis. kredit sindikasi) | dilewati | **Valuasi** | Utang bila kontrak pinjaman; model memilah | (bervariasi, perlu model) |
| **22** | Penjaminan (背書保證) | debt ❌ | **Sinyal risiko** | Saldo penjaminan dan rasionya terhadap ekuitas | `迄事實發生日止背書保證餘額(仟元)`, `…占…淨值之比率` |
| **23** | Pinjaman dana ke pihak lain (資金貸與) | dilewati | **Sinyal risiko** | Saldo pinjaman dan rasionya terhadap ekuitas | `迄事實發生日止資金貸與餘額(仟元)`, `…占…淨值之比率` |
| **1** | Gagal bayar / obligasi jatuh tempo belum dibayar | dilewati | **Sinyal risiko, langsung HELD** | Jumlah yang gagal dibayar | `喪失債信之金額` |
| **3** | Penghentian produksi, PHK massal | dilewati | **Sinyal risiko, langsung HELD** | — | — |
| **40** | Penghentian perdagangan saham | dilewati | **Sinyal risiko, langsung HELD** | — | — |
| **28** | Klien/debitur bermasalah | dilewati | **Sinyal risiko** | Piutang/penjaminan terdampak | `債權種類或背書保證金額及其所占資產比例` |
| **26** | Insiden keamanan siber | dilewati | **Sinyal risiko** | — | — |
| **51 (TWSE) / 53 (TPEx)** | Lain-lain: klarifikasi media, koreksi angka, ganti nama, dsb. | dilewati | **Triase model** | Model memutuskan relevan atau tidak, dengan skor keyakinan | `更正前/後金額`, `近期營業收入及損益資訊` |
| 14 | Dividen | dilewati | Dilewati | Tidak mengubah arus kas bebas | — |
| 12 | Paparan investor | dilewati | Dilewati | — | — |
| 6, 7, 8 | Perubahan direksi, auditor, manajemen | dilewati | Dilewati | (kandidat sinyal tata kelola di versi berikutnya) | — |
| 16, 17, 18, 21, 36, 43, 44, 47, 52 | RUPS, izin non-kompetisi, donasi, keberatan direktur independen, dll. | dilewati | Dilewati | — | — |
| 2 | (tidak muncul di data) | debt, cash | **Hapus** | Dugaan awal "cek kosong" tidak terbukti | — |

## Pertanyaan untuk Ferry & Patrice

Jawab langsung di dokumen ini atau di chat tim. Cukup "setuju" atau koreksinya.

1. **Pasal 31:** setuju dijadikan pemicu pembaruan fundamental + DCF?
2. **Pasal 22/23:** setuju sebagai **sinyal risiko**, bukan input DCF? Mulai ambang
   berapa rasio saldo/ekuitas dianggap perlu peringatan? (usulan: ≥ 50%, sesuai batas
   yang memang memicu kewajiban lapor di regulasi)
3. **Pasal 11 dan 35:** setuju dampaknya ke **jumlah saham** (nilai wajar per lembar)?
4. **Pasal 1, 3, 40:** setuju selalu HELD untuk manusia?
5. **Pasal 51/53:** setuju diserahkan ke triase model, atau dilewati saja?
6. **Pasal 6/7/8 (tata kelola):** tetap dilewati untuk sekarang?
7. **Teks regulasi:** tolong cocokkan judul tiap pasal dengan teks resmi
   《對有價證券上市公司重大訊息之查證暨公開處理程序》 第4條 (TWSE) dan versi TPEx.
   Dokumen resmi tidak bisa diunduh dari luar Taiwan, jadi kolom "Isi" di atas disusun
   dari judul pengumuman asli.
8. **Pasal 20, angka transaksi tunggal** (mis. mesin 108 juta NTD): saat ini angka itu
   *mengganti* belanja modal setahun di DCF (cocok untuk anggaran capex direksi, tidak
   cocok untuk satu transaksi), sehingga hampir selalu ditahan pemeriksa besaran.
   Usulan: transaksi tunggal *ditambahkan* ke capex tahun berjalan. Setuju?
9. **Materialitas triase** (`app/agent/triase.py`): jumlah ÷ kapitalisasi pasar —
   ≥ 2% material, ≥ 0,5% cukup, ≥ 0,05% kecil, di bawahnya remeh (diarsipkan). Pada
   data 10 Nov, 7 dari 55 pengumuman pasal 20 jatuh ke "remeh" (sewa ruang beberapa
   juta NTD). Batas ini wajar menurut kalian?

## Bukti: statistik pengumuman asli 9 Nov

Dihasilkan `scripts/statistik_pasal.py`. Di server, skrip yang sama membaca seluruh
arsip sejak 8 Nov:

```bash
python3 scripts/statistik_pasal.py --contoh 3
```

Dari 578 pengumuman unik (2026-11-09 s.d. 2026-11-09), 2 berkas arsip.

| Pasal | TWSE | TPEx | Saringan sekarang | Contoh judul | Label butir berisi jumlah |
|---|---|---|---|---|---|
| 31 | 108 | 69 | dilewati | 公告本公司董事會通過115年度第三季合併財務報告 · 公告本公司115年第3季合併財務報告業經提報董事會 | 1月1日累計至本期止稅前淨利 (仟元) · 1月1日累計至本期止本期淨利 (仟元) · 1月1日累計至本期止歸屬於母公司業主淨利 (仟元) · 期末總資產 (仟元) |
| 20 | 42 | 13 | lolos → capex, cash | 代孫公司濟南聯合製罐有限公司公告取得理財商品 · 本公司向關係人取得使用權資產 | 交易相對人為關係人者，並應公告選定關係人為交易對象之 · 交易標的最近五年內所有權人曾為公司之關係人者，尚應公 · 估價報告是否為限定價格、特定價格或特殊價格 · 交易單位數量、每單位價格及交易總金額 |
| 12 | 31 | 20 | dilewati | 本公司受邀參加凱基證券舉辦之線上法人說明會 · 本公司受邀參加福邦證券舉辦線上法人說明會。 | — |
| 51 | 50 | 0 | dilewati | 公告本公司名稱由「世紀離岸風電設備股份有限公司」更名 為「世 · 澄清媒體報導 | 近期營業收入及損益資訊 · 歷史每月營業收入 · 更正前金額/內容/頁次 · 更正後金額/內容/頁次 |
| 53 | 0 | 31 | dilewati | 公告本公司名稱由「森寶開發股份有限公司」更名為 「長耀地產投 · 本公司骨質疏鬆症生物相似藥SPD8（Denosumab） 正 | 更正前金額/內容/頁次 · 更正後金額/內容/頁次 · 115/11/09期初餘額$1,966,696。 預 · 規劃貸與金額回收 |
| 8 | 19 | 10 | dilewati | 公告本公司會計主管異動 · 代重要子公司騰輝電子(蘇州)有限公司公告總經理異動 | — |
| 6 | 20 | 9 | dilewati | 公告本公司法人董事代表人逝世 · 代子公司信益陶瓷(中國)有限公司公告法人董事代表人逝世 | — |
| 11 | 19 | 10 | lolos → capex | 公告本公司董事會決議庫藏股註銷減資基準日 · 公告本公司國內第二次有擔保及第三次無擔保轉換 公司債115年 | 發行價格 · 全案發行總金額及股數 · 採總括申報發行新股案件，本次發行金額及股數 · 採總括申報發行新股案件，本次發行後，剩餘之金額及股數 |
| 23 | 15 | 10 | dilewati | 依公開發行公司資金貸與及背書保證處理準則第二十二條第一項 第 · 本公司對昶和纖維﹝紹興﹞有限公司資金貸與達「公開發行公司 資 | 資金貸與之限額 (仟元) · 迄事實發生日為止，資金貸與餘額 (仟元) · 迄事實發生日為止，資金貸與餘額占公開發行公司最近期財 · 原資金貸與之餘額 (仟元) |
| 14 | 14 | 11 | dilewati | 本公司之子公司EDISON OPTO USA CORPORA · 公告本公司董事會決議115年第三季盈餘分配發放現金 | 發放股利種類及金額 · 股利所屬年度 · 股利所屬期間 · 盈餘分配之現金股利 |
| 22 | 15 | 4 | lolos → debt | 本公司依「公開發行公司資金貸與及背書保證處理準則」第二十五  · 本公司代子公司騰輝電子股份有限公司 依「公開發行公 司資金貸 | 背書保證之限額 (仟元) · 原背書保證之餘額 (仟元) · 本次新增背書保證之金額 (仟元) · 被背書保證公司實際動支金額 (仟元) |
| 21 | 7 | 1 | dilewati | 代子公司申華化學工業有限公司公告解除 董事競業禁止之限制 · 代子公司台橡（南通）實業有限公司公告解除 董事競業禁止之限制 | 經理人如有對該大陸地區事業從事投資者，其投資金額及持 · 董事如有對該大陸地區事業從事投資者，其投資金額及持股 |
| 43 | 5 | 2 | dilewati | 代子公司「中國化學製藥股份有限公司」董事會通過對 財團法人王 · 代子公司「中國化學製藥股份有限公司」董事會通過 2027年「 | 捐贈金額 |
| 35 | 2 | 5 | dilewati | 本公司買回庫藏股執行完畢 · 公告本公司買回庫藏股期間屆滿執行情形(更正實際買回期間) | 本次平均每股買回價格 (元) · 原預定買回股份總金額上限 (元) · 原預定買回區間價格 (元) · 本次已買回股份總金額 (元) |
| 17 | 3 | 3 | dilewati | 代子公司台橡（南通）實業有限公司公告股東臨時會 召開事宜 · 公告本公司董事會決議召開115年第二次股東臨時會 | — |
| 18 | 5 | 0 | dilewati | 玉山金控代子公司三商美邦保險代理人股份有限公司公告 董事會代 · 代子公司申華化學工業有限公司公告股東臨時會 重要決議事宜 | — |
| 26 | 4 | 1 | dilewati | 公告本公司之子公司"好漾生活股份有限公司"之線上商店 委外服 · 公告子公司安永生活事業股份有限公司電商平台委外服務 商發生資 | 可能獲得保險理賠之金額 |
| 10 | 2 | 2 | dilewati | 公告本公司董事會決議通過與聯貸銀行團簽訂聯合授信 合約 · 代重要子公司ShunYun Technology Holdi | — |
| 16 | 1 | 3 | dilewati | (補充115/3/13公告)本公司董事會決議不繼續辦理114 · 公告本公司不繼續辦理前經114年12月12日股東臨時會通過之 | 本次變更對股東權益之影響 |
| 7 | 3 | 0 | dilewati | 公告本公司因會計師事務所內部輪調更換會計師 · 玉山金控代子公司三商保代公告變更會計師事務所及簽證會計師 | — |
| 3 | 1 | 1 | dilewati | 公告本公司太子廠部份產線暫時停產事宜。 · 本公司業務大幅縮減，擬依法辦理大量解僱勞工並提報 「解僱計畫 | 出租之公司廠房或主要設備占總資產比例 · 質押之資產占總資產之比例 · 質押之資產占總資產比例 |
| 47 | 1 | 0 | dilewati | 公告本公司115年第三季合併財務報告因適用 T-IFRSs及 | 本國上市有價證券財務資訊之差異項目及金額 · 境外發行有價證券財務資訊之差異項目及金額 |
| 1 | 1 | 0 | dilewati | 公告說明本公司民國115年2月23日公司債到期尚未償還，本月 | 喪失債信之金額 |
| 40 | 1 | 0 | dilewati | 本公司因有重大訊息待公布，經證交所同意自115年11月10日 | — |
| 28 | 1 | 0 | dilewati | 公告本公司客戶 THE CHILDREN’S PLACE,  | 債權種類或背書保證金額及其所占資產比例 |
| 36 | 1 | 0 | dilewati | 公告本公司庫藏股註銷完成變更登記事宜 | — |
| 52 | 0 | 1 | dilewati | 公告本公司董事會決議通過因子公司蘇州冠禮科技股份有限 公司擬 | 對公司或子公司財務、業務或股東權益具重大影響之承諾事 |
| 44 | 0 | 1 | dilewati | 公告本公司獨立董事對薪酬委員會決議事項表示反對意見 及對董事 | — |

