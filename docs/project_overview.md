# Amazon Seller Support Tool - Project Overview

## 1. Proje Amacı
Amazon satıcılarının mağaza verilerini analiz etmelerini, trendleri takip etmelerini ve veri odaklı kararlar almalarını sağlayan bir analitik platformu geliştirmek.

## 2. Hedefler
- Farklı rapor türleri için tutarlı ve kullanıcı dostu bir arayüz sunmak
- Veri analizini otomatikleştirmek ve hızlandırmak
- Özelleştirilebilir metrik ve görselleştirmeler sağlamak
- Yüksek performanslı ve ölçeklenebilir bir sistem oluşturmak

## 3. Rapor Türleri ve Özellikleri

### 3.1 Business Report
- Satış performansı analizi
- Ürün bazlı metrikler
- Dönüşüm oranları ve trend analizi
- Kategori bazlı performans karşılaştırması

### 3.2 Inventory Report
- Stok seviyesi takibi
- Stok devir hızı analizi
- Tedarik zinciri metrikleri
- Stok maliyeti analizi

### 3.3 Returns Report
- İade oranları analizi
- İade nedenleri dağılımı
- Ürün/kategori bazlı iade analizi
- İade maliyeti hesaplaması

### 3.4 Advertisement Report
- Reklam performansı analizi
- ACOS ve TACOS metrikleri
- Kampanya bazlı analiz
- ROI hesaplaması

## 4. Teknik Altyapı

### 4.1 Metrik Sistemi
```typescript
interface MetricConfig {
    id: string;
    name: string;
    description: string;
    formula: string | ((data: any[]) => number);
    category: 'sales' | 'inventory' | 'advertising' | 'customer' | 'logistics' | 'custom';
    dependencies?: string[];
    visualization: {
        type: 'currency' | 'percentage' | 'number' | 'custom';
        format?: string;
        chartType?: 'line' | 'bar' | 'pie';
        options?: {
            stacked?: boolean;
            cumulative?: boolean;
            compareWithPrevious?: boolean;
        };
    };
    permissions?: string[];
    thresholds?: {
        warning?: number;
        critical?: number;
        direction?: 'asc' | 'desc';
    };
    caching?: {
        duration: number;
        key: string[];
    };
}

// Örnek Metrik Tanımları
const BusinessMetrics: Record<string, MetricConfig> = {
    total_revenue: {
        id: 'total_revenue',
        name: 'Total Revenue',
        description: 'Total revenue from all orders',
        formula: 'sum(ordered_product_sales)',
        category: 'sales',
        visualization: {
            type: 'currency',
            format: '$0,0.00',
            chartType: 'line',
            options: {
                compareWithPrevious: true
            }
        },
        thresholds: {
            warning: 1000,
            critical: 500,
            direction: 'desc'
        }
    },
    conversion_rate: {
        id: 'conversion_rate',
        name: 'Conversion Rate',
        description: 'Percentage of sessions resulting in orders',
        formula: '(sum(units_ordered) / sum(sessions)) * 100',
        category: 'sales',
        visualization: {
            type: 'percentage',
            format: '0.00%',
            chartType: 'line'
        },
        thresholds: {
            warning: 2,
            critical: 1,
            direction: 'desc'
        }
    }
};
```

