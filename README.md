# Yaz_Staji_RAG_Projesi
Foundry Local RAG Projesi

Microsoft yaz staj programı kapsamında Azure Foundry Local kullanılarak geliştirilmiş, tamamen çevrimdışı çalışan yerel bir RAG (Retrieval-Augmented Generation) soru-cevap asistanı.

Projenin Amacı

Bu proje, kullanıcının yüklediği PDF belgelerini okuyup, bu belgeler hakkında sorulan sorulara internete bağlanmadan, tamamen kullanıcının kendi bilgisayarında çalışarak cevap veren bir asistan geliştirmeyi amaçlamaktadır.

Sistem, büyük dil modellerinin (LLM) genel bilgiye dayanarak ürettiği ve zaman zaman hatalı olabilen ("halüsinasyon") cevaplar yerine, kullanıcının kendi belgelerine dayanan, doğrulanabilir cevaplar üretir.

Nasıl Çalışıyor?
Veri Alma (Ingestion): PDF belgeleri okunur, küçük parçalara (chunk) bölünür.
Embedding: Her parça, qwen3-embedding modeli kullanılarak sayısal bir vektöre çevrilir.
Depolama: Metin ve embedding vektörleri SQLite veritabanında kalıcı olarak saklanır.
Retrieval (Getirim): Kullanıcı bir soru sorduğunda, sorunun embedding'i çıkarılır ve veritabanındaki en alakalı parça, kosinüs benzerliği ile bulunur.
Generation (Üretim): Bulunan parça, bir system prompt ile birlikte yerel sohbet modeline (qwen2.5) gönderilir; model, yalnızca bu bağlamı kullanarak cevap üretir.
Kullanılan Teknolojiler
Microsoft Foundry Local — yerel/çevrimdışı LLM çalıştırma
Python — SQLite (veritabanı), pypdf (PDF okuma), numpy (benzerlik hesabı)
RAG mimarisi — embedding tabanlı getirim + bağlama dayalı üretim
Kurulum
bash
# Foundry Local'i kurun (Windows)
winget install Microsoft.FoundryLocal

# Python bağımlılıklarını kurun
python -m pip install foundry-local-sdk-winml openai numpy pypdf
Kullanım
bash
python rag.py

Program başladığında modelleri yükler, ardından terminalden soru sorabilirsiniz. Çıkmak için q yazmanız yeterlidir.

Sorunuz: Algoritma nedir?
(Bulunan ilgili belge: ...)
Cevap: ...
Proje Dosyaları
Dosya	Açıklama
belgeler.py	PDF'ten metin okuma ve parçalara bölme
embed.py	Metinleri embedding vektörlerine çevirme (test amaçlı)
veritabani.py	Embedding'leri SQLite'a kaydetme
sor.py	Tek seferlik soru-cevap testi (retrieval odaklı)
rag.py	Tam RAG döngüsü — sürekli soru-cevap arayüzü
kontrol.py	Veritabanı doğrulama aracı
Geliştirme Sürecinde Karşılaşılan Sorunlar ve Çözümleri

Geliştirme sürecinde çeşitli teknik zorluklarla karşılaşıldı; bu sorunlar ve çözümleri aşağıda listelenmiştir:

Sonsuz tekrar döngüsü: Küçük parametreli modellerde görülen, aynı kelime/cümlenin tekrar tekrar üretilmesi sorunu. frequency_penalty, temperature ve max_tokens gibi üretim (generation) parametreleri ayarlanarak çözüldü.
Alakasız sorulara hatalı cevap üretme: Bağlamla ilgisi olmayan sorularda bile modelin bir cevap uydurmaya çalışması, bir benzerlik eşiği (similarity threshold) eklenerek engellendi — skor eşiğin altındaysa sistem "bu konuda bilgi bulunmuyor" yanıtını veriyor.
Parçalama (chunking) doğruluğu: Sabit karakter sayısına göre bölme, cümlelerin ortadan kesilmesine yol açıyordu; kelime bazlı ve örtüşmeli (overlapping) bir chunking yöntemine geçilerek getirim doğruluğu artırıldı.
Türkçe karakter kodlama sorunu: Windows terminalinde Türkçe karakterlerin bozuk görünmesi, UTF-8 kodlaması zorlanarak çözüldü.
Model kalitesi: Cevap tutarlılığını artırmak için daha büyük parametreli bir sohbet modeline geçildi.
Çoklu PDF desteği: Sistem, tek belge yerine birden fazla PDF'i aynı anda işleyebilecek şekilde genişletildi.
Bilinen Sınırlamalar
Küçük/orta ölçekli yerel modeller, büyük bulut modellerine (GPT-4 gibi) kıyasla prompt talimatlarına daha az sadık kalabiliyor.
Yanıt hızı, kullanılan donanıma (CPU/GPU/NPU) bağlı olarak değişkenlik gösterebilir.
Chunking stratejisi, karmaşık tablo/kod içeren PDF'lerde iyileştirmeye açıktır.
