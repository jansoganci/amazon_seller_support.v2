# Amazon Seller Support

## Changelog

### [2025-01-15]
#### Added
- Revenue trends API iyileştirmeleri
  - Satış olmayan günler için 0 değeri atama
  - Doğru tarih sütunu kullanımı (date)
  - Recursive CTE ile tarih aralığı sorgusu
  - ASIN bazlı filtreleme
- Reklam raporu ekranı eklendi
  - Temel sayfa yapısı
  - Dashboard entegrasyonu
  - Filtreleme seçenekleri (kampanya, ad group, targeting type)
  - Metrik kartları ve grafikler için altyapı
#### Fixed
- Tarih filtreleme sorunları çözüldü
- SQL sorgularında performans iyileştirmeleri yapıldı

### [2025-01-13]
#### Added
- CSV veri yükleme işlevselliği tamamlandı (Business, Inventory, Advertising ve Return raporları)
- Store detay sayfası

#### Fixed
- Store yetkilendirme sorunu çözüldü
- CSV validasyon hataları düzeltildi

### [2025-01-09]
#### Added
- Store modeli ve ilişkileri
- CSV Validator güncellemeleri
- Mağazalarım UI geliştirmeleri

### [2025-01-05]
#### Added
- Seasonal Analytics geliştirmeleri
- Peak detection algoritması
- Test suite implementasyonu

## Active Issues 🐛
1. CSV yükleme hataları kullanıcıya gösterilmiyor
2. CSV sütun isimleri case-sensitive kontrol ediliyor
3. Store yetkilendirme sorunu tekrar ortaya çıktı (12.01.2025)

## Pending Tasks 📋
### High Priority
- [ ] Store düzenleme fonksiyonu
- [ ] Store silme fonksiyon
- [ ] Store bazlı rapor filtreleme
- [ ] Store işlemleri için audit log
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] Dashboard geliştirmeleri
  - [ ] Metric cards implementation
  - [ ] Interactive charts (Chart.js entegrasyonu)
  - [ ] Responsive design improvements
- [ ] Para birimi API entegrasyonu
- [ ] Raporlama geliştirmeleri
  - [ ] Monthly/Quarterly/Weekly trend analysis
  - [ ] Peak period detection
  - [ ] Special period analysis (Black Friday, Christmas)
  - [ ] Upload history tracking
- [ ] Shipment Planner
  - [ ] Shipment planning algoritması
  - [ ] AJAX ile anlık güncelleme

### Analytics Development 📊
#### 1. Finansal Performans Analizleri
- [ ] Toplam Gelir Trendi Raporu
- [ ] Kar Marjı Analiz Raporu
- [ ] ROI Analiz Raporu
- [ ] En Karlı Ürünler Raporu
- [ ] Sezonsal Gelir Dalgalanmaları Raporu

#### 2. Ürün Performans Analizleri
- [ ] En Çok Satan Ürünler Raporu
- [ ] En Yüksek Dönüşüm Oranlı Ürünler Raporu
- [ ] Stok Devir Hızı Raporu
- [ ] İade Oranı Yüksek Ürünler Raporu
- [ ] Düşük Performanslı Ürünler Raporu

#### 3. Stok ve Tedarik Analizleri
- [ ] Stok Tükenmesi Risk Raporu
- [ ] Aşırı Stoklu Ürünler Raporu
- [ ] Optimal Stok Seviyeleri Raporu
- [ ] Depo Dağılımı Optimizasyon Raporu
- [ ] Sezonsal Stok İhtiyacı Tahmin Raporu

#### 4. Reklam ve Marketing Analizleri
- [ ] Kampanya Performans Raporu
- [ ] ACOS Optimizasyon Raporu
- [ ] Reklam ROI Analiz Raporu
- [ ] Keyword Performans Raporu
- [ ] Kampanya Bütçe Optimizasyon Raporu

