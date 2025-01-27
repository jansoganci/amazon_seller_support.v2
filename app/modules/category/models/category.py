"""Basit kategori modeli."""

from datetime import datetime
from app.extensions import db

class Category(db.Model):
    """Kategori tablosu."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parent = db.relationship('Category', remote_side=[id], backref='alt_kategoriler')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class ASINKategori(db.Model):
    """ASIN-Kategori eşleştirme tablosu."""
    __tablename__ = 'asin_kategoriler'
    
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(10), unique=True, nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    kategori = db.relationship('Category', backref='asinler')
    
    def __repr__(self):
        return f'<ASINKategori {self.asin}>'