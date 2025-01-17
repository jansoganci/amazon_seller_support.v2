# AMAZON SELLER CSV ANALYZER

## Overview
A powerful analytics platform for Amazon sellers to process CSV reports and gain valuable insights about their business performance.

## Features
- CSV file processing (Business Reports, Inventory Reports, etc.)
- Sales and inventory analytics
- Performance dashboards
- Multi-store support
- Data visualization
- Seasonal Analytics Dashboard
  - Monthly/Quarterly/Weekly trend analysis
  - Peak period detection
  - Special period analysis (Black Friday, Christmas, etc.)
- CSV Report Upload
  - Support for multiple report types
  - Progress tracking
  - Upload history
  - Validation and error handling

## MVP Timeline (2 Weeks)
### Week 1: Analytics Engine
- Basic sales trend analysis
- Inventory status monitoring
- Data filtering capabilities

### Week 2: Dashboard
- Metric cards implementation
- Basic charts (sales trends, inventory status)
- Responsive design improvements

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/amazon_seller_support.git
cd amazon_seller_support

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Run the application
flask run
```

## Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_csv_processor.py

# Run with coverage report
pytest --cov=app tests/
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Project Structure
```
amazon_seller_support/
├── app/                    # Application package
│   ├── models/            # Database models
│   ├── routes/            # Route handlers
│   ├── utils/             # Utility functions
│   ├── templates/         # Jinja2 templates
│   └── static/            # Static files
├── docs/                  # Documentation
├── tests/                 # Test files
├── migrations/            # Database migrations
└── instance/             # Instance-specific files
```

## Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS, Chart.js
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Testing**: Pytest
- **Documentation**: Markdown
- **Version Control**: Git

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Flask documentation
- Tailwind CSS
- Chart.js

## TEKNOLOJİLER
- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS
- **Template Engine**: Jinja2
- **Veritabanı**: SQLite
- **Dosya İşlemleri**: Flask request.files
- **Loglama**: Python logging modülü
- **Kimlik Doğrulama**: Flask-Login
- **Versiyon Kontrolü**: Git + GitHub

## DOSYA YAPISI

```
amazon_seller_support.v1/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── store.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── analytics.py
│   ├── templates/
│   │   ├── analytics/
│   │   │   ├── dashboard.html
│   │   │   ├── advertisement_report.html
│   │   │   └── revenue_trends.html
│   │   ├── components/
│   │   │   └── sidebar.html
│   │   ├── settings/
│   │   │   ├── settings.html
│   │   │   ├── stores.html
│   │   │   └── create_store.html
│   │   └── base_tailwind.html
│   └── utils/
│       ├── __init__.py
│       ├── analytics_engine.py
│       └── constants.py
├── docs/
│   ├── api.md
│   ├── technical.md
│   └── user_guide.md
├── instance/
│   └── app.db
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_analytics.py
├── .gitignore
├── ai_guidelines.md
├── analytics_progress.md
├── progress.md
├── readme.md
└── requirements.txt
```

## KURULUM

1. **Repo Kopyalama**
   - `git clone <REPO_URL>`

2. **Python Sanal Ortam Oluşturma ve Aktivasyon**
   - `python -m venv venv`
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. **Bağımlılıkların Kurulumu**
   - `pip install -r requirements.txt`

4. **Veritabanı Oluşturma**
   - `flask db init`
   - `flask db migrate`
   - `flask db upgrade`

5. **Uygulamayı Çalıştırma**
   - `flask run`
   - `http://localhost:5000` adresini kullan

## ÖZELLİKLER

### 1. CSV Dosyası Yükleme (MVP)
- Flask'in `request.files` özelliği ile dosya yükleme işlemini gerçekleştiririm
- Zorunlu sütunlar (ASIN, Sales, ConversionRate vb.) sistemde tanımlıdır
- Eksik veya hatalı sütun varsa flash mesajı ile kullanıcıyı bilgilendiririm
- Başarılı yüklemede kullanıcıya onay mesajı gösteririm

### 2. Dashboard
- Jinja2 template engine ile dinamik içerik sunarım
- Tailwind CSS ile modern ve responsive tasarım
- Satış, stok ve reklam metrikleri için Chart.js entegrasyonu
- Kullanıcı dostu navigasyon ve veri görselleştirme

### 3. Shipment Planner
- SQLite veritabanında satış verilerini saklarım
- Python ile öneri algoritmasını işletirim
- Jinja2 template ile sonuçları görselleştiririm
- AJAX ile anlık güncelleme sağlarım

### 4. Kimlik Doğrulama
- Flask-Login ile kullanıcı yönetimi
- Güvenli parola hash'leme
- Oturum yönetimi ve güvenlik kontrolleri
- Kullanıcıya özel dashboard görünümü

## LOG YÖNETİMİ
- Python'un logging modülü ile log yönetimi
- Hata ve işlem kayıtlarını dosyaya yazma
- Farklı log seviyeleri (INFO, ERROR, DEBUG)
- Yapılandırılabilir log formatı

## TEST SENARYOLARI
1. **CSV Yükleme**
   - Doğru format kontrolü
   - Hata mesajları kontrolü
   - Dosya kaydetme işlemi
2. **Shipment Planner**
   - Algoritma çıktı kontrolü
   - Veri güncelleme işlemleri
3. **Auth**
   - Kayıt ve giriş işlemleri
   - Oturum kontrolü
   - Güvenlik testleri