#### 5. Müşteri Memnuniyeti ve İade Analizleri
- [ ] İade Nedenleri Detay Raporu
- [ ] Kategori Bazlı İade Oranları Raporu
- [ ] Müşteri Memnuniyet Trend Raporu
- [ ] İade Maliyet Analiz Raporu
- [ ] Ürün İyileştirme Öneri Raporu

#### 6. Tahminsel Analizler
- [ ] Gelir Tahmin Raporu
- [ ] Stok İhtiyacı Tahmin Raporu
- [ ] Sezonsal Trend Tahmin Raporu
- [ ] Peak Dönem Performans Tahmin Raporu
- [ ] İade Oranı Tahmin Raporu

#### 7. Karşılaştırmalı Analizler
- [ ] Dönemsel Karşılaştırma Raporu (YoY, MoM)
- [ ] Kategori Performans Karşılaştırma Raporu
- [ ] Marketplace Karşılaştırma Raporu
- [ ] Kampanya Performans Karşılaştırma Raporu
- [ ] Rakip Analiz Raporu

#### 8. Aksiyon Önerileri
- [ ] Stok Optimizasyonu Öneri Raporu
- [ ] Reklam Bütçesi Ayarlama Raporu
- [ ] Ürün Fiyatlandırma Öneri Raporu
- [ ] İade Oranı İyileştirme Raporu
- [ ] Sezonsal Strateji Öneri Raporu

### Testing Tasks
- [ ] CSV format kontrolü testleri
- [ ] Hata mesajları kontrolü testleri
- [ ] Dosya kaydetme işlemi testleri
- [ ] Algoritma çıktı kontrolü testleri

### Future Releases
- [ ] CSV export fonksiyonu (Faz 2)
- [ ] Diğer rapor tiplerinin CSV entegrasyonu

## Completed Features ✅
- [x] CSV örnek dosya şablonu oluşturma
- [x] CSV yükleme kılavuzu hazırlama
- [x] Hata mesajlarını daha açıklayıcı hale getirme
- [x] CSV doğrulama sürecini hızlandırma
- [x] Store bazlı yetkilendirme
- [x] Kullanıcı-store ilişkisi kontrolü
- [x] Business Report CSV entegrasyonu
- [x] Advertising Report CSV entegrasyonu
- [x] Return Report CSV entegrasyonu
- [x] Inventory Report CSV entegrasyonu

## Technical Specifications

### CSV Format Specifications
#### Business Report
```
store_id, date, sku, asin, title, sessions, units_ordered, ordered_product_sales, total_order_items, conversion_rate
```

#### Advertising Report
```
store_id, date, campaign_name, ad_group_name, targeting_type, match_type, search_term, impressions, clicks, ctr, cpc, spend, total_sales, acos, total_orders, total_units, conversion_rate
```

#### Return Report
```
store_id, return_date, order_id, sku, asin, title, quantity, return_reason, status, refund_amount, return_center, return_carrier, tracking_number
```

#### Inventory Report
```
store_id, date, sku, asin, product_name, condition, price, mfn_listing_exists, mfn_fulfillable_quantity, afn_listing_exists, afn_warehouse_quantity, afn_fulfillable_quantity, afn_unsellable_quantity, afn_reserved_quantity, afn_total_quantity, per_unit_volume
```

## Development Roadmap

### Phase 1: Data Processing Infrastructure
- CSV Processing System
- Data Validation Layer
- Store Management System

### Phase 2: Analytics Engine
- Analysis System
- Inventory Planning
- Advanced Reporting

### Phase 3: Testing & Optimization
- Unit Tests
- Integration Tests
- Performance Tests
- Security Improvements

## Technical Notes
- Store ID'ler veritabanı tarafından otomatik oluşturuluyor
- Her store bir kullanıcıya ait olmalı
- CSV yüklemelerinde store_id kontrolü kullanıcı bazlı yapılıyor
- Yeni CSV formatları daha detaylı veri içeriyor
- Tarih alanları datetime objesine dönüştürülüyor
- CSV hata mesajları frontend'e iletilmiyor
- CSV sütun isimlerinde büyük/küçük harf duyarlılığı var