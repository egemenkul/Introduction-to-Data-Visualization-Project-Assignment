# AI Asistan Kampusu

<div align="center">


`Local AI + Cloud AI = Daha hizli ogrenme`

[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-111827?style=for-the-badge)](https://docs.ollama.com/quickstart)
[![Gemini 3 Preview](https://img.shields.io/badge/Gemini%203-Preview-0f766e?style=for-the-badge)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/get-started-with-gemini-3)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI-1a73e8?style=for-the-badge)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/quickstart)

</div>

## KULLANIM KILAVUZU --- DİKKAT EDİLMESİ GEREKEN NOKTALAR
1D VERİ YORUMLAYICI - NEDİR?
Girilen n büyüklükte bir veri dizisi hakkında çeşitli yorumlar ve işlemleri yapmak için yazılmış, LLM destekli AI asistanı
Kullanım kılavuzu: Bir sayı dizisi seçtikten sonra F8 tuşuna basıldıktan sonra, çıkan seçeneklerden birini seçebilirsiniz.

**Önemli not: Model, ondalık verileri okurken tam ve ondalık kısmının "." ile ayırt edilmesi gerekmektedir. Örnek olarak: 10.5, 6.7, 8.9
**Önemli not: Model, nokta karakteri hariç her şeyi ayırtıcı olarak algılar.

## KULLANILABİLECEK SEÇENEKLER
1. TREND YORUMU:
LLM, verinin zaman içindeki değişimine göre verinin trendi, düzeni ve istikrarı hakkında teknik olmayan bilgiler verir.
-----------------------
2. ANOMALİ TESPİTİ:
LLM, veri ve verinin istatistiksel özellikleri (Ortalama, Standart Sapma) kullanılarak veri dizisi içindeki anormal verileri tespit eder.
-----------------------
3. YAPAY VERİ ÜRETİMİ:
LLM, veri ve verinin istatistiksel özelliklerini kullanarak veri dizisinin trendine uygun şekilde sentetik veri üretir. Üretilen veri sayısı 20'dir.
-----------------------
4. CSV DÖNÜŞTÜRME KODU:
LLM, girilen veriyi bilgisayarınızda CSV formatında bir dosya olarak kaydetmeniz için çalıştırmanız gereken bir script yazar. 
Gelecek güncellemelerde asistan dosyayı otomatik olarak kaydedecektir.
-----------------------
5. VERİ HİKAYESİ:
LLM, girilen veriyi yorumlar. Ani değişimler durumunda sensör veya bir sunucudan gelen verilerden kaynağın mı hatalı olduğunu, yoksa ani değişimlerin gerçek
değişim mi olduğu hakkında yorum yapar.
-----------------------
6. HİPOTEZ ÖNERİSİ:
LLM, verinin yapısına göre kullanmamız için bir istatistik testi önerisinde bulunur.
-----------------------
7. KISA RAPOR SEÇENEĞİ:
LLM, veri hakkında teknik bilgisi olmayan okuyucuların anlayabileceği şekilde kısa bir metin yazar.
-----------------------

## Dependencies (Bağlılıklar):
requests
pyperclip
pynput
pyautogui
sympy
Pillow
PyMuPDF
re
NumPy
MatplotLib

## Planlanan Güncellemeler:
1. CSV üretim scriptinin otonom çalışımı:
Bu güncellemenin hedefi, LLM tarafından üretilen scriptin kullanıcı dahil olmadan çalıştırılıp, dosyanın kaydedilmesi olacaktır.

2. Grafik oluşturma seçenekleri:
Bu güncellemenin hedefi, verinin hedefine uygun olan bir grafik türü ile veriyi görselleştirmek olacaktır.

3. LLM'e verilen istatistiksel bilgilerin arttırılması:
İlk versiyonu LLM'e sadece standart sapma ve ortalama bilgilerini sunar. Bu istatistiksel bilgilerin arttırılması (örn. Z-Score) asistanın daha iyi performans göstermesini sağlayacaktır.


## Kaynaklar (Resmi)
- Ollama Quickstart: https://docs.ollama.com/quickstart
- Ollama Windows: https://docs.ollama.com/windows
- Ollama Linux: https://docs.ollama.com/linux
- Vertex AI Quickstart: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/quickstart
- Gemini 3 Baslangic: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/get-started-with-gemini-3
- Gemini 3 Pro Model: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro
- Gemini 3 Flash Model: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-flash
