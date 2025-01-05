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
                    revenue=row['revenue']
                ).first()
                if existing:
                    continue
                    
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
                    clicks=row['clicks']
                ).first()
                if existing:
                    continue
                    
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
                    return_count=row['return_count']
                ).first()
                if existing:
                    continue
                    
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
                    units_total=row['units_total']
                ).first()
                if existing:
                    continue
                    
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
        return False, str(e)

@bp.route('/csv/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """CSV dosyası yükleme sayfası"""
    if request.method == 'POST':
        # Dosya kontrolü
        if 'file' not in request.files:
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        report_type = request.form.get('report_type')
        
        # Temel kontroller
        if file.filename == '':
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
            
        if not report_type:
            flash('Lütfen rapor tipini seçin', 'error')
            return redirect(request.url)
            
        if not file.filename.lower().endswith('.csv'):
            flash('Sadece CSV dosyaları kabul edilmektedir', 'error')
            return redirect(request.url)
        
        try:
            # CSV doğrulama
            is_valid, error_message, metadata = CSVValidator.validate_csv(file, report_type)
            
            if not is_valid:
                flash(error_message, 'error')
                return redirect(request.url)
            
            # Dosyayı kaydet
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Dosya zaten var mı kontrol et
            if os.path.exists(file_path):
                flash('Bu dosya zaten yüklenmiş', 'error')
                return redirect(request.url)
                
            file.seek(0)
            file.save(file_path)
            
            # Verileri ilgili tabloya kaydet
            success, error = save_report_data(metadata['transformed_data'], report_type)
            if not success:
                # Dosyayı sil
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash(error, 'error')
                return redirect(request.url)
            
            # CSV dosyasını kaydet
            csv_file = CSVFile(
                filename=filename,
                file_path=file_path,
                file_type=report_type,
                user_id=current_user.id,
                row_count=metadata.get('row_count', 0),
                column_count=metadata.get('column_count', 0)
            )
            db.session.add(csv_file)
            db.session.commit()
            
            flash('CSV dosyası başarıyla yüklendi', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            logger.error(f"Dosya yükleme hatası: {str(e)}", exc_info=True)
            flash(f'Beklenmeyen bir hata oluştu', 'error')
            return redirect(request.url)
    
    return render_template('csv/upload.html', report_types=CSVValidator.REQUIRED_COLUMNS.keys())
