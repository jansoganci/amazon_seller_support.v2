# Amazon Seller Support Tool - Project Overview

## 1. Proje Amacı
Amazon satıcılarının mağaza verilerini analiz etmelerini, trendleri takip etmelerini ve veri odaklı kararlar almalarını sağlayan bir analitik platformu geliştirmek.

## 2. Hedefler
- Farklı rapor türleri için tutarlı ve kullanıcı dostu bir arayüz sunmak
- Veri analizini otomatikleştirmek ve hızlandırmak
- Özelleştirilebilir metrik ve görselleştirmeler sağlamak
- Yüksek performanslı ve ölçeklenebilir bir sistem oluşturmak
- Modüler ve genişletilebilir bir mimari sağlamak

## 3. Modüler Mimari

### 3.1 Temel Prensipler
- Her modül bağımsız çalışabilir
- Ortak altyapıyı kullanır ama özelleştirebilir
- Kod tekrarını minimize eder
- Modüller arası bağımlılık minimum seviyede

### 3.2 Ortak Altyapı Bileşenleri

#### Template Engine
- Tüm modüller için ortak template yapısı
- Modül özelinde özelleştirilebilir bloklar
- Tutarlı kullanıcı deneyimi
```html
<!-- base_report.html -->
{% extends "base.html" %}
{% block content %}
  {% block metrics_section %}{% endblock %}
  {% block chart_section %}{% endblock %}
  {% block table_section %}{% endblock %}
{% endblock %}
```

#### Analytics Engine
- Her modül için bağımsız analitik motoru
- Ortak metrik hesaplama altyapısı
- Modüle özel metrik ve grafik desteği
```python
class BaseAnalyticsEngine:
    def calculate_base_metrics(self):
        pass
    
class BusinessAnalytics(BaseAnalyticsEngine):
    def calculate_sales_metrics(self):
        pass
```

### 3.3 Modül Yapısı
Her modül (Business, Inventory, Advertising, Returns) şu yapıyı takip eder:
```
/modules/{module_name}/
  ├── routes.py           # Endpoint tanımları
  ├── models.py           # Veri modelleri
  ├── services/
  │   ├── report.py      # Rapor servisleri
  │   └── analytics.py   # Analitik servisleri
  ├── templates/
  │   └── {module_name}/ # Modüle özel template'ler
  └── static/
      └── {module_name}/ # Modüle özel statik dosyalar
```

## 4. Rapor Türleri ve Özellikleri

### 4.1 Business Report
- Satış performansı analizi
- Ürün bazlı metrikler
- Dönüşüm oranları ve trend analizi
- Kategori bazlı performans karşılaştırması

#### MVP Özellikleri
- **Filtreler**:
  - Tarih aralığı
  - Group by (daily/weekly/monthly)
  - Ana kategori
  - ASIN

- **Grafikler**:
  1. Revenue Trend (Line Chart)
  2. Orders & Units (Bar Chart)
  3. Conversion Rate (Line + Area)
  4. Top Performers (Horizontal Bar)

- **Backend**:
  - SQLAlchemy ile veri sorgulama
  - Pandas ile veri işleme
  - Metrik hesaplama

- **Frontend**:
  - Alpine.js ile state management
  - Chart.js ile grafikler
  - TailwindCSS ile responsive tasarım

#### Geliştirme Sırası
1. Temel filtreler ve veri yapısı
2. İlk iki grafik (Revenue + Orders/Units)
3. Conversion Rate grafiği
4. Top Performers grafiği
5. Eksik tarih doldurma mantığı
6. UI/UX iyileştirmeleri

#### MVP Sonrası
- Quarterly/Yearly group by
- Alt kategori desteği
- Daha fazla metrik
- Export özellikleri
- Detaylı tablo görünümü

### 4.2 Inventory Report
- Stok seviyesi takibi
- Stok devir hızı analizi
- Tedarik zinciri metrikleri
- Stok maliyeti analizi

### 4.3 Returns Report
- İade oranları analizi
- İade nedenleri dağılımı
- Ürün/kategori bazlı iade analizi
- İade maliyeti hesaplaması

### 4.4 Advertisement Report
- Reklam performansı analizi
- ACOS ve TACOS metrikleri
- Kampanya bazlı analiz
- ROI hesaplaması

## 5. Teknik Altyapı

### 5.1 Metrik Sistemi
Her modül kendi metriklerini tanımlar ancak ortak bir format kullanır:
```python
METRIC_CONFIG = {
    'id': str,          # Metrik ID
    'name': str,        # Görünen isim
    'category': str,    # Metrik kategorisi
    'formula': Callable, # Hesaplama fonksiyonu
    'visualization': {   # Görselleştirme ayarları
        'type': str,
        'options': dict
    }
}
```

### 5.2 Filtreleme Sistemi
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
        field: string;      
        condition: string;  
        value: any;        
    }[];
}
```

## 6. Geliştirme Durumu

### 6.1 Tamamlanan Özellikler
1. **Metrik Motoru**
   - Temel metrik motoru oluşturuldu
   - Metrik kayıt sistemi implementasyonu
   - Görselleştirme konfigürasyonları

2. **Rapor Servisleri**
   - Trend analizi implementasyonu
   - Tarihsel karşılaştırmalar
   - Büyüme oranı hesaplamaları

3. **Kategori Yönetimi**
   - Veritabanı modelleri
   - Admin yetkilendirmesi
   - API endpoint'leri
   - Frontend entegrasyonu

4. **Authentication ve Authorization**
   - Authentication ve authorization sistemi tamamlandı

### 6.2 Devam Eden Çalışmalar
1. **Analytics Engine Geliştirmeleri**
   - Modül bazlı analitik motorları
   - Özelleştirilebilir metrik hesaplamaları
   - Performans optimizasyonları

2. **Template Sistemi**
   - Ortak template yapısı
   - Modül özel blokları
   - Komponent sistemi

### 6.3 Planlanan Geliştirmeler
1. **Modüler Yapı İyileştirmeleri**
   - Her modül için bağımsız analitik motoru
   - Özelleştirilebilir metrik ve grafikler
   - Minimum modül bağımlılığı

2. **Performans Optimizasyonları**
   - Veritabanı sorgu optimizasyonları
   - Önbellek stratejileri
   - Asenkron veri işleme

## 7. Katkıda Bulunma
1. Yeni bir modül eklerken modül yapısını takip edin
2. Ortak altyapı bileşenlerini kullanın
3. Modül özelinde gerekli özelleştirmeleri yapın
4. Test coverage'ını koruyun
