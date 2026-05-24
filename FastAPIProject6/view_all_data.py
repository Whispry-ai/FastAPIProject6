#!/usr/bin/env python3
"""
View all data in the database: Languages, States, Districts, Cities, News
"""

from database import get_db
from models.base_location import Language, State, District, City
from models.news import News, Category
from sqlalchemy.orm import Session

def view_all_data():
    """View all data in the database"""
    print("📊 Viewing All Data in Database")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # 1. Languages
        print("\n🌍 LANGUAGES:")
        print("-" * 40)
        languages = db.query(Language).all()
        if languages:
            for lang in languages:
                print(f"   ID: {lang.id} | Code: {lang.code} | Name: {lang.name}")
            print(f"   Total: {len(languages)} languages")
        else:
            print("   ❌ No languages found")
        
        # 2. States
        print("\n🏛️  STATES:")
        print("-" * 40)
        states = db.query(State).all()
        if states:
            for state in states:
                lang_name = state.language.name if state.language else "No language"
                print(f"   ID: {state.id} | Name: {state.name} | Language: {lang_name}")
            print(f"   Total: {len(states)} states")
        else:
            print("   ❌ No states found")
        
        # 3. Districts
        print("\n📍 DISTRICTS:")
        print("-" * 40)
        districts = db.query(District).all()
        if districts:
            for district in districts:
                state_name = district.state.name if district.state else "No state"
                print(f"   ID: {district.id} | Name: {district.name} | State: {state_name}")
            print(f"   Total: {len(districts)} districts")
        else:
            print("   ❌ No districts found")
        
        # 4. Cities
        print("\n🏙️  CITIES:")
        print("-" * 40)
        cities = db.query(City).all()
        if cities:
            for city in cities:
                district_name = city.district.name if city.district else "No district"
                print(f"   ID: {city.id} | Name: {city.name} | District: {district_name}")
            print(f"   Total: {len(cities)} cities")
        else:
            print("   ❌ No cities found")
        
        # 5. Categories
        print("\n📂 CATEGORIES:")
        print("-" * 40)
        categories = db.query(Category).all()
        if categories:
            for cat in categories:
                print(f"   ID: {cat.id} | Name: {cat.name}")
            print(f"   Total: {len(categories)} categories")
        else:
            print("   ❌ No categories found")
        
        # 6. News
        print("\n📰 NEWS:")
        print("-" * 40)
        news = db.query(News).all()
        if news:
            for item in news:
                status = "✅ Approved" if item.is_approved else "⏳ Pending"
                breaking = "🔥 BREAKING" if item.is_breaking else ""
                lang_name = item.language.name if item.language else "No language"
                city_name = item.city.name if item.city else "No city"
                print(f"   ID: {item.id} | UID: {item.news_uid}")
                print(f"   Title: {item.title}")
                print(f"   Language: {lang_name} | City: {city_name}")
                print(f"   Status: {status} {breaking}")
                print(f"   👁️ Views: {item.views_count} | ❤️ Likes: {item.likes_count} | 💬 Comments: {item.comments_count} | 📤 Shares: {item.shares_count}")
                print()
            print(f"   Total: {len(news)} news articles")
        else:
            print("   ❌ No news found")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY:")
        print(f"   Languages: {len(languages)}")
        print(f"   States: {len(states)}")
        print(f"   Districts: {len(districts)}")
        print(f"   Cities: {len(cities)}")
        print(f"   Categories: {len(categories)}")
        print(f"   News: {len(news)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    view_all_data()
