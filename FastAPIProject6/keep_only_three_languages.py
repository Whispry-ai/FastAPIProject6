#!/usr/bin/env python3
"""
Delete all languages except Telugu, English, and Hindi
"""

from database import SessionLocal
from models.base_location import Language

def keep_only_three_languages():
    """Keep only Telugu, English, and Hindi, delete all other languages"""
    print("🗑️  Keeping Only Telugu, English, and Hindi")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get all languages
        all_languages = db.query(Language).all()
        
        print(f"📊 Current languages in database: {len(all_languages)}")
        
        # Languages to keep (with their codes)
        languages_to_keep = {
            "Telugu": "te",
            "English": "en",
            "Hindi": "hi"
        }
        
        languages_to_delete = []
        languages_kept = []
        
        for lang in all_languages:
            if lang.name in languages_to_keep and lang.code == languages_to_keep[lang.name]:
                languages_kept.append(lang)
                print(f"✅ Keeping: {lang.name} (Code: {lang.code}, ID: {lang.id})")
            else:
                languages_to_delete.append(lang)
                print(f"🗑️  Will delete: {lang.name} (Code: {lang.code}, ID: {lang.id})")
        
        print(f"\n📊 Summary:")
        print(f"   Languages to keep: {len(languages_kept)}")
        print(f"   Languages to delete: {len(languages_to_delete)}")
        
        if len(languages_to_delete) == 0:
            print("\n✅ No languages to delete. Database already has only Telugu, English, and Hindi.")
            return
        
        # Confirm deletion
        print("\n⚠️  WARNING: This will delete all languages except Telugu, English, and Hindi!")
        print("   This action cannot be undone.")
        
        # Delete languages
        for lang in languages_to_delete:
            print(f"\n   Deleting {lang.name} (Code: {lang.code})")
            db.delete(lang)
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully deleted {len(languages_to_delete)} languages")
        print(f"✅ Kept {len(languages_kept)} languages:")
        for lang in languages_kept:
            print(f"      - {lang.name} (Code: {lang.code})")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    keep_only_three_languages()
