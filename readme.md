# AMAZON SELLER CSV ANALYZER - MVP

## AMAÇ
- Amazon satıcılarının CSV dosyalarını (Business Reports, Inventory Reports vb.) **manuel düzenleme gerektirmeden** yüklemelerini sağlıyorum.  
- Yüklenen veriler üzerinden **satış, stok, reklam harcaması** gibi temel metrikleri görüntülüyorum ve **shipment planı** oluşturuyorum.  
- Blog/metadata sayfalarını ve çoklu dil desteğini ilerleyen aşamalarda entegre ediyorum.  
- Sistemi **Flask ve Tailwind CSS** kullanarak geliştiriyorum ve modern, bakımı kolay bir yapı hedefliyorum.

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
amazon_seller_support/
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── csv_handler.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── shipment_service.py
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       ├── base.html
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       └── dashboard/
│           ├── index.html
│           ├── upload.html
│           └── shipment.html
├── instance/
│   └── database.sqlite
├── requirements.txt
├── config.py
└── run.py
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
