"""CLI commands for category management."""

import click
import csv
import sys
from typing import List, Dict, Any, TextIO
from flask.cli import with_appcontext
from app.modules.category.services.category_service import CategoryService
from app.extensions import db

@click.group()
def category():
    """Category management commands."""
    pass

@category.command('import-categories')
@click.argument('file', type=click.File('r'))
@click.option('--delimiter', default=',', help='CSV delimiter')
@click.option('--dry-run', is_flag=True, help='Validate without importing')
@with_appcontext
def import_categories(file: TextIO, delimiter: str, dry_run: bool):
    """Import categories from CSV file.
    
    Expected CSV format:
    name,code,description,parent_code
    Electronics,electronics,Electronic devices,
    Smartphones,smartphones,Mobile phones,electronics
    """
    try:
        reader = csv.DictReader(file, delimiter=delimiter)
        required_fields = {'name', 'code'}
        if not all(field in reader.fieldnames for field in required_fields):
            click.echo('Error: CSV must contain name and code columns', err=True)
            sys.exit(1)
            
        service = CategoryService()
        categories = []
        errors = []
        
        # First pass: validate
        for row in reader:
            try:
                if not row['name'] or not row['code']:
                    errors.append(f"Row {reader.line_num}: name and code are required")
                    continue
                    
                # Check if category exists
                existing = service.get_category_by_code(row['code'])
                if existing:
                    errors.append(f"Row {reader.line_num}: Category with code {row['code']} already exists")
                    continue
                    
                categories.append(row)
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
                
        if errors:
            click.echo('\n'.join(errors), err=True)
            if not dry_run:
                if not click.confirm('Continue with valid entries?'):
                    sys.exit(1)
                    
        if dry_run:
            click.echo(f"Validation complete. Found {len(errors)} errors in {reader.line_num} rows.")
            sys.exit(0 if not errors else 1)
            
        # Second pass: import
        imported = 0
        for category in categories:
            try:
                service.create_category(
                    name=category['name'],
                    code=category['code'],
                    description=category.get('description'),
                    parent_code=category.get('parent_code')
                )
                imported += 1
                click.echo(f"Imported: {category['name']} ({category['code']})")
            except Exception as e:
                click.echo(f"Error importing {category['code']}: {str(e)}", err=True)
                
        click.echo(f"Import complete. Imported {imported} categories.")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@category.command('export-categories')
@click.argument('file', type=click.File('w'))
@click.option('--delimiter', default=',', help='CSV delimiter')
@with_appcontext
def export_categories(file: TextIO, delimiter: str):
    """Export categories to CSV file."""
    try:
        service = CategoryService()
        categories = service.get_category_tree()
        
        writer = csv.DictWriter(
            file,
            fieldnames=['name', 'code', 'description', 'parent_code'],
            delimiter=delimiter
        )
        writer.writeheader()
        
        def flatten_categories(cats: List[Dict[str, Any]], parent_code: str = None):
            """Flatten nested category structure."""
            flattened = []
            for cat in cats:
                row = {
                    'name': cat['name'],
                    'code': cat['code'],
                    'description': cat.get('description', ''),
                    'parent_code': parent_code or ''
                }
                flattened.append(row)
                if 'children' in cat:
                    flattened.extend(flatten_categories(cat['children'], cat['code']))
            return flattened
            
        flat_categories = flatten_categories(categories)
        writer.writerows(flat_categories)
        
        click.echo(f"Exported {len(flat_categories)} categories.")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@category.command('import-asin-categories')
@click.argument('file', type=click.File('r'))
@click.option('--delimiter', default=',', help='CSV delimiter')
@click.option('--dry-run', is_flag=True, help='Validate without importing')
@click.option('--batch-size', default=1000, help='Batch size for bulk import')
@with_appcontext
def import_asin_categories(file: TextIO, delimiter: str, dry_run: bool, batch_size: int):
    """Import ASIN-category mappings from CSV file.
    
    Expected CSV format:
    asin,category_code,title,description
    B01EXAMPLE,electronics,iPhone 13,Latest iPhone
    """
    try:
        reader = csv.DictReader(file, delimiter=delimiter)
        required_fields = {'asin', 'category_code', 'title'}
        if not all(field in reader.fieldnames for field in required_fields):
            click.echo('Error: CSV must contain asin, category_code, and title columns', err=True)
            sys.exit(1)
            
        service = CategoryService()
        mappings = []
        errors = []
        total_rows = 0
        
        # First pass: validate
        for row in reader:
            total_rows += 1
            try:
                if not all(row.get(field) for field in required_fields):
                    errors.append(f"Row {reader.line_num}: asin, category_code, and title are required")
                    continue
                    
                # Check if category exists
                if not service.get_category_by_code(row['category_code']):
                    errors.append(f"Row {reader.line_num}: Category {row['category_code']} not found")
                    continue
                    
                mappings.append(row)
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {str(e)}")
                
        if errors:
            click.echo('\n'.join(errors), err=True)
            if not dry_run:
                if not click.confirm('Continue with valid entries?'):
                    sys.exit(1)
                    
        if dry_run:
            click.echo(f"Validation complete. Found {len(errors)} errors in {total_rows} rows.")
            sys.exit(0 if not errors else 1)
            
        # Second pass: import in batches
        imported = 0
        for i in range(0, len(mappings), batch_size):
            batch = mappings[i:i + batch_size]
            try:
                service.bulk_assign_categories(batch)
                imported += len(batch)
                click.echo(f"Imported batch: {i+1}-{i+len(batch)} of {len(mappings)}")
            except Exception as e:
                click.echo(f"Error importing batch {i//batch_size + 1}: {str(e)}", err=True)
                if not click.confirm('Continue with next batch?'):
                    break
                    
        click.echo(f"Import complete. Imported {imported} mappings.")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@category.command('export-asin-categories')
@click.argument('file', type=click.File('w'))
@click.option('--delimiter', default=',', help='CSV delimiter')
@click.option('--include-uncategorized', is_flag=True, help='Include ASINs without categories')
@with_appcontext
def export_asin_categories(file: TextIO, delimiter: str, include_uncategorized: bool):
    """Export ASIN-category mappings to CSV file."""
    try:
        service = CategoryService()
        
        # Get uncategorized ASINs if requested
        uncategorized = []
        if include_uncategorized:
            uncategorized = service.get_uncategorized_asins()
            
        writer = csv.DictWriter(
            file,
            fieldnames=['asin', 'category', 'category_code', 'parent_category', 'parent_code', 'title', 'description'],
            delimiter=delimiter
        )
        writer.writeheader()
        
        # Write uncategorized ASINs
        for asin in uncategorized:
            writer.writerow({
                'asin': asin,
                'category': '#N/A',
                'category_code': '#N/A',
                'parent_category': '#N/A',
                'parent_code': '#N/A',
                'title': '',
                'description': ''
            })
            
        # Get and write categorized ASINs
        # This is a placeholder - we need to implement a method to get all ASINs
        # TODO: Implement get_all_asins in CategoryService
        
        click.echo("Export complete.")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@category.command('cleanup')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted')
@with_appcontext
def cleanup_categories():
    """Remove unused categories and fix inconsistencies."""
    # TODO: Implement category cleanup
    click.echo("Category cleanup not implemented yet.")
    
def init_app(app):
    """Register CLI commands with the app."""
    app.cli.add_command(category)
