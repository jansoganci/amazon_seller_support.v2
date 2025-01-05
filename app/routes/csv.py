from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
from app import db
from app.models.csv_file import CSVFile
from app.models.store import Store
import os

bp = Blueprint('csv', __name__)

ALLOWED_EXTENSIONS = {'csv'}
REQUIRED_COLUMNS = {
    'business_report': ['store_name', 'date', 'asin', 'product_name', 'units_sold', 'sales', 'conversion_rate', 'impressions', 'clicks'],
    'advertising_report': ['store_name', 'date', 'campaign_name', 'impressions', 'clicks', 'cost', 'sales', 'acos', 'roas'],
    'return_report': ['store_name', 'date', 'asin', 'product_name', 'return_reason', 'return_rate'],
    'inventory_report': ['store_name', 'date', 'asin', 'product_name', 'quantity', 'restock_level', 'days_of_supply']
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/csv/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        file_type = request.form.get('file_type')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
            
        if not file_type:
            flash('Please select a file type', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # CSV dosyasını oku
                df = pd.read_csv(file)
                
                # Gerekli sütunları kontrol et
                required_cols = REQUIRED_COLUMNS.get(file_type, [])
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    flash(f'Missing required columns: {", ".join(missing_cols)}', 'error')
                    return redirect(request.url)
                
                # Mağaza adlarını kontrol et ve gerekirse oluştur
                store_names = df['store_name'].unique()
                stores_dict = {}
                
                for store_name in store_names:
                    store = Store.query.filter_by(name=store_name, user_id=current_user.id).first()
                    if not store:
                        store = Store(name=store_name, user_id=current_user.id)
                        db.session.add(store)
                        db.session.flush()  # ID'yi almak için flush
                    stores_dict[store_name] = store.id
                
                # CSV dosyasını kaydet
                filename = secure_filename(file.filename)
                csv_file = CSVFile(
                    filename=filename,
                    file_type=file_type,
                    user_id=current_user.id,
                    store_id=stores_dict[store_names[0]],  # İlk mağazayı varsayılan olarak kullan
                    row_count=len(df)
                )
                db.session.add(csv_file)
                db.session.commit()
                
                flash('File uploaded successfully', 'success')
                return redirect(url_for('main.dashboard'))
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
                
        else:
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(request.url)
    
    # GET isteği için mağazaları getir
    stores = Store.query.filter_by(user_id=current_user.id).all()
    return render_template('csv/upload.html', stores=stores)
