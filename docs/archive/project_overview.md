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


Amazon Seller Analytics - Technical Documentation & Work Plan

Project Overview

This document outlines the technical specifications and work plan for developing an Amazon Seller Analytics tool. The tool aims to provide analytics capabilities to Amazon sellers, focusing on metrics such as sales, revenue analysis, and conversion rates, with an initial emphasis on building a modular and MVP-compliant system.

1. Project Goals and Objectives

Primary Objective
	•	Build a modular analytics engine to process and analyze sales, revenue, and inventory data for Amazon sellers.
	•	Focus on delivering an MVP (Minimal Viable Product) that supports basic filtering, metric calculations, and reporting functionalities with minimal complexity and high usability.

Future Objectives
	•	Expand the MVP with advanced analytics, user interactivity, AI-powered insights, and data visualizations in later versions.

2. Key Features for MVP

Core Features (To be included in MVP):
	1.	Filtering System:
	•	Data Filters: Date range, category, and ASIN filters for querying data.
	•	SQL-based filtering for rapid data extraction.
	•	Basic query optimization via indexing and other performance strategies in future updates.
	2.	Metric Calculation:
	•	Basic Metrics: Revenue, Sales Metrics, Conversion Rate.
	•	Each module (Business, Inventory, etc.) will have its own metric calculation.
	3.	Reporting System:
	•	Basic reports for key metrics.
	•	Graphics: Simple trend graphs (e.g., revenue trends, conversion rates) presented to the user.
	•	User will receive summarized data based on chosen filters.
	4.	Modular Data Architecture:
	•	Modular System: Each module (Business, Inventory, Returns) is self-contained, and no inter-module data sharing is required in the MVP.
	•	Independent modules with their own data sources and processing logic.
	•	In future versions, cross-module data integration will be possible via new tables and LEFT JOIN SQL queries.

3. System Architecture & Design

Modular Architecture:
	•	Each module is responsible for its own set of functionalities and metrics (e.g., Business Report handles sales-related data and metrics).
	•	Mixins: Shared functionalities, such as category-aware filtering, are implemented using mixins, ensuring reusability without code duplication.
	•	Data Flow: Data flows from SQL queries to the respective module’s processing engine, which calculates metrics and generates reports.

Key Components:
	•	Analytics Engine: The backbone of the system, responsible for calculating metrics and generating reports.
	•	Base Models and Mixins: Common functionalities for filtering and calculations are handled by shared mixins and base models, making the system scalable.
	•	Modular Components: Each module (Business, Inventory) will extend the base analytics engine and define specific metric calculations.

4. MVP Development Plan

Step 1: Initial Setup and Configuration
	•	Set up the database schema: Create tables for business, inventory, returns, and other necessary modules.
	•	Define the basic data models: Establish models for each report type, such as BusinessReport, InventoryReport.
	•	Implement SQL queries to support filtering by date, category, and ASIN.

Step 2: Develop Core Features
	1.	Filtering and Query System:
	•	Build the filtering system based on the provided criteria (date range, category, ASIN).
	•	Implement SQL-based queries to extract data from the database.
	2.	Metric Calculation:
	•	Define key metrics for each module (e.g., Revenue, Conversion Rate).
	•	Implement metric calculation functions using a modular structure (e.g., BusinessAnalytics, InventoryAnalytics).
	3.	Report Generation:
	•	Develop a basic reporting system to display calculated metrics.
	•	Create simple graphs (e.g., line graphs for revenue trends).

Step 3: Testing & Validation
	•	Conduct unit tests for core functionalities like metric calculations and filtering.
	•	Implement integration tests to ensure the components work well together.
	•	Perform end-to-end tests to verify user flows like logging in, applying filters, and viewing reports.

5. Technical Specifications

Database Design
	•	Modular Data Structure:
	•	Business, Inventory, Returns, and other relevant tables are kept separate for modularity.
	•	No inter-module data sharing in the MVP; modules operate independently.
	•	Future data integration can be achieved using LEFT JOINs for combining data across modules.

Metric Calculation Framework
	•	Per-Module Calculation:
	•	Each module (Business, Inventory, etc.) is responsible for its own metric calculations.
	•	Use of mixins to handle shared functionalities like category-aware filtering.

Testing Strategy
	•	Unit Testing:
	•	Test individual metric calculations (e.g., Revenue, Conversion Rate).
	•	Test SQL queries to ensure correct data retrieval.
	•	Integration Testing:
	•	Ensure proper integration of filtering and data retrieval logic with the database.
	•	Validate if metrics are calculated and reported correctly.
	•	End-to-End Testing:
	•	Verify user interactions: login, filter application, and report generation.

Modular Architecture
	•	Each module has a clear responsibility:
	•	Business Analytics: Handles business-related metrics and reports.
	•	Inventory Analytics: Deals with inventory-related metrics and reports.
	•	Modules operate independently, and data sharing is only done when necessary (future feature).

6. Milestones and Timeline
	1.	Phase 1: MVP Setup
	•	Set up database schema and models (1 week)
	•	Implement basic filtering system and data retrieval (2 weeks)
	•	Define and implement key metrics for Business and Inventory modules (2 weeks)
	2.	Phase 2: Core Features
	•	Develop metric calculation logic and reporting system (2 weeks)
	•	Integrate simple graphs for reporting (1 week)
	3.	Phase 3: Testing & Finalization
	•	Conduct unit tests, integration tests, and end-to-end tests (2 weeks)
	•	Performance testing and optimizations if necessary (1 week)

7. Future Work and Features

Post-MVP Features:
	•	Advanced Analytics: Forecasting, trend analysis, and custom user reports.
	•	User Interaction: More interactive UI elements for deeper engagement.
	•	AI-powered Insights: Machine learning models to predict trends and recommend actions.

Scalability Considerations:
	•	As the project grows, modular components will allow easy expansion with new features.
	•	Performance optimizations will be prioritized once the MVP is stable.

8. Conclusion

This plan ensures that the MVP is developed in a modular and scalable manner, focusing on core functionalities first. The architecture supports future growth, enabling new features to be added as needed. By following this structured approach, the tool can deliver the essential analytics capabilities to Amazon sellers with a focus on ease of use, reliability, and performance.
