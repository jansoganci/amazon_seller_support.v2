import os
import pytest
from flask import url_for
from flask_login import login_user
from app import db
from app.models.store import Store
from app.models.reports import BusinessReport, AdvertisingReport, ReturnReport, InventoryReport
from app.services.csv_validator import CSVValidator
from io import BytesIO
import pandas as pd

@pytest.fixture
def test_data_path():
    return os.path.join(os.path.dirname(__file__), 'test_data')

@pytest.fixture
def sample_user(app, client):
    # Test kullanıcısı oluştur
    from app.models.user import User
    user = User(name='Test User', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # Flask-Login ile kullanıcı girişi yap
    with client.session_transaction() as sess:
        sess['_user_id'] = user.id
        sess['_fresh'] = True
    
    return user

@pytest.fixture
def sample_store(sample_user):
    # Test mağazası oluştur
    store = Store(
        id=1,
        name='Test Store',
        region='US',
        user_id=sample_user.id
    )
    db.session.add(store)
    db.session.commit()
    return store

class TestCSVUpload:
    def test_upload_page_access(self, client, sample_user):
        """CSV yükleme sayfasına erişim testi"""
        response = client.get('/csv/upload')
        assert response.status_code == 200
        assert b'CSV' in response.data

    def test_upload_without_file(self, client, sample_user):
        """Dosya olmadan yükleme denemesi"""
        response = client.post('/csv/upload', data={
            'report_type': 'business_report'
        }, follow_redirects=True)
        assert b'Dosya se\xc3\xa7ilmedi' in response.data

    def test_upload_invalid_file_type(self, client, sample_user):
        """Geçersiz dosya tipi yükleme denemesi"""
        data = {
            'file': (BytesIO(b'invalid file content'), 'test.txt'),
            'report_type': 'business_report'
        }
        response = client.post('/csv/upload', data=data, follow_redirects=True)
        assert b'Sadece CSV dosyalar\xc4\xb1 kabul edilmektedir' in response.data

    def test_upload_business_report(self, client, sample_user, sample_store, test_data_path):
        """Business report yükleme testi"""
        with open(os.path.join(test_data_path, 'business_report_example.csv'), 'rb') as f:
            data = {
                'file': (f, 'business_report.csv'),
                'report_type': 'business_report'
            }
            response = client.post('/csv/upload', data=data, follow_redirects=True)
            assert b'CSV dosyas\xc4\xb1 ba\xc5\x9far\xc4\xb1yla y\xc3\xbcklendi' in response.data
            
            # Verilerin kaydedildiğini kontrol et
            reports = BusinessReport.query.all()
            assert len(reports) > 0
            
            # İlk raporu kontrol et
            report = reports[0]
            assert report.store_id == sample_store.id
            assert isinstance(report.units_sold, int)
            assert isinstance(report.revenue, (float, int))
            assert isinstance(report.conversion_rate, float)

    def test_upload_advertising_report(self, client, sample_user, sample_store, test_data_path):
        """Advertising report yükleme testi"""
        with open(os.path.join(test_data_path, 'advertising_report_example.csv'), 'rb') as f:
            data = {
                'file': (f, 'advertising_report.csv'),
                'report_type': 'advertising_report'
            }
            response = client.post('/csv/upload', data=data, follow_redirects=True)
            assert b'CSV dosyas\xc4\xb1 ba\xc5\x9far\xc4\xb1yla y\xc3\xbcklendi' in response.data
            
            # Verilerin kaydedildiğini kontrol et
            reports = AdvertisingReport.query.all()
            assert len(reports) > 0
            
            # İlk raporu kontrol et
            report = reports[0]
            assert report.store_id == sample_store.id
            assert isinstance(report.impressions, int)
            assert isinstance(report.clicks, int)
            assert isinstance(report.cost, (float, int))
            assert isinstance(report.acos, float)

    def test_upload_return_report(self, client, sample_user, sample_store, test_data_path):
        """Return report yükleme testi"""
        with open(os.path.join(test_data_path, 'return_report_example.csv'), 'rb') as f:
            data = {
                'file': (f, 'return_report.csv'),
                'report_type': 'return_report'
            }
            response = client.post('/csv/upload', data=data, follow_redirects=True)
            assert b'CSV dosyas\xc4\xb1 ba\xc5\x9far\xc4\xb1yla y\xc3\xbcklendi' in response.data
            
            # Verilerin kaydedildiğini kontrol et
            reports = ReturnReport.query.all()
            assert len(reports) > 0
            
            # İlk raporu kontrol et
            report = reports[0]
            assert report.store_id == sample_store.id
            assert isinstance(report.return_count, int)
            assert isinstance(report.total_units_sold, int)
            assert isinstance(report.return_rate, float)

    def test_upload_inventory_report(self, client, sample_user, sample_store, test_data_path):
        """Inventory report yükleme testi"""
        with open(os.path.join(test_data_path, 'inventory_report_example.csv'), 'rb') as f:
            data = {
                'file': (f, 'inventory_report.csv'),
                'report_type': 'inventory_report'
            }
            response = client.post('/csv/upload', data=data, follow_redirects=True)
            assert b'CSV dosyas\xc4\xb1 ba\xc5\x9far\xc4\xb1yla y\xc3\xbcklendi' in response.data
            
            # Verilerin kaydedildiğini kontrol et
            reports = InventoryReport.query.all()
            assert len(reports) > 0
            
            # İlk raporu kontrol et
            report = reports[0]
            assert report.store_id == sample_store.id
            assert isinstance(report.units_available, int)
            assert isinstance(report.units_total, int)
            assert isinstance(report.reorder_required, bool)

    def test_invalid_store_id(self, client, sample_user, test_data_path):
        """Geçersiz store_id ile yükleme denemesi"""
        # Önce geçerli bir store oluştur
        store = Store(id=999, name='Test Store', region='US', user_id=sample_user.id)
        db.session.add(store)
        db.session.commit()
        
        # CSV içeriğini oluştur
        csv_content = "store_id,store_name,asin,title,units_sold,revenue,returns,conversion_rate,page_views,sessions\n"
        csv_content += "9999,Invalid Store,B001,Test Product,10,100.50,1,0.05,200,1000"  # Geçersiz store_id
        
        data = {
            'file': (BytesIO(csv_content.encode()), 'business_report.csv'),
            'report_type': 'business_report'
        }
        response = client.post('/csv/upload', data=data, follow_redirects=True)
        assert b'Baz\xc4\xb1 ma\xc4\x9fazalar sistemde bulunamad\xc4\xb1' in response.data

    def test_invalid_numeric_values(self, client, sample_user, sample_store):
        """Geçersiz sayısal değerlerle yükleme denemesi"""
        csv_content = "store_id,store_name,asin,title,units_sold,revenue,returns,conversion_rate,page_views,sessions\n"
        csv_content += f"{sample_store.id},{sample_store.name},B001,Test Product,abc,def,ghi,jkl,mno,pqr"  # Geçersiz sayısal değerler
        
        data = {
            'file': (BytesIO(csv_content.encode()), 'business_report.csv'),
            'report_type': 'business_report'
        }
        response = client.post('/csv/upload', data=data, follow_redirects=True)
        assert b'Ge\xc3\xa7ersiz say\xc4\xb1sal de\xc4\x9fer' in response.data

    def test_missing_required_columns(self, client, sample_user):
        """Eksik zorunlu sütunlarla yükleme denemesi"""
        csv_content = "store_id,store_name,asin,title\n1,Test Store,B001,Test Product"  # Eksik sütunlar
        
        data = {
            'file': (BytesIO(csv_content.encode()), 'business_report.csv'),
            'report_type': 'business_report'
        }
        response = client.post('/csv/upload', data=data, follow_redirects=True)
        assert b'Eksik zorunlu s\xc3\xbctunlar' in response.data

    def test_empty_csv(self, client, sample_user):
        """Boş CSV dosyası yükleme denemesi"""
        data = {
            'file': (BytesIO(b''), 'empty.csv'),
            'report_type': 'business_report'
        }
        response = client.post('/csv/upload', data=data, follow_redirects=True)
        assert b'CSV dosyas\xc4\xb1 bo\xc5\x9f' in response.data

    def test_duplicate_upload(self, client, sample_user, sample_store, test_data_path):
        """Aynı dosyanın tekrar yüklenmesi testi"""
        # İlk yükleme
        with open(os.path.join(test_data_path, 'business_report_example.csv'), 'rb') as f:
            data = {
                'file': (f, 'business_report.csv'),
                'report_type': 'business_report'
            }
            client.post('/csv/upload', data=data, follow_redirects=True)
        
        # Aynı dosyayı tekrar yükle
        with open(os.path.join(test_data_path, 'business_report_example.csv'), 'rb') as f:
            data = {
                'file': (f, 'business_report.csv'),
                'report_type': 'business_report'
            }
            response = client.post('/csv/upload', data=data, follow_redirects=True)
            assert b'Bu dosya zaten y\xc3\xbcklenmi\xc5\x9f' in response.data
            
            # Verilerin duplike olmadığını kontrol et
            initial_count = BusinessReport.query.count()
            assert initial_count > 0
            
            # Tekrar yüklemeden sonra sayının değişmediğini kontrol et
            final_count = BusinessReport.query.count()
            assert final_count == initial_count  # Duplike kayıtlara izin verilmiyor
