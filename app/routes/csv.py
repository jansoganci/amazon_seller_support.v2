from flask import Blueprint, flash, redirect, url_for, render_template, request, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from app import db
from app.models.store import Store
from app.models.csv_file import CSVFile
from app.models.reports import BusinessReport, AdvertisingReport, ReturnReport, InventoryReport
from app.services.csv_validator import CSVValidator
import logging
import pandas as pd

# Logging yapılandırması
logger = logging.getLogger(__name__)

bp = Blueprint('csv', __name__)

def save_report_data(df, report_type):
    """CSV verilerini ilgili rapor tablosuna kaydeder"""
    try:
        for _, row in df.iterrows():
            if report_type == 'store':
                # Mağaza var mı kontrol et
                store = Store.query.filter_by(id=row['store_id']).first()
                if store:
                    # Mağaza varsa güncelle
                    store.name = row['store_name']
                    store.region = row.get('store_region')  # Opsiyonel alan
                else:
                    # Mağaza yoksa yeni ekle
                    store = Store(
                        id=row['store_id'],
                        name=row['store_name'],
                        region=row.get('store_region'),
                        user_id=current_user.id
                    )
                    db.session.add(store)

            elif report_type == 'business_report':
                # Duplike kontrolü
                existing = BusinessReport.query.filter_by(
                    store_id=row['store_id'],
                    asin=row['asin'],
                    units_sold=row['units_sold'],
                    revenue=row['revenue'],
                    returns=row['returns'],
                    conversion_rate=row['conversion_rate'],
                    page_views=row['page_views'],
                    sessions=row['sessions']
                ).first()
                if existing:
                    return False, 'Bu rapor zaten yüklenmiş'
                    
                report = BusinessReport(
                    store_id=row['store_id'],
                    asin=row['asin'],
                    title=row['title'],
                    units_sold=row['units_sold'],
                    revenue=row['revenue'],
                    returns=row['returns'],
                    conversion_rate=row['conversion_rate'],
                    page_views=row['page_views'],
                    sessions=row['sessions']
                )
                db.session.add(report)

            elif report_type == 'advertising_report':
                # Duplike kontrolü
                existing = AdvertisingReport.query.filter_by(
                    store_id=row['store_id'],
                    campaign_name=row['campaign_name'],
                    impressions=row['impressions'],
                    clicks=row['clicks'],
                    cost=row['cost'],
                    sales=row['sales'],
                    acos=row['acos'],
                    roi=row['roi']
                ).first()
                if existing:
                    return False, 'Bu rapor zaten yüklenmiş'
                    
                report = AdvertisingReport(
                    store_id=row['store_id'],
                    campaign_name=row['campaign_name'],
                    impressions=row['impressions'],
                    clicks=row['clicks'],
                    cost=row['cost'],
                    sales=row['sales'],
                    acos=row['acos'],
                    roi=row['roi']
                )
                db.session.add(report)

            elif report_type == 'return_report':
                # Duplike kontrolü
                existing = ReturnReport.query.filter_by(
                    store_id=row['store_id'],
                    asin=row['asin'],
                    return_reason=row['return_reason'],
                    return_count=row['return_count'],
                    total_units_sold=row['total_units_sold'],
                    return_rate=row['return_rate']
                ).first()
                if existing:
                    return False, 'Bu rapor zaten yüklenmiş'
                    
                report = ReturnReport(
                    store_id=row['store_id'],
                    asin=row['asin'],
                    title=row['title'],
                    return_reason=row['return_reason'],
                    return_count=row['return_count'],
                    total_units_sold=row['total_units_sold'],
                    return_rate=row['return_rate'],
                    customer_feedback=row.get('customer_feedback')  # Opsiyonel alan
                )
                db.session.add(report)

            elif report_type == 'inventory_report':
                # Duplike kontrolü
                existing = InventoryReport.query.filter_by(
                    store_id=row['store_id'],
                    asin=row['asin'],
                    units_available=row['units_available'],
                    units_inbound=row['units_inbound'],
                    units_reserved=row['units_reserved'],
                    units_total=row['units_total']
                ).first()
                if existing:
                    return False, 'Bu rapor zaten yüklenmiş'
                    
                report = InventoryReport(
                    store_id=row['store_id'],
                    asin=row['asin'],
                    title=row['title'],
                    units_available=row['units_available'],
                    units_inbound=row['units_inbound'],
                    units_reserved=row['units_reserved'],
                    units_total=row['units_total'],
                    reorder_required=row['reorder_required']
                )
                db.session.add(report)

        db.session.commit()
        return True, None
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Veri kaydetme hatası: {str(e)}", exc_info=True)
        return False, f'Veri kaydetme hatası: {str(e)}'

