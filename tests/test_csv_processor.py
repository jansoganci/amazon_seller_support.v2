import os
import pytest
from app.utils.csv_processor import CSVProcessor
from app.models.reports import (
    StoreReport, BusinessReport, InventoryReport,
    AdvertisingReport, ReturnReport
)

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

def test_validate_csv_file_exists():
    processor = CSVProcessor()
    with pytest.raises(FileNotFoundError):
        processor.validate_csv("non_existent.csv", "business")

def test_validate_csv_invalid_type():
    processor = CSVProcessor()
    with pytest.raises(ValueError, match="Invalid report type"):
        processor.validate_csv(
            os.path.join(TEST_DATA_DIR, "business_report.csv"),
            "invalid_type"
        )

def test_validate_business_report():
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "business_report.csv")
    assert processor.validate_csv(file_path, "business") == True

def test_validate_inventory_report():
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "inventory_report.csv")
    assert processor.validate_csv(file_path, "inventory") == True

def test_validate_advertising_report():
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "advertising_report.csv")
    assert processor.validate_csv(file_path, "advertising") == True

def test_validate_return_report():
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "return_report.csv")
    assert processor.validate_csv(file_path, "return") == True

def test_import_business_report(app):
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "business_report.csv")
    reports = processor.import_data(file_path, "business")
    
    assert len(reports) == 3
    report = reports[0]
    assert isinstance(report, BusinessReport)
    assert report.store_id == 1
    assert report.asin == "B001TEST1"
    assert report.units_sold == 100
    assert float(report.revenue) == 1000.50

def test_import_inventory_report(app):
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "inventory_report.csv")
    reports = processor.import_data(file_path, "inventory")
    
    assert len(reports) == 3
    report = reports[0]
    assert isinstance(report, InventoryReport)
    assert report.store_id == 1
    assert report.asin == "B001TEST1"
    assert report.units_available == 100
    assert report.units_inbound == 50

def test_import_advertising_report(app):
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "advertising_report.csv")
    reports = processor.import_data(file_path, "advertising")
    
    assert len(reports) == 3
    report = reports[0]
    assert isinstance(report, AdvertisingReport)
    assert report.store_id == 1
    assert report.campaign_name == "Campaign 1"
    assert report.impressions == 10000
    assert float(report.cost) == 250.50

def test_import_return_report(app):
    processor = CSVProcessor()
    file_path = os.path.join(TEST_DATA_DIR, "return_report.csv")
    reports = processor.import_data(file_path, "return")
    
    assert len(reports) == 3
    report = reports[0]
    assert isinstance(report, ReturnReport)
    assert report.store_id == 1
    assert report.asin == "B001TEST1"
    assert report.return_count == 5
    assert float(report.return_rate) == 0.05
    assert report.return_reason == "Size issue"

def test_export_business_report(app):
    # Önce veriyi import et
    processor = CSVProcessor()
    import_file = os.path.join(TEST_DATA_DIR, "business_report.csv")
    processor.import_data(import_file, "business")
    
    # Şimdi export et
    export_file = os.path.join(TEST_DATA_DIR, "business_report_export.csv")
    success = processor.export_data(1, "business", export_file)
    assert success == True
    
    # Export edilen dosyayı kontrol et
    assert os.path.exists(export_file)
    
    # Temizlik
    if os.path.exists(export_file):
        os.remove(export_file)

def test_export_inventory_report(app):
    processor = CSVProcessor()
    import_file = os.path.join(TEST_DATA_DIR, "inventory_report.csv")
    processor.import_data(import_file, "inventory")
    
    export_file = os.path.join(TEST_DATA_DIR, "inventory_report_export.csv")
    success = processor.export_data(1, "inventory", export_file)
    assert success == True
    
    assert os.path.exists(export_file)
    
    if os.path.exists(export_file):
        os.remove(export_file)

def test_export_advertising_report(app):
    processor = CSVProcessor()
    import_file = os.path.join(TEST_DATA_DIR, "advertising_report.csv")
    processor.import_data(import_file, "advertising")
    
    export_file = os.path.join(TEST_DATA_DIR, "advertising_report_export.csv")
    success = processor.export_data(1, "advertising", export_file)
    assert success == True
    
    assert os.path.exists(export_file)
    
    if os.path.exists(export_file):
        os.remove(export_file)

def test_export_return_report(app):
    processor = CSVProcessor()
    import_file = os.path.join(TEST_DATA_DIR, "return_report.csv")
    processor.import_data(import_file, "return")
    
    export_file = os.path.join(TEST_DATA_DIR, "return_report_export.csv")
    success = processor.export_data(1, "return", export_file)
    assert success == True
    
    assert os.path.exists(export_file)
    
    if os.path.exists(export_file):
        os.remove(export_file)