### 4.2 Filtreleme Sistemi
```typescript
interface FilterDefinition {
    id: string;
    type: 'date' | 'select' | 'multiselect' | 'text' | 'number' | 'boolean';
    defaultValue?: any;
    validation?: {
        required?: boolean;
        min?: number;
        max?: number;
        pattern?: string;
    };
    dependencies?: {
        field: string;      // Bağımlı olduğu filtre
        condition: string;  // Koşul
        value: any;        // Koşul değeri
    }[];
}

## Business Analytics Development Status

### Completed Features
1. **Metric Engine Implementation**
   - Created core metric engine for business analytics
   - Implemented metric registration system
   - Added support for metric visualization configurations

2. **Business Report Service**
   - Implemented trend analysis for key metrics
   - Added support for historical comparisons
   - Integrated growth rate calculations
   - Metrics implemented:
     - Total Revenue (ordered_product_sales)
     - Total Orders (total_order_items)
     - Sessions
     - Conversion Rate

3. **Data Processing**
   - Added support for date range filtering
   - Implemented category and ASIN filtering
   - Added data aggregation by daily/weekly/monthly periods

4. **UI Components**
   - Created metric card component with:
     - Current value display
     - Growth rate comparison
     - Icon support
     - Tooltip information
   - Implemented chart containers for metric visualization
   - Added filter controls for date, category, and ASIN selection

### Current Issues
1. **Template Rendering Issue**
   ```
   ERROR:app.modules.business.routes:Error rendering business report: business/business_report.html
   jinja2.exceptions.TemplateNotFound: business/business_report.html
   ```
   - Fixed by updating blueprint template folder configuration

2. **Metric Registration Error**
   ```
   ERROR:app.modules.business.routes:Error rendering business report: Metric total_revenue already registered
   ValueError: Metric total_revenue already registered
   ```
   - Fixed by moving metric registration to module initialization

3. **Current Issue: Metric Card Display**
   - Problem: Business report page closes after adding metric cards section
   - Possible causes:
     - Template syntax error in metric card rendering
     - Missing required parameters in metric_card macro
     - Incorrect data format in initial_data

### Next Steps
1. **Debug Metric Card Display**
   - Review metric_card.html component requirements
   - Verify all required parameters are passed correctly
   - Test metric card rendering with minimal data

2. **Data Format Standardization**
   - Ensure consistent data format between service and template
   - Add data validation and formatting utilities
   - Implement proper error handling for missing or invalid data

3. **UI Improvements**
   - Implement 4x1 grid layout for metric cards
   - Add 1x4 layout for charts
   - Improve responsive design for mobile views

4. **Performance Optimization**
   - Add caching for frequently accessed metrics
   - Optimize database queries
   - Implement lazy loading for charts

### Technical Debt
1. **Flask-Limiter Warning**
   ```
   UserWarning: Using the in-memory storage for tracking rate limits...
   ```
   - Need to implement proper storage backend (Redis) for production

## 5. İş Planı ve Öncelikler

### Faz 1: Temel Altyapı (2 Hafta)
- [x] Proje mimarisinin oluşturulması
- [ ] Metrik motoru geliştirme
  - [ ] Formül parser implementasyonu
  - [ ] Metrik hesaplama engine
  - [ ] Önbellekleme mekanizması
- [ ] Dinamik filtre sistemi
  - [ ] Filtre bileşenleri
  - [ ] Filtre state yönetimi
  - [ ] URL entegrasyonu

### Faz 2: Business Report (2 Hafta)
- [ ] Veri modeli ve API'lerin geliştirilmesi
  - [ ] Metrik tanımları
  - [ ] API endpoint'leri
  - [ ] Veri dönüşüm katmanı
- [ ] Frontend geliştirme
  - [ ] Dinamik metrik kartları
  - [ ] Grafik bileşenleri
  - [ ] Filtre paneli
- [ ] Performans optimizasyonu
  - [ ] Web worker implementasyonu
  - [ ] Veri örnekleme
  - [ ] Debouncing

### Faz 3: Diğer Raporlar (4 Hafta)
- [ ] Inventory Report implementasyonu
- [ ] Returns Report implementasyonu
- [ ] Advertisement Report implementasyonu
- [ ] Cross-report analiz özelliklerinin eklenmesi

### Faz 4: İyileştirmeler ve Optimizasyon (2 Hafta)
- [ ] Performans optimizasyonu
- [ ] Hata yakalama ve loglama
- [ ] UI/UX iyileştirmeleri
- [ ] Dokümantasyon ve test coverage

## 6. Kalite Kriterleri
- Tüm metrikler için birim testleri
- %90+ test coverage
- 1 saniyeden kısa sayfa yüklenme süresi
- Mobil uyumlu responsive tasarım
- WCAG 2.1 AA seviyesi erişilebilirlik

## MVP - Kategori Yönetimi Planı

#### 1. Veritabanı Modelleri
- **Category Model**
  ```python
  class Category(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(100), nullable=False)
      code = db.Column(db.String(10), unique=True, nullable=False)
      parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
      subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
  ```

- **AsinCategory Model**
  ```python
  class AsinCategory(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      asin = db.Column(db.String(20), unique=True, nullable=False)
      category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
      sub_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
      category = db.relationship('Category', foreign_keys=[category_id])
      subcategory = db.relationship('Category', foreign_keys=[sub_category_id])
  ```

#### 2. Admin Yetkilendirmesi
- Basit HTTP Basic Auth implementasyonu
- Sabit admin kullanıcı adı ve şifre
- Sadece admin veri girişi yapabilir

#### 3. Terminal Komutları
- ASIN ve kategori ekleme için CLI komutları
- Örnek kullanım:
  ```bash
  flask add-category FASHION FSH
  flask add-subcategory SUNGLASSES SGL FASHION
  flask add-asin B0123456789 FSH SGL
  ```

#### 4. API Endpoints
- `/api/categories`: Tüm kategori ve alt kategorileri döndürür
- `/api/asin-categories`: ASIN ve kategori bilgilerini döndürür

#### 5. Frontend Entegrasyonu
- Kategori dropdown'ları için JavaScript fonksiyonları
- ASIN verilerini çekmek için API çağrıları
- Rapor tablosunu güncellemek için fonksiyonlar

### Yapılacaklar

1. **Kategori Yönetimi - MVP**
   - [ ] Veritabanı modellerini oluştur
   - [ ] Admin yetkilendirmesini ekle
   - [ ] CLI komutlarını implement et
   - [ ] API endpoint'lerini oluştur
   - [ ] Frontend entegrasyonunu tamamla

2. **Rapor Entegrasyonu**
   - [ ] Business report template'ini güncelle
   - [ ] Kategori filtrelerini ekle
   - [ ] ASIN filtrelerini ekle
   - [ ] JavaScript kodunu revize et
   - [ ] Filtreleme mantığını test et

3. **Test ve Deploy**
   - [ ] Veritabanı migration'larını oluştur
   - [ ] Test verilerini hazırla
   - [ ] Tüm API endpoint'lerini test et
   - [ ] Frontend fonksiyonlarını test et
   - [ ] Uygulamayı çalıştır ve hataları gider

### Gelecek Geliştirmeler
1. **Otomatik Kategori Atama**
   - Amazon API entegrasyonu
   - Kategori tahmin algoritması
   - Bulk import desteği

2. **Admin Arayüzü**
   - Web tabanlı veri girişi
   - Kategori yönetim paneli
   - ASIN yönetim paneli

3. **API Geliştirmeleri**
   - Pagination
   - Gelişmiş filtreleme
   - Rate limiting
