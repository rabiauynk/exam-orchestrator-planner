# 🧠 Sınav Planlama Kuralları

Bu dokümant, Exam Orchestrator sisteminde uygulanan gelişmiş sınav planlama kurallarını açıklar.

## 🕒 1. Tarih ve Saat Kuralları

### ✅ Yasak Saat Dilimleri
- **12:15-13:00 arası**: Hiçbir gün sınav yapılamaz (öğle molası)
- **Cuma 12:00-13:30 arası**: Cuma günleri bu saatlerde sınav yapılamaz (Cuma namazı)

### ✅ Saat Dilimi Boşlukları
- Aynı gün birden fazla sınav varsa, aralarında **en az 15 dakika** boşluk olmalıdır
- Bu kural sınıf değişimi ve hazırlık için gereklidir

### 📅 Geçerli Saat Dilimleri

**Normal Günler (Pazartesi-Perşembe):**
- 08:30-10:00
- 10:15-11:45
- 13:00-14:30
- 14:45-16:15
- 16:30-18:00

**Cuma Günleri:**
- 08:30-10:00
- 10:15-11:45
- 13:30-15:00
- 15:15-16:45
- 17:00-18:30

## 🧠 2. Zorluk (Kredi) Bazlı Kurallar

### ✅ Zor Ders Tanımı
- **Kredi ≥ 4** olan dersler "zor" kategorisinde kabul edilir
- Bu dersler daha fazla konsantrasyon gerektirir

### ✅ Zor Ders Kısıtlamaları
- **Aynı gün içinde sadece bir zor sınav** yapılabilir
- Bu kural öğrenci performansını korumak için uygulanır
- Zor sınavlar öncelikli olarak planlanır

### 📊 Kredi Seviyeleri
- **1-3 Kredi**: Normal zorluk
- **4+ Kredi**: Zor kategori (özel kısıtlamalar)

## 🧠 3. Çakışma Kuralları

### ✅ Sınıf Seviyesi Çakışmaları
- **Aynı sınıf seviyesindeki derslerin sınavları** aynı saat diliminde yapılamaz
- Örnek: Tüm 2. sınıf dersleri farklı saatlerde sınava girmeli
- Bu kural öğrencilerin birden fazla sınava aynı anda girmesini önler

### ✅ Zaman Çakışması Kontrolü
- Aynı saat diliminde çakışan sınavlar tespit edilir ve önlenir
- 15 dakikalık minimum boşluk kuralı uygulanır

## 🧠 4. Sınıf Atama Kuralları

### ✅ Kapasite Kontrolü
- Sınav için girilen **öğrenci sayısını karşılayacak** şekilde sınıf(lar) atanır
- Tek sınıf yeterli değilse, **birden fazla sınıf** otomatik olarak atanır

### ✅ Bilgisayar Gereksinimi
- **"Bilgisayar Gerekiyor"** seçildiyse, sadece bilgisayarlı sınıflar atanır
- Bilgisayar labları öncelikli olarak kullanılır

### ✅ Sınıf Çakışması Önleme
- **Aynı saat diliminde aynı sınıfa** birden fazla sınav atanamaz
- Sınıf kullanılabilirliği gerçek zamanlı kontrol edilir

### 🏢 Sınıf Tercihi Algoritması
1. **Bölüm uyumu**: Aynı bölümün sınıfları öncelikli
2. **Kapasite uyumu**: Öğrenci sayısına en yakın kapasite
3. **Bilgisayar gereksinimi**: Gerekirse sadece bilgisayarlı sınıflar

## 🧠 5. Tercih ve Tarih Aralığı Kuralları

### ✅ Hoca Tercihleri
- Hocalar her sınav için **3 farklı tarih tercihi** verir
- Sistem mümkünse bu tercihlere sadık kalır
- Tercihler sınav haftası içinde olmalıdır

### ✅ Sınav Haftası Kısıtı
- Sınavlar, admin tarafından belirlenen **sınav haftası tarih aralığı** içinde planlanır
- Hafta sonları otomatik olarak hariç tutulur

### ✅ Esneklik Kuralları
- Hocalar tarih aralığında **en az 3 gün** işaretlemelidir
- Daha az tercih = daha yüksek planlama önceliği

## 🔄 Planlama Algoritması

### 📊 Öncelik Sıralaması
Sınavlar aşağıdaki öncelik sırasına göre planlanır:

1. **Zor sınavlar** (kredi ≥ 4) - çakışma riskini azaltmak için
2. **Bilgisayar gerektiren sınavlar** - sınırlı kaynak
3. **Yüksek öğrenci sayısı** - kapasite kısıtları
4. **Uzun süre** - zaman dilimi kısıtları
5. **Az tercih** - daha az esneklik

### 🔍 Kısıt Kontrolü Sırası
Her sınav için aşağıdaki kontroller yapılır:

1. **Zaman dilimi kuralları** (yasak saatler, Cuma kısıtları)
2. **Zor sınav kuralları** (günde bir zor sınav)
3. **Sınıf seviyesi çakışmaları** (aynı sınıf, aynı saat)
4. **15 dakika boşluk** kuralı
5. **Sınıf kapasitesi** ve bilgisayar gereksinimi
6. **Sınıf müsaitliği** kontrolü

### ⚡ Optimizasyon Stratejileri

- **Backtracking**: Çakışma durumunda alternatif çözümler aranır
- **Constraint Satisfaction**: Tüm kısıtlar eş zamanlı kontrol edilir
- **Greedy Approach**: En kısıtlı sınavlar önce planlanır
- **Room Splitting**: Büyük sınavlar için birden fazla sınıf kullanımı

## 🛠️ Teknik Uygulama

### 📁 İlgili Dosyalar
- `services/scheduler_service.py`: Ana planlama servisi
- `services/advanced_scheduler.py`: Gelişmiş kısıt kontrolleri
- `models.py`: Exam.is_difficult property'si

### 🔧 Konfigürasyon
- Zor ders eşiği: `credits >= 4`
- Minimum boşluk: `15 dakika`
- Maksimum sınıf kombinasyonu: `3 sınıf`

### 📊 Performans Metrikleri
- Başarılı planlama oranı
- Tercih uyum oranı
- Sınıf kullanım verimliliği
- Çakışma önleme başarısı

## 🚨 Hata Durumları

### ❌ Planlama Başarısızlık Sebepleri
1. **Yetersiz sınıf kapasitesi**
2. **Zor sınav çakışması**
3. **Sınıf seviyesi çakışması**
4. **Bilgisayar lab yetersizliği**
5. **Tercih edilen tarihler uygun değil**

### 🔄 Çözüm Önerileri
- Sınav haftası aralığını genişletme
- Ek sınıf/lab tanımlama
- Tercih tarihlerini revize etme
- Sınav sürelerini optimize etme

## 📈 Gelecek Geliştirmeler

### 🎯 Planlanan Özellikler
- **OR-Tools entegrasyonu**: Daha gelişmiş optimizasyon
- **Machine Learning**: Geçmiş verilerden öğrenme
- **Multi-objective optimization**: Çoklu hedef optimizasyonu
- **Real-time constraints**: Gerçek zamanlı kısıt güncellemeleri

### 🔬 Araştırma Alanları
- Constraint Programming (CP-SAT)
- Genetic Algorithms
- Simulated Annealing
- Integer Linear Programming (ILP)
