# Analytics Development Progress

## Genel Bilgiler
- **Başlangıç Tarihi:** 2024-01-15
- **Tahmini Bitiş:** 2024-01-22 (MVP)
- **Sorumlu Ekip:** Analytics Team

## Faz 1: MVP (1 Hafta)

### 1. Toplam Gelir Trendi Raporu
- [x] Veri Toplama ve İşleme
  - [x] BusinessReport'tan günlük satış verilerinin çekilmesi
  - [x] Zaman bazlı gruplandırma (günlük/haftalık/aylık)
  - [x] Büyüme oranı hesaplamaları
  - [x] Satış olmayan günler için 0 değeri atama
  - [x] Doğru tarih sütunu kullanımı (date)
- [x] Görselleştirme
  - [x] Chart.js line chart implementasyonu
  - [ ] Tooltip ve legend düzenlemeleri
- [x] Filtreleme
  - [x] Store bazlı filtreleme
  - [x] Tarih aralığı seçimi
  - [x] Kategori filtreleme
  - [x] ASIN bazlı filtreleme

**Tamamlanan Backend Geliştirmeleri:**
- AnalyticsEngine sınıfına get_revenue_trends metodu eklendi
- API endpoint (/analytics/api/revenue/trends) oluşturuldu
- SQLAlchemy sorgularından düz SQL'e geçiş yapıldı
- Test verisi oluşturma script'i yazıldı
- ASIN-kategori eşleştirme yapısı oluşturuldu
- Recursive CTE ile tarih aralığı sorgusu iyileştirildi
- Tarih filtreleme performansı artırıldı

**Sonraki Adımlar:**
1. Seasonal analytics metodlarını düz SQL'e çevirme
2. Chart.js tooltip ve legend düzenlemeleri
3. Test verilerinin görüntülenmesini sağlama

### 2. En Karlı Ürünler Raporu
- [ ] Veri İşleme
  - [ ] Ürün bazlı satış verilerinin toplanması
  - [ ] Kar marjı hesaplamaları
  - [ ] Top 10 listesi oluşturma
- [ ] Görselleştirme
  - [ ] Bar chart implementasyonu
  - [ ] Detay tablosu

### 3. Kar Marjı Analiz Raporu
- [ ] Hesaplamalar
  - [ ] Ürün bazlı kar marjı
  - [ ] Kategori bazlı kar marjı
  - [ ] Trend analizi
- [ ] Görselleştirme
  - [ ] Multi-line chart
  - [ ] Karşılaştırma grafikleri

### 4. Temel Dashboard
- [ ] Metric Cards
  - [ ] Toplam Gelir
  - [ ] Toplam Sipariş
  - [ ] Ortalama Sipariş Değeri
  - [ ] Stok Durumu
- [ ] Layout
  - [ ] Responsive grid tasarımı
  - [ ] Dark/Light mode desteği

### 5. Güvenlik
- [ ] Rate Limiting
  - [ ] API endpoint koruması
  - [ ] Store bazlı limit
- [ ] Input Sanitization
  - [ ] CSV validation
  - [ ] Form input temizleme

### 2. Reklam Performans Raporu
- [x] Temel Yapı
  - [x] Reklam raporu sayfası oluşturuldu
  - [x] Dashboard entegrasyonu tamamlandı
  - [x] Route yapısı eklendi
- [ ] Veri İşleme
  - [ ] Reklam verilerinin çekilmesi
  - [ ] Metrik hesaplamaları (ACOS, CTR, CPC)
  - [ ] Kampanya bazlı analiz
- [ ] Görselleştirme
  - [ ] Spend vs Sales grafiği
  - [ ] CTR trend grafiği
  - [ ] CPC trend grafiği
  - [ ] Conversion Rate grafiği
- [ ] Filtreleme
  - [x] Tarih aralığı seçimi
  - [x] Kampanya filtreleme
  - [x] Ad Group filtreleme
  - [x] Targeting Type filtreleme

**Tamamlanan Backend Geliştirmeleri:**
- Reklam raporu template'i oluşturuldu
- Route ve API endpoint yapısı hazırlandı
- Dashboard'a reklam kartı eklendi
- Kampanya ve Ad Group listeleme sorguları eklendi

**Sonraki Adımlar:**
1. API endpoint'inin tamamlanması
2. Chart.js grafik implementasyonları
3. Metrik hesaplama fonksiyonlarının yazılması

## Faz 2: Gelişmiş Özellikler (2 Hafta)

### 1. ROI Analiz Raporu
- [ ] Hesaplamalar
  - [ ] Kampanya bazlı ROI
  - [ ] Ürün bazlı ROI
  - [ ] Trend analizi
- [ ] Görselleştirme
  - [ ] ROI dashboard
  - [ ] Karşılaştırma grafikleri

### 2. Sezonsal Analiz
- [ ] Veri İşleme
  - [ ] Sezonsal pattern tespiti
  - [ ] YoY karşılaştırma
  - [ ] Peak dönem analizi
- [ ] Görselleştirme
  - [ ] Sezonsal trend grafikleri
  - [ ] Tahmin grafikleri

### 3. Detaylı Raporlama
- [ ] Kampanya Performans
  - [ ] ACOS analizi
  - [ ] Keyword performans
- [ ] Stok Optimizasyonu
  - [ ] Stok tükenme tahminleri
  - [ ] Optimal stok önerileri
- [ ] Müşteri Memnuniyeti
  - [ ] İade oranları
  - [ ] Müşteri feedback analizi

### 4. Gelişmiş Güvenlik
- [ ] Audit Logging
  - [ ] Kullanıcı aktivite logları
  - [ ] Rapor erişim logları
- [ ] Input Validation
  - [ ] Gelişmiş CSV validasyonu
  - [ ] XSS koruması

### 5. Para Birimi Entegrasyonu
- [ ] API Entegrasyonu
  - [ ] Döviz kuru servisi bağlantısı
  - [ ] Otomatik güncelleme
- [ ] Multi-currency Raporlama
  - [ ] Para birimi dönüşümleri
  - [ ] Raporlarda çoklu para birimi desteği

## Teknik Notlar
- Tüm grafiklerde Chart.js kullanılacak
- Veri işleme için pandas ve numpy
- API rate limiting için Flask-Limiter
- Input sanitization için bleach
- Testing için pytest
- SQLAlchemy yerine düz SQL sorguları kullanılacak
- ASIN bazlı kategori yönetimi için JSON dosyası kullanılacak

## Bağımlılıklar
- Business Report verileri
- Inventory Report verileri
- Advertising Report verileri
- Store yetkilendirme sistemi

## KPIs
- Sayfa yüklenme süresi < 2 saniye
- API response time < 500ms
- Test coverage > 80% 