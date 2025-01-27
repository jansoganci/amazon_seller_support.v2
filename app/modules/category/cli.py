"""Kategori CLI komutları."""

import click
from flask.cli import with_appcontext
import pandas as pd
from app.extensions import db
from app.modules.category.models.category import Category, ASINKategori

@click.group()
def kategori():
    """Kategori komutları."""
    pass

@kategori.command('kategori-yukle')
@click.argument('csv_file')
@with_appcontext
def kategori_yukle(csv_file):
    """CSV'den kategori yükle."""
    try:
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            category = Category.query.filter_by(name=row['category']).first()
            if not category:
                category = Category(name=row['category'])
                db.session.add(category)
                db.session.flush()
            
            mapping = ASINKategori(asin=row['asin'], kategori_id=category.id)
            db.session.add(mapping)
        
        db.session.commit()
        click.echo('Yükleme başarılı')
        
    except Exception as e:
        db.session.rollback()
        click.echo(f'Hata: {str(e)}')