@bp.route('/csv/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """CSV dosyası yükleme sayfası"""
    if request.method == 'POST':
        try:
            # Dosya kontrolü
            if 'file' not in request.files:
                flash('Dosya seçilmedi', 'danger')
                return redirect(request.url)
                
            file = request.files['file']
            report_type = request.form.get('report_type')
            
            # Temel kontroller
            if file.filename == '':
                flash('Dosya seçilmedi', 'danger')
                return redirect(request.url)
                
            if not report_type:
                flash('Lütfen rapor tipini seçin', 'danger')
                return redirect(request.url)
                
            if not file.filename.lower().endswith('.csv'):
                flash('Sadece CSV dosyaları kabul edilmektedir', 'danger')
                return redirect(request.url)
            
            # CSV doğrulama
            validator = CSVValidator()
            logger.info(f"CSV doğrulama başlıyor: {file.filename}, tip: {report_type}")
            is_valid, error_message, metadata = validator.validate_csv(file, report_type)
            logger.info(f"CSV doğrulama sonucu: valid={is_valid}, error={error_message}, metadata={metadata}")
            
            if not is_valid:
                flash(f'CSV doğrulama hatası: {error_message}', 'danger')
                return redirect(request.url)
            
            # Veri kaydetme
            try:
                # CSV verilerini kaydet
                logger.info("CSV verileri kaydediliyor...")
                save_report_data(metadata['transformed_data'], report_type)
                logger.info("CSV verileri başarıyla kaydedildi")
                
                # CSV dosya kaydını oluştur
                store_id = metadata['store_ids'][0] if metadata['store_ids'] else None
                logger.info(f"Store ID: {store_id}")
                
                if not store_id:
                    flash('Store ID bulunamadı', 'danger')
                    return redirect(request.url)
                    
                csv_file = CSVFile(
                    filename=secure_filename(file.filename),
                    file_type=report_type,
                    status='success',
                    user_id=current_user.id,
                    store_id=store_id,
                    row_count=metadata['row_count']
                )
                logger.info(f"CSV dosya kaydı oluşturuluyor: {csv_file}")
                db.session.add(csv_file)
                db.session.commit()
                logger.info("CSV dosya kaydı başarıyla oluşturuldu")
                
                flash(f'{file.filename} başarıyla yüklendi ve işlendi', 'success')
            except Exception as e:
                logger.error(f"Veri kaydetme hatası: {str(e)}", exc_info=True)
                # Hata durumunda CSV dosya kaydını oluştur
                store_id = metadata['store_ids'][0] if metadata['store_ids'] else None
                if store_id:
                    csv_file = CSVFile(
                        filename=secure_filename(file.filename),
                        file_type=report_type,
                        status='error',
                        error_message=str(e),
                        user_id=current_user.id,
                        store_id=store_id,
                        row_count=metadata.get('row_count', 0)
                    )
                    db.session.add(csv_file)
                    db.session.commit()
                
                flash(f'Veri kaydedilirken hata oluştu: {str(e)}', 'danger')
                return redirect(request.url)
                
            return redirect(url_for('csv.upload'))
            
        except pd.errors.EmptyDataError:
            flash('CSV dosyası boş', 'danger')
            return redirect(request.url)
        except pd.errors.ParserError:
            flash('CSV dosyası okunamadı. Lütfen dosya formatını kontrol edin', 'danger')
            return redirect(request.url)
        except Exception as e:
            logger.error(f"CSV yükleme hatası: {str(e)}")
            flash(f'Beklenmeyen bir hata oluştu: {str(e)}', 'danger')
            return redirect(request.url)
    
    # GET request - form sayfasını göster
    report_types = [
        'business_report',
        'inventory_report',
        'advertising_report',
        'return_report'
    ]
    
    # Yükleme geçmişini al
    uploads = CSVFile.query.filter_by(user_id=current_user.id).order_by(CSVFile.upload_date.desc()).all()
    logger.info(f"Yükleme geçmişi: {len(uploads)} kayıt bulundu")
    
    return render_template('csv/upload.html', report_types=report_types, uploads=uploads)
