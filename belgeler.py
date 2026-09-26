from pypdf import PdfReader
import os

def pdf_den_belgeleri_oku(dosya_adi, parca_boyutu=150, ortusme=30):
    reader = PdfReader(dosya_adi)

    tum_metin = ""
    for sayfa in reader.pages:
        tum_metin += sayfa.extract_text() + " "

    kelimeler = tum_metin.split()

    parcalar = []
    baslangic = 0
    while baslangic < len(kelimeler):
        bitis = baslangic + parca_boyutu
        parca = " ".join(kelimeler[baslangic:bitis])
        parcalar.append(parca.strip())
        baslangic += parca_boyutu - ortusme

    return parcalar


PDF_KLASORU = "pdfler"

belgeler = []
if os.path.isdir(PDF_KLASORU):
    for dosya in os.listdir(PDF_KLASORU):
        if dosya.lower().endswith(".pdf"):
            tam_yol = os.path.join(PDF_KLASORU, dosya)
            print(f"Okunuyor: {dosya}")
            belgeler.extend(pdf_den_belgeleri_oku(tam_yol))
else:
    belgeler = pdf_den_belgeleri_oku("dosyajava.pdf")