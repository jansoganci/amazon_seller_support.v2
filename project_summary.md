# Amazon Seller Support - Proje Özeti

## 0. Dikkat Edilecek Dokümanlar (Önce Bu dokamnları inceleyin):
- [AI Guidelines](ai_guidelines.md)
- [Readme](readme.md)
- [Progress](progress.md)
- [Design Guide](design_guide.md)

## 1. AI Guidelines (ai_guidelines.md)
- **Uzmanlık Alanları**:
  - Backend: Flask, Güvenli Kimlik Doğrulama, API Entegrasyonları
  - Frontend: HTML, Tailwind CSS, UX İyileştirmeleri
  - Veritabanı: SQLite, PostgreSQL
  - Tasarım: Modern UI/UX standartları
  - Amazon Platform: Seller Tools, CSV analizi

- **Vizyon**:
  - Temiz ve modern arayüz
  - Tam mobil uyumluluk
  - Gelişmiş analitik özellikler

## 2. Readme (readme.md)
- **Amaç**: Amazon satıcıları için CSV analiz aracı
- **Teknolojiler**: Flask, Tailwind CSS, SQLite, Jinja2
- **Ana Özellikler**:
  - CSV dosya yükleme ve analiz
  - Dashboard görüntüleme
  - Shipment planlama
  - Kimlik doğrulama sistemi

## 3. Progress (progress.md)
### Tamamlanan İşler:
- Temel yapı kurulumu
- Veritabanı modelleri
- Arayüz geliştirmeleri (Bootstrap'a geçiş)
- CSV işleme servisleri

### Devam Eden İşler:
- CSV upload testleri
- Flash mesaj sistemi düzeltmeleri
- Yönlendirme sorunları

### Sonraki Adımlar:
- Flash mesaj sistemini düzeltme
- Test verilerini kontrol
- CSV yükleme hatalarını iyileştirme

## 4. Design Guide (design_guide.md)
### Tasarım Prensipleri:
- Minimal ve işlevsel tasarım
- Responsive yapı
- WCAG 2.1 erişilebilirlik standartları

### Tema Özellikleri:
- Gece/Gündüz modu desteği
- Tutarlı renk paleti
- Modern tipografi
- Modüler CSS yapısı

### Veritabanı Şeması:
- Users
- Stores
- Products
- Sales
- Inventory

### CSV Dosya Yapıları:
- Business Reports
- Inventory Reports
- Order History
