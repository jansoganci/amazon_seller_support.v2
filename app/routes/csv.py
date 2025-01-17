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

def save_report_data(df, report_type, user_id):
    """CSV verilerini veritabanına kaydet"""
    try:
        # Store ID kontrolü
        store_ids = df['store_id'].unique()
        logger.info(f"CSV'deki store ID'ler: {store_ids}")
        logger.info(f"Kullanıcı ID: {user_id}")
        
        # Kullanıcının store'larını kontrol et
        user_stores = Store.query.filter_by(user_id=user_id).all()
        logger.info(f"Kullanıcının store'ları:")
        for store in user_stores:
            logger.info(f"Store ID: {store.id}, İsim: {store.name}, User ID: {store.user_id}")
        
        user_store_ids = [store.id for store in user_stores]
        invalid_stores = [str(id) for id in store_ids if id not in user_store_ids]
        
        if invalid_stores:
            error_msg = f"Store ID {', '.join(invalid_stores)} bulunamadı veya erişim izniniz yok. "
            error_msg += f"Sizin store ID'leriniz: {', '.join(map(str, user_store_ids))}"
            logger.error(error_msg)
            return False, error_msg

        # Rapor tipine göre kaydetme işlemi
        if report_type == 'business_report':
            # Önce mevcut kayıtları kontrol et
            for _, row in df.iterrows():
                existing = BusinessReport.query.filter_by(
                    store_id=row['store_id'],
                    date=row['date'],
                    asin=row['asin']
                ).first()
                
                if not existing:
                    report = BusinessReport(
                        store_id=row['store_id'],
                        date=row['date'],
                        sku=row['sku'],
                        asin=row['asin'],
                        title=row['title'],
                        sessions=row['sessions'],
                        units_ordered=row['units_ordered'],
                        ordered_product_sales=row['ordered_product_sales'],
                        total_order_items=row['total_order_items'],
                        conversion_rate=row['conversion_rate']
                    )
                    db.session.add(report)

        elif report_type == 'advertising_report':
            for _, row in df.iterrows():
                report = AdvertisingReport(
                    store_id=row['store_id'],
                    date=row['date'],
                    campaign_name=row['campaign_name'],
                    ad_group_name=row['ad_group_name'],
                    targeting_type=row['targeting_type'],
                    match_type=row['match_type'],
                    search_term=row['search_term'],
                    impressions=row['impressions'],
                    clicks=row['clicks'],
                    ctr=row['ctr'],
                    cpc=row['cpc'],
                    spend=row['spend'],
                    total_sales=row['total_sales'],
                    acos=row['acos'],
                    total_orders=row['total_orders'],
                    total_units=row['total_units'],
                    conversion_rate=row['conversion_rate']
                )
                db.session.add(report)

        elif report_type == 'inventory_report':
            for _, row in df.iterrows():
                report = InventoryReport(
                    store_id=row['store_id'],
                    date=row['date'],
                    sku=row['sku'],
                    asin=row['asin'],
                    product_name=row['product_name'],
                    condition=row['condition'],
                    price=row['price'],
                    mfn_listing_exists=row['mfn_listing_exists'],
                    mfn_fulfillable_quantity=row['mfn_fulfillable_quantity'],
                    afn_listing_exists=row['afn_listing_exists'],
                    afn_warehouse_quantity=row['afn_warehouse_quantity'],
                    afn_fulfillable_quantity=row['afn_fulfillable_quantity'],
                    afn_unsellable_quantity=row['afn_unsellable_quantity'],
                    afn_reserved_quantity=row['afn_reserved_quantity'],
                    afn_total_quantity=row['afn_total_quantity'],
                    per_unit_volume=row['per_unit_volume']
                )
                db.session.add(report)

        elif report_type == 'return_report':
            for _, row in df.iterrows():
                report = ReturnReport(
                    store_id=row['store_id'],
                    return_date=row['return_date'],
                    order_id=row['order_id'],
                    sku=row['sku'],
                    asin=row['asin'],
                    title=row['title'],
                    quantity=row['quantity'],
                    return_reason=row['return_reason'],
                    status=row['status'],
                    refund_amount=row['refund_amount'],
                    return_center=row['return_center'],
                    return_carrier=row['return_carrier'],
                    tracking_number=row['tracking_number']
                )
                db.session.add(report)

        db.session.commit()
        return True, "Veriler başarıyla kaydedildi."

    except Exception as e:
        db.session.rollback()
        logger.error(f"Veri kaydetme hatası: {str(e)}")
        logger.error(f"Kullanıcı ID: {user_id}")
        logger.error(f"Store ID'ler: {store_ids}")
        return False, f"Veri kaydetme hatası: {str(e)}"

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        logger.info(f"Upload sayfası açıldı - User: {current_user.email}")
        logger.info("==================== YENİ UPLOAD İSTEĞİ ====================")
        logger.info(f"Kullanıcı: {current_user.email} (ID: {current_user.id})")
        logger.info(f"Request Data: {request.form}")
        logger.info(f"Files: {request.files}")

        # Rapor tipi kontrolü
        report_type = request.form.get('report_type')
        if not report_type:
            flash('Lütfen bir rapor tipi seçin.', 'error')
            return redirect(url_for('analytics.upload_csv'))

        # Dosya kontrolü
        if 'file' not in request.files:
            flash('Dosya seçilmedi. Lütfen bir CSV dosyası seçin.', 'error')
            return redirect(url_for('analytics.upload_csv'))

        file = request.files['file']
        if not file.filename:
            flash('Dosya seçilmedi. Lütfen bir CSV dosyası seçin.', 'error')
            return redirect(url_for('analytics.upload_csv'))

        if not file.filename.endswith('.csv'):
            flash('Sadece CSV dosyaları yüklenebilir.', 'error')
            return redirect(url_for('analytics.upload_csv'))

        logger.info(f"Rapor Tipi: {report_type}")
        logger.info(f"Dosya Adı: {file.filename}")

        # CSV içeriğini logla
        file_content = file.read().decode('utf-8')[:500]  # İlk 500 karakter
        logger.info(f"CSV İçeriği (ilk 500 karakter):\n{file_content}")
        file.seek(0)  # Dosya pointer'ı başa al

        logger.info("CSV doğrulama başlıyor...")
        success, message, metadata = CSVValidator.validate_csv(file, report_type)

        if not success:
            error_message = f"CSV Doğrulama Hatası: {message}"
            logger.error(error_message)
            flash(error_message, 'error')
            return redirect(url_for('analytics.upload_csv'))

        logger.info("CSV doğrulama başarılı!")
        logger.info(f"Metadata: {metadata}")

        logger.info("Veri kaydetme başlıyor...")
        success, message = save_report_data(metadata['transformed_data'], report_type, current_user.id)

        if not success:
            error_message = f"Veri kaydetme hatası: {message}"
            logger.error(error_message)
            flash(error_message, 'error')
            return redirect(url_for('analytics.upload_csv'))

        logger.info(f"Veri kaydetme başarılı: {message}")
        flash('CSV dosyası başarıyla yüklendi ve işlendi.', 'success')
        return redirect(url_for('analytics.upload_csv'))

    return render_template('csv/upload.html', report_types=['business_report', 'advertising_report', 'inventory_report', 'return_report'])
