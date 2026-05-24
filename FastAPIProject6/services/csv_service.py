"""
CSV Service for Import/Export functionality
"""

import csv
import io
from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.news import News
from models.news import Category
from schemas import NewsCreate

class CSVService:
    """Service for handling CSV import/export operations"""
    
    REQUIRED_COLUMNS = ['title', 'summary', 'content', 'language_id', 'user_uid']
    OPTIONAL_COLUMNS = ['image_url', 'source_url', 'source_name', 'city_id', 'category_ids']
    
    @staticmethod
    def validate_csv_structure(file_content: str) -> Dict[str, Any]:
        """Validate CSV file structure"""
        try:
            # Parse CSV to check structure
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)
            
            if not rows:
                return {
                    'valid': False,
                    'error': 'CSV file is empty',
                    'missing_columns': []
                }
            
            # Get all columns from CSV
            csv_columns = set()
            for row in rows:
                csv_columns.update(row.keys())
            
            # Check required columns
            missing_required = [col for col in CSVService.REQUIRED_COLUMNS if col not in csv_columns]
            
            # Check for unknown columns
            unknown_columns = [col for col in csv_columns if col not in CSVService.REQUIRED_COLUMNS + CSVService.OPTIONAL_COLUMNS]
            
            return {
                'valid': len(missing_required) == 0,
                'error': f"Missing required columns: {', '.join(missing_required)}" if missing_required else None,
                'missing_columns': missing_required,
                'unknown_columns': unknown_columns,
                'total_rows': len(rows),
                'found_columns': list(csv_columns)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'CSV parsing error: {str(e)}',
                'missing_columns': []
            }
    
    @staticmethod
    def import_news_from_csv(file_content: str, db: Session) -> Dict[str, Any]:
        """Import news from CSV file"""
        try:
            # Validate CSV structure first
            validation = CSVService.validate_csv_structure(file_content)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error'],
                    'imported_count': 0
                }
            
            # Parse and import news
            csv_reader = csv.DictReader(io.StringIO(file_content))
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Create news object
                    news_data = NewsCreate(
                        title=row['title'],
                        summary=row['summary'],
                        content=row['content'],
                        language_id=int(row['language_id']),
                        user_uid=row['user_uid'],
                        image_url=row.get('image_url'),
                        source_url=row.get('source_url'),
                        source_name=row.get('source_name'),
                        city_id=int(row['city_id']) if row.get('city_id') else None,
                        category_ids=[int(cid) for cid in row.get('category_ids', '').split(',') if cid.strip()]
                    )
                    
                    # Create news record (you'll need to implement this logic in your routes)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return {
                'success': True,
                'imported_count': imported_count,
                'total_rows': validation['total_rows'],
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Import error: {str(e)}',
                'imported_count': 0
            }
    
    @staticmethod
    def export_news_to_csv(db: Session, filters: Dict[str, Any] = None) -> str:
        """Export news to CSV format"""
        try:
            # Build query based on filters
            query = db.query(News)
            
            if filters:
                if 'language_id' in filters:
                    query = query.filter(News.language_id == filters['language_id'])
                if 'user_uid' in filters:
                    query = query.filter(News.user_uid == filters['user_uid'])
                if 'city_id' in filters:
                    query = query.filter(News.city_id == filters['city_id'])
                if 'category_id' in filters:
                    # This would require joining with categories table
                    pass
            
            # Get all news
            news_items = query.all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'id', 'news_uid', 'title', 'summary', 'content', 'language_id',
                'user_uid', 'city_id', 'image_url', 'source_url', 'source_name',
                'is_approved', 'is_published', 'created_at', 'updated_at'
            ])
            
            # Write data rows
            for news_item in news_items:
                writer.writerow([
                    news_item.id,
                    news_item.news_uid,
                    news_item.title,
                    news_item.summary,
                    news_item.content,
                    news_item.language_id,
                    news_item.user_uid,
                    news_item.city_id,
                    news_item.image_url,
                    news_item.source_url,
                    news_item.source_name,
                    news_item.is_approved,
                    news_item.is_published,
                    news_item.created_at.isoformat() if news_item.created_at else '',
                    news_item.updated_at.isoformat() if news_item.updated_at else ''
                ])
            
            return output.getvalue()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")
    
    @staticmethod
    def export_categories_to_csv(db: Session) -> str:
        """Export categories to CSV format"""
        try:
            categories = db.query(Category).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['id', 'name'])
            
            # Write data rows
            for category in categories:
                writer.writerow([category.id, category.name])
            
            return output.getvalue()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")
    
    @staticmethod
    def generate_csv_template() -> str:
        """Generate CSV template for news import"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header with all columns
        all_columns = CSVService.REQUIRED_COLUMNS + CSVService.OPTIONAL_COLUMNS
        writer.writerow(all_columns)
        
        # Write example row
        writer.writerow([
            'Example News Title',
            'This is a summary of the news article',
            'Full news content goes here...',
            '1',
            'user123',
            'https://example.com/image.jpg',
            'https://example.com/news',
            'Example Source',
            '1',
            '1,2,3'
        ])
        
        return output.getvalue()
