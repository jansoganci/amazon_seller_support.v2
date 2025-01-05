import unittest
import os
import pandas as pd
import io
from app.services.csv_validator import CSVValidator

class TestCSVValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Test sınıfı başlatıldığında çalışır"""
        cls.base_path = os.path.join(os.path.dirname(__file__), 'test_data')
        
    def get_test_file_path(self, filename):
        """Test dosyasının tam yolunu döndürür"""
        return os.path.join(self.base_path, filename)
    
    def test_business_report_valid(self):
        """Geçerli business report CSV'sini test eder"""
        file_path = self.get_test_file_path('business_report_example.csv')
        with open(file_path, 'rb') as file:
            is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'business_report')
            
        self.assertTrue(is_valid)
        self.assertEqual("CSV dosyası başarıyla doğrulandı", error_message)
        self.assertEqual(metadata['row_count'], 30)
        self.assertEqual(metadata['column_count'], 9)
        
    def test_inventory_report_valid(self):
        """Geçerli inventory report CSV'sini test eder"""
        file_path = self.get_test_file_path('inventory_report_example.csv')
        with open(file_path, 'rb') as file:
            is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'inventory_report')
            
        self.assertTrue(is_valid)
        self.assertEqual("CSV dosyası başarıyla doğrulandı", error_message)
        self.assertEqual(metadata['row_count'], 30)
        self.assertEqual(metadata['column_count'], 8)
        
    def test_advertising_report_valid(self):
        """Geçerli advertising report CSV'sini test eder"""
        file_path = self.get_test_file_path('advertising_report_example.csv')
        with open(file_path, 'rb') as file:
            is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'advertising_report')
            
        self.assertTrue(is_valid)
        self.assertEqual("CSV dosyası başarıyla doğrulandı", error_message)
        self.assertEqual(metadata['row_count'], 30)
        self.assertEqual(metadata['column_count'], 8)
        
    def test_return_report_valid(self):
        """Geçerli return report CSV'sini test eder"""
        file_path = self.get_test_file_path('return_report_example.csv')
        with open(file_path, 'rb') as file:
            is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'return_report')
            
        self.assertTrue(is_valid)
        self.assertEqual("CSV dosyası başarıyla doğrulandı", error_message)
        self.assertEqual(metadata['row_count'], 30)
        self.assertEqual(metadata['column_count'], 8)
    
    def test_missing_required_columns(self):
        """Eksik zorunlu sütunları test eder"""
        # Eksik sütunlu business report oluştur
        df = pd.DataFrame({
            'store_name': ['US Store'],
            'asin': ['B001ABC123'],
            # title sütunu eksik
            'units_sold': [100],
            'revenue': [500.00]
        })
        test_file = self.get_test_file_path('missing_columns.csv')
        df.to_csv(test_file, index=False)
        
        with open(test_file, 'rb') as file:
            is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'business_report')
            
        self.assertFalse(is_valid)
        self.assertTrue("Eksik zorunlu sütunlar" in error_message)
        os.remove(test_file)
    
    def test_invalid_numeric_data(self):
        """Geçersiz sayısal verileri test eder"""
        # Geçersiz sayısal verili inventory report oluştur
        df = pd.DataFrame({
            'store_name': ['US Store'],
            'asin': ['B001ABC123'],
            'title': ['Ergonomic Chair'],
            'units_available': ['invalid'],  # Sayısal olması gereken değer
            'units_inbound': [20],
            'units_reserved': [5],
            'units_total': [35],
            'reorder_required': ['Yes']
        })
        test_file = self.get_test_file_path('invalid_numeric.csv')
        df.to_csv(test_file, index=False)
        
        with open(test_file, 'rb') as file:
            is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'inventory_report')
            
        self.assertFalse(is_valid)
        self.assertTrue("Geçersiz sayısal değer" in error_message)
        os.remove(test_file)
        
    def test_file_with_empty_rows(self):
        """Boş satır içeren dosyayı test eder"""
        # Boş satır içeren CSV oluştur
        csv_content = (
            "store_name,asin,title,units_sold,revenue,returns,conversion_rate,page_views,sessions\n"
            "US Store,B001ABC123,Chair,100,500.00,2,5.0,2000,1500\n"
            ",,,,,,,,\n"  # Tamamen boş satır
            "UK Store,B002XYZ456,Desk,80,400.00,1,4.0,1500,1200\n"
        )
        
        # StringIO kullanarak dosya benzeri nesne oluştur
        file = io.StringIO(csv_content)
        is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'business_report')
        
        self.assertFalse(is_valid)
        self.assertEqual("Boş satır tespit edildi", error_message)
        
    def test_empty_file(self):
        """Boş CSV dosyasını test eder"""
        # Boş CSV oluştur
        csv_content = ""
        file = io.StringIO(csv_content)
        
        is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'business_report')
        
        self.assertFalse(is_valid)
        self.assertEqual("CSV dosyası boş", error_message)

    def test_quoted_csv_content(self):
        """Tırnak içeren CSV içeriğini test eder"""
        # Tırnak içeren CSV içeriği oluştur
        csv_content = '"store_name,asin,title,units_sold,revenue,returns,conversion_rate,page_views,sessions"\n'
        csv_content += '"US Store,B001ABC123,Chair,100,500.00,2,5.0,2000,1500"\n'
        
        # StringIO kullanarak dosya benzeri nesne oluştur
        file = io.StringIO(csv_content)
        is_valid, error_message, metadata = CSVValidator.validate_csv(file, 'business_report')
        
        # Debug için çıktı
        print("Test CSV içeriği:", csv_content)
        print("Doğrulama sonucu:", is_valid, error_message, metadata)
        
        self.assertTrue(is_valid)
        self.assertEqual("CSV dosyası başarıyla doğrulandı", error_message)

if __name__ == '__main__':
    unittest.main()
