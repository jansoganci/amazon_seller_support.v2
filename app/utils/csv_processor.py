import csv
import os
from typing import Dict, List, Any
from app.models.reports import (
    StoreReport, BusinessReport, InventoryReport,
    AdvertisingReport, ReturnReport
)
from app import db
from datetime import datetime

class CSVProcessor:
    """CSV dosyalarını işlemek ve raporları veritabanına kaydetmek için kullanılan sınıf."""

    REQUIRED_HEADERS = {
        "business": [
            "store_id", "asin", "title", "units_sold", "revenue",
            "returns", "conversion_rate", "page_views", "sessions"
        ],
        "inventory": [
            "store_id", "asin", "title", "units_available",
            "units_inbound", "units_reserved", "reorder_required"
        ],
        "advertising": [
            "store_id", "campaign_name", "impressions", "clicks",
            "cost", "sales", "ACOS", "ROI"
        ],
        "return": [
            "store_id", "asin", "title", "return_reason",
            "return_count", "total_units_sold", "return_rate"
        ]
    }

    def validate_csv(self, file_path: str, report_type: str) -> bool:
        """CSV dosyasını doğrular.

        Args:
            file_path: CSV dosyasının yolu
            report_type: Rapor tipi (business, inventory, advertising, return)

        Returns:
            bool: Doğrulama başarılı ise True

        Raises:
            FileNotFoundError: Dosya bulunamazsa
            ValueError: Rapor tipi geçersizse veya başlıklar eksikse
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        if report_type not in self.REQUIRED_HEADERS:
            raise ValueError(f"Invalid report type: {report_type}")

        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # İlk satır başlıklar
            return self.validate_headers(report_type, headers)

    def validate_headers(self, report_type: str, headers: List[str]) -> bool:
        """CSV başlıklarını doğrular.

        Args:
            report_type: Rapor tipi
            headers: CSV başlıkları

        Returns:
            bool: Başlıklar geçerli ise True

        Raises:
            ValueError: Gerekli başlıklar eksikse
        """
        required = set(self.REQUIRED_HEADERS[report_type])
        current = set(headers)
        missing = required - current
        
        if missing:
            raise ValueError(f"Missing required headers: {missing}")
        
        return True

    def import_data(self, file_path: str, report_type: str) -> List[Any]:
        """CSV dosyasından veriyi içe aktarır.

        Args:
            file_path: CSV dosyasının yolu
            report_type: Rapor tipi

        Returns:
            List[Any]: İçe aktarılan rapor nesneleri listesi
        """
        self.validate_csv(file_path, report_type)
        reports = []

        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                report = self.create_report(report_type, row)
                if report:
                    reports.append(report)
                    db.session.add(report)
            
            db.session.commit()

        return reports

    def create_report(self, report_type: str, data: Dict[str, Any]) -> Any:
        """Rapor nesnesini oluşturur.

        Args:
            report_type: Rapor tipi
            data: Rapor verileri

        Returns:
            Any: Oluşturulan rapor nesnesi
        """
        creators = {
            "business": self.create_business_report,
            "inventory": self.create_inventory_report,
            "advertising": self.create_advertising_report,
            "return": self.create_return_report
        }
        
        creator = creators.get(report_type)
        if creator:
            return creator(data)
        return None

    def create_business_report(self, data: Dict[str, Any]) -> BusinessReport:
        """Business Report nesnesi oluşturur."""
        data['report_period'] = 'Daily'  # Default value
        return BusinessReport(
            store_id=data['store_id'],
            asin=data['asin'],
            title=data['title'],
            units_sold=data['units_sold'],
            revenue=data['revenue'],
            returns=data['returns'],
            conversion_rate=data['conversion_rate'],
            page_views=data['page_views'],
            sessions=data['sessions'],
            report_period=data['report_period']
        )

    def create_inventory_report(self, data: Dict[str, Any]) -> InventoryReport:
        """Inventory Report nesnesi oluşturur."""
        data['units_total'] = int(data['units_available']) + int(data['units_inbound']) + int(data['units_reserved'])
        return InventoryReport(
            store_id=data['store_id'],
            asin=data['asin'],
            title=data['title'],
            units_available=data['units_available'],
            units_inbound=data['units_inbound'],
            units_reserved=data['units_reserved'],
            units_total=data['units_total'],
            reorder_required=data['reorder_required'].lower() == 'true'
        )

    def create_advertising_report(self, data: Dict[str, Any]) -> AdvertisingReport:
        """Advertising Report nesnesi oluşturur."""
        # Default dates if not provided
        current_date = datetime.utcnow().date()
        data['start_date'] = current_date
        data['end_date'] = current_date
        
        return AdvertisingReport(
            store_id=data['store_id'],
            campaign_name=data['campaign_name'],
            impressions=data['impressions'],
            clicks=data['clicks'],
            cost=data['cost'],
            sales=data['sales'],
            acos=data['ACOS'],
            roi=data['ROI'],
            start_date=data['start_date'],
            end_date=data['end_date']
        )

    def create_return_report(self, data: Dict[str, Any]) -> ReturnReport:
        """Return Report nesnesi oluşturur."""
        return ReturnReport(
            store_id=data['store_id'],
            asin=data['asin'],
            title=data['title'],
            return_reason=data['return_reason'],
            return_count=data['return_count'],
            total_units_sold=data['total_units_sold'],
            return_rate=data['return_rate']
        )

    def export_data(self, store_id: int, report_type: str, file_path: str) -> bool:
        """Veritabanından rapor verilerini CSV dosyasına aktarır."""
        try:
            # Report tipine göre modeli seç
            model = self._get_model(report_type)
            if not model:
                return False

            # Store ID'ye göre raporları getir
            reports = model.query.filter_by(store_id=store_id).all()
            if not reports:
                return False

            # CSV başlıklarını al
            headers = self.REQUIRED_HEADERS[report_type]

            # CSV dosyasını oluştur ve yaz
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()

                for report in reports:
                    # Model verilerini dict'e çevir
                    data = report.to_dict()
                    # Sadece CSV başlıklarında olan alanları al
                    row = {k: data[k] for k in headers if k in data}
                    writer.writerow(row)

            return True

        except Exception as e:
            print(f"Export error: {str(e)}")
            return False

    def _get_model(self, report_type: str):
        report_models = {
            "business": BusinessReport,
            "inventory": InventoryReport,
            "advertising": AdvertisingReport,
            "return": ReturnReport
        }

        return report_models.get(report_type)
