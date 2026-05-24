#!/usr/bin/env python3
"""
Script to create default categories in the database
"""

from database import engine, SessionLocal
from models.news import Category

def create_default_categories():
    """Create default news categories"""
    print("🏷️ Creating Default Categories")
    print("=" * 40)
    
    default_categories = [
        "Politics",
        "Business", 
        "Technology",
        "Sports",
        "Entertainment",
        "Health",
        "Education",
        "Science",
        "Environment",
        "Lifestyle",
        "Travel",
        "Food",
        "Fashion",
        "Real Estate",
        "Automotive",
        "Crime",
        "Weather",
        "Transportation",
        "Infrastructure",
        "Agriculture",
        "Local Events",
        "Community",
        "Culture",
        "Religion",
        "Social Issues"
    ]
    
    try:
        with SessionLocal() as db:
            # Check existing categories
            existing_categories = db.query(Category).all()
            existing_names = {cat.name for cat in existing_categories}
            
            print(f"📊 Found {len(existing_categories)} existing categories")
            
            # Add new categories
            new_categories_added = 0
            for category_name in default_categories:
                if category_name not in existing_names:
                    category = Category(name=category_name)
                    db.add(category)
                    new_categories_added += 1
                    print(f"✅ Added: {category_name}")
                else:
                    print(f"⏭️  Already exists: {category_name}")
            
            # Commit changes
            if new_categories_added > 0:
                db.commit()
                print(f"\n🎉 Successfully added {new_categories_added} new categories!")
            else:
                print("\n📝 No new categories to add.")
            
            # Show all categories
            print("\n📋 All Categories:")
            all_categories = db.query(Category).order_by(Category.name).all()
            for i, category in enumerate(all_categories, 1):
                print(f"  {i:2d}. {category.name} (ID: {category.id})")
                
    except Exception as e:
        print(f"❌ Error creating categories: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Category Creation Script")
    print("=" * 50)
    
    if create_default_categories():
        print("\n✅ Category creation completed successfully!")
    else:
        print("\n❌ Category creation failed!")
