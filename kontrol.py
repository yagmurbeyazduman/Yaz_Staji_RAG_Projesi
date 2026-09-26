import sqlite3

baglanti = sqlite3.connect("belgeler.db")
imlec = baglanti.cursor()

imlec.execute("SELECT id, content FROM belgeler_tablosu")
sonuclar = imlec.fetchall()

for satir in sonuclar:
    print(satir)

baglanti.close()