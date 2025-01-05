from app import db
from datetime import datetime

class CSVFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # business_report, advertising_report, return_report, inventory_report
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    row_count = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CSVFile {self.filename}>'
