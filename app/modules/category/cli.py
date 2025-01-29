"""Kategori CLI komutları."""

import click
from flask.cli import with_appcontext
import pandas as pd
from app.modules.category.services.category_service import CategoryService

@click.group()
def kategori():
    """Kategori komutları."""
    pass

@kategori.command('kategori-yukle')
@click.argument('csv_file')
@with_appcontext
def kategori_yukle(csv_file: str):
    """CSV'den kategori yükle.
    
    Args:
        csv_file: Path to CSV file with mappings.
    """
    try:
        df = pd.read_csv(csv_file)
        service = CategoryService()
        
        # First create any missing categories
        unique_categories = df[['category']].drop_duplicates()
        for _, row in unique_categories.iterrows():
            try:
                service.create_category(
                    name=row['category'].replace('_', ' ').title(),
                    code=row['category']
                )
            except ValueError:
                # Category already exists
                pass
                
        # Now create ASIN mappings
        mappings = []
        for _, row in df.iterrows():
            mappings.append({
                'asin': row['asin'],
                'category_code': row['category'],
                'title': row.get('title')
            })
            
        results = service.bulk_assign_categories(mappings)
        click.echo(f'Yükleme başarılı: {len(results)} mappings')
        
    except Exception as e:
        click.echo(f'Hata: {str(e)}', err=True)
