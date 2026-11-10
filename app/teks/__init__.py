"""Kunci terjemahan tambahan, satu berkas per agent/area kerja.

Setiap modul di folder ini mendefinisikan `T: dict[str, tuple[str, str, str]]`
(English, 繁體中文, Bahasa Indonesia), dimuat oleh app/i18n.py saat impor. Dengan begitu
beberapa agent bisa menambah teks bersamaan tanpa menyunting berkas yang sama.
Kunci yang sudah ada di app/i18n.py tidak boleh ditimpa (impor gagal bila bentrok).
"""
