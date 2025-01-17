# CSV Entegrasyon Rehberi

Bu rehber, Amazon Seller Support uygulamasına yeni bir CSV rapor tipi eklemek için gereken adımları detaylı olarak açıklar.

## Yeni Rapor Tipi Ekleme Adımları

### 1. Model Tanımlama
- `app/models/reports.py` dosyasında yeni model sınıfını tanımla
- Gerekli sütunları ve veri tiplerini belirle
- Model ilişkilerini tanımla (örn: Store ile ilişki)
- `to_dict()` metodunu implement et

Örnek:
```python
class NewReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # ... diğer sütunlar ...

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # ... diğer alanlar ...
        }
```

### 2. CSV Validator Güncellemesi
`app/services/csv_validator.py` dosyasında aşağıdaki güncellemeleri yap:

1. REQUIRED_COLUMNS'a yeni rapor tipini ekle:
```python
REQUIRED_COLUMNS = {
    'new_report': ['store_id', 'field1', 'field2', ...]
}
```

2. NUMERIC_COLUMNS'a sayısal alanları ekle:
```python
NUMERIC_COLUMNS = {
    'new_report': {
        'numeric_field1': int,
        'numeric_field2': Decimal,
    }
}
```

3. BOOLEAN_COLUMNS'a boolean alanları ekle (varsa):
```python
BOOLEAN_COLUMNS = {
    'new_report': {
        'boolean_field': ['true', 'false', '1', '0', 'yes', 'no']
    }
}
```

### 3. CSV İşleme Mantığı
`app/routes/csv.py` dosyasında `save_report_data` fonksiyonuna yeni rapor tipi için işleme mantığı ekle:

```python
elif report_type == 'new_report':
    # Duplike kontrolü
    existing = NewReport.query.filter_by(
        store_id=row['store_id'],
        field1=row['field1'],
        # ... diğer alanlar ...
    ).first()
    
    if existing:
        return False, 'Bu rapor zaten yüklenmiş'
        
    report = NewReport(
        store_id=row['store_id'],
        field1=row['field1'],
        # ... diğer alanlar ...
    )
    db.session.add(report)
```

### 4. Template Güncellemesi
`app/templates/csv/upload.html` dosyasında rapor tipi seçeneğini ekle:

```html
{% if report_type == 'new_report' %}
    Yeni Rapor Tipi
{% endif %}
```

### 5. Test Dosyaları
1. `tests/test_csv_validator.py` dosyasına yeni test ekle:
```python
def test_new_report_valid(self):
    """Geçerli yeni rapor CSV'sini test eder"""
    file_path = self.get_test_file_path('new_report_example.csv')
    with open(file_path, 'rb') as file:
        is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'new_report')
        
    self.assertTrue(is_valid)
    self.assertEqual("CSV dosyası başarıyla doğrulandı", error_message)
```

2. `tests/test_data` dizinine örnek CSV dosyası ekle:
- `new_report_example.csv`

### 6. Veritabanı Migrasyonu
1. Yeni migration dosyası oluştur:
```bash
flask db migrate -m "Add new report model"
```

2. Migrationı uygula:
```bash
flask db upgrade
```

### 7. Dokümantasyon
1. `docs/technical.md` dosyasına yeni model şemasını ekle
2. `csv_progress.md` dosyasını güncelle
3. Örnek CSV formatını `design_guide.md` dosyasına ekle

## Önemli Noktalar
1. Tüm zorunlu alanların doğru veri tipinde olduğundan emin ol
2. Duplike kontrolleri için doğru alanları seç
3. Test verilerinin gerçekçi olmasına dikkat et
4. Hata mesajlarının kullanıcı dostu olmasını sağla

## Kontrol Listesi
- [ ] Model tanımlandı
- [ ] CSV Validator güncellendi
- [ ] CSV işleme mantığı eklendi
- [ ] Template güncellendi
- [ ] Testler yazıldı
- [ ] Örnek CSV dosyası oluşturuldu
- [ ] Migration yapıldı
- [ ] Dokümantasyon güncellendi 