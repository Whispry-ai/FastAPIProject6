#!/usr/bin/env python3
"""
Language Creation Script for Hyperlocal News Application
Creates default languages in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from models.base_location import Language
from sqlalchemy.orm import Session

def create_default_languages():
    """Create default languages in the database"""
    
    db = SessionLocal()
    
    try:
        # 22 Official Indian Languages (8th Schedule of Indian Constitution) + English
        default_languages = [
            {"name": "English", "code": "en"},
            {"name": "Assamese", "code": "as"},
            {"name": "Bengali", "code": "bn"},
            {"name": "Bodo", "code": "brx"},
            {"name": "Dogri", "code": "doi"},
            {"name": "Gujarati", "code": "gu"},
            {"name": "Hindi", "code": "hi"},
            {"name": "Kannada", "code": "kn"},
            {"name": "Kashmiri", "code": "ks"},
            {"name": "Konkani", "code": "kok"},
            {"name": "Maithili", "code": "mai"},
            {"name": "Malayalam", "code": "ml"},
            {"name": "Manipuri", "code": "mni"},
            {"name": "Marathi", "code": "mr"},
            {"name": "Nepali", "code": "ne"},
            {"name": "Odia", "code": "or"},
            {"name": "Punjabi", "code": "pa"},
            {"name": "Sanskrit", "code": "sa"},
            {"name": "Santali", "code": "sat"},
            {"name": "Sindhi", "code": "sd"},
            {"name": "Tamil", "code": "ta"},
            {"name": "Telugu", "code": "te"},
            {"name": "Urdu", "code": "ur"}
        ]
        
        print("🚀 Language Creation Script")
        print("=" * 50)
        print("🌍 Creating Default Languages")
        print("=" * 50)
        
        # Check existing languages
        existing_languages = db.query(Language).all()
        existing_names = {lang.name for lang in existing_languages}
        
        print(f"📊 Found {len(existing_languages)} existing languages")
        
        new_languages_count = 0
        
        for lang_data in default_languages:
            if lang_data["name"] not in existing_names:
                new_language = Language(**lang_data)
                db.add(new_language)
                new_languages_count += 1
                print(f"✅ Added: {lang_data['name']} ({lang_data['code']})")
            else:
                print(f"⏭️  Already exists: {lang_data['name']}")
        
        if new_languages_count > 0:
            db.commit()
            print(f"\n🎉 Successfully created {new_languages_count} new languages!")
        else:
            print(f"\n📝 No new languages to add.")
        
        # Show all languages
        print("\n📋 All Languages:")
        all_languages = db.query(Language).order_by(Language.name).all()
        for i, lang in enumerate(all_languages, 1):
            print(f"   {i}. {lang.name} (ID: {lang.id}, Code: {lang.code})")
        
        print("\n✅ Language creation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating languages: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    create_default_languages()
