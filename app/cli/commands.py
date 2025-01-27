"""CLI komutları."""
import os
import click
from flask.cli import with_appcontext
import pandas as pd
from app.extensions import db
from app.modules.category.models.category import Category, ASINKategori
from app.modules.business.services import CategoryService
from sqlalchemy.exc import IntegrityError


@click.group()
def category():
    """Kategori yönetim komutları."""
    pass


@category.command('add')
@click.argument('name')
@click.argument('code')
@with_appcontext
def add_category(name: str, code: str):
    """Yeni bir kategori ekle.
    
    Args:
        name: Kategori adı
        code: Kategori kodu
    """
    try:
        service = CategoryService()
        result = service.add_category(name=name, code=code)
        click.echo(f"Kategori eklendi: {result}")
    except ValueError as e:
        click.echo(f"Hata: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Beklenmedik hata: {str(e)}", err=True)


@category.command('add-sub')
@click.argument('name')
@click.argument('code')
@click.argument('parent_code')
@with_appcontext
def add_subcategory(name: str, code: str, parent_code: str):
    """Yeni bir alt kategori ekle.
    
    Args:
        name: Alt kategori adı
        code: Alt kategori kodu
        parent_code: Üst kategori kodu
    """
    try:
        service = CategoryService()
        result = service.add_category(
            name=name,
            code=code,
            parent_code=parent_code
        )
        click.echo(f"Alt kategori eklendi: {result}")
    except ValueError as e:
        click.echo(f"Hata: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Beklenmedik hata: {str(e)}", err=True)


@category.command('assign-asin')
@click.argument('asin')
@click.argument('main_category')
@click.option('--sub-category', '-s', help='Alt kategori adı')
@click.option('--title', '-t', help='Ürün başlığı')
@with_appcontext
def assign_asin_category(asin: str, main_category: str, sub_category: str = None, title: str = None):
    """ASIN'e kategori atayın.
    
    Args:
        asin: ASIN
        main_category: Ana kategori adı
        sub_category: İsteğe bağlı alt kategori adı
        title: İsteğe bağlı ürün başlığı
    """
    try:
        service = CategoryService()
        result = service.assign_asin_category(
            asin=asin,
            main_category=main_category,
            sub_category=sub_category,
            title=title
        )
        click.echo(f"ASIN kategori atandı: {result}")
    except ValueError as e:
        click.echo(f"Hata: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Beklenmedik hata: {str(e)}", err=True)


@category.command('list')
@with_appcontext
def list_categories():
    """Tüm kategorileri ve alt kategorileri listele."""
    try:
        service = CategoryService()
        categories = service.get_categories()
        
        for cat in categories:
            click.echo(f"\n{cat['name']} ({cat['code']})")
            if cat['subcategories']:
                for sub in cat['subcategories']:
                    click.echo(f"  ├─ {sub['name']} ({sub['code']})")
                    
    except Exception as e:
        click.echo(f"Kategorileri listeleme hatası: {str(e)}", err=True)


@category.command('get-asin')
@click.argument('asin')
@with_appcontext
def get_asin_category(asin: str):
    """ASIN'in kategori bilgilerini al.
    
    Args:
        asin: ASIN
    """
    try:
        service = CategoryService()
        result = service.get_asin_category(asin)
        
        if result:
            click.echo(f"\nASIN: {result['asin']}")
            click.echo(f"Ana Kategori: {result['main_category']}")
            click.echo(f"Alt Kategori: {result['sub_category']}")
            if result['title']:
                click.echo(f"Başlık: {result['title']}")
        else:
            click.echo(f"ASIN için kategori bulunamadı: {asin}")
            
    except Exception as e:
        click.echo(f"ASIN kategori alma hatası: {str(e)}", err=True)


@category.command('import')
@click.argument('sql_file', type=click.Path(exists=True))
@with_appcontext
def import_categories(sql_file: str):
    """SQL dosyasından kategorileri yükle.
    
    Args:
        sql_file: Kategori verilerini içeren SQL dosyasının yolu
    """
    try:
        # Veritabanı yolunu app config'den al
        from flask import current_app
        db_path = os.path.join(current_app.instance_path, 'amazon_seller.db')
        
        # Veritabanına bağlan
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL dosyasını satır satır oku ve her INSERT ifadesini çalıştır
        with open(sql_file, 'r') as f:
            sql_content = f.read()
            cursor.executescript(sql_content)
        
        conn.commit()
        conn.close()
        
        click.echo("Kategoriler başarıyla yüklendi!")
        
    except Exception as e:
        click.echo(f"Kategorileri yükleme hatası: {str(e)}", err=True)


@category.command('import-mappings')
@click.argument('csv_file', type=click.Path(exists=True))
@with_appcontext
def import_asin_mappings(csv_file: str):
    """CSV dosyasından ASIN-kategori eşleştirmelerini yükle.
    
    Args:
        csv_file: ASIN-kategori eşleştirmelerini içeren CSV dosyasının yolu
    """
    try:
        # CSV dosyasını oku
        df = pd.read_csv(csv_file)
        required_columns = ['asin', 'category_code', 'title']
        if not all(col in df.columns for col in required_columns):
            click.echo('Hata: CSV dosyası asin, category_code, title sütunlarını içermelidir')
            return

        # Her satırı işle
        success_count = 0
        error_count = 0
        for _, row in df.iterrows():
            try:
                # Kategoriyi bul veya oluştur
                category = Category.query.filter_by(code=row['category_code']).first()
                if not category:
                    category = Category(
                        code=row['category_code'],
                        name=row['category_code'].replace('_', ' ').title(),
                        is_system=True
                    )
                    db.session.add(category)
                    db.session.flush()

                # ASIN eşleştirmesini oluştur
                mapping = ASINKategori(
                    asin=row['asin'],
                    kategori_id=category.id,
                    title=row['title']
                )
                db.session.add(mapping)
                db.session.flush()
                success_count += 1

            except Exception as e:
                db.session.rollback()
                click.echo(f"Satır işleme hatası: {e}")
                error_count += 1
                continue

        # Tüm değişiklikleri işle
        db.session.commit()
        click.echo(f'{success_count} eşleştirme başarıyla yüklendi')
        if error_count > 0:
            click.echo(f'{error_count} eşleştirme yüklenemedi')

    except Exception as e:
        click.echo(f'CSV dosyası okuma hatası: {e}', err=True)
