#!/usr/bin/env python3
"""
Create 9 news articles with ads inserted after every 3 articles
Pattern: 3 news, 1 ad, 3 news, 1 ad, 3 news
Includes breaking news
"""

from database import SessionLocal
from models.news import News, Category
from models.content import Advertisement
from models.base_location import Language, State, District, City
from datetime import datetime, timedelta
import random

def create_news_with_ads():
    """Create 9 news articles with ads after every 3 articles"""
    print("📰 Creating News with Ads")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get required data
        english_lang = db.query(Language).filter(Language.code == "en").first()
        telugu_lang = db.query(Language).filter(Language.code == "te").first()
        hindi_lang = db.query(Language).filter(Language.code == "hi").first()
        
        andhra_state = db.query(State).filter(State.name == "Andhra Pradesh").first()
        telangana_state = db.query(State).filter(State.name == "Telangana").first()
        
        # Get districts
        guntur_district = db.query(District).filter(District.name == "Guntur").first()
        hyderabad_district = db.query(District).filter(District.name == "Hyderabad").first()
        vijayawada_district = db.query(District).filter(District.name == "Krishna").first()
        
        # Get cities
        vijayawada_city = db.query(City).filter(City.district_id == vijayawada_district.id).first()
        hyderabad_city = db.query(City).filter(City.district_id == hyderabad_district.id).first()
        guntur_city = db.query(City).filter(City.district_id == guntur_district.id).first()
        
        # Get or create categories
        politics_cat = db.query(Category).filter(Category.name == "Politics").first()
        if not politics_cat:
            politics_cat = Category(name="Politics")
            db.add(politics_cat)
            db.commit()
            db.refresh(politics_cat)
        
        tech_cat = db.query(Category).filter(Category.name == "Technology").first()
        if not tech_cat:
            tech_cat = Category(name="Technology")
            db.add(tech_cat)
            db.commit()
            db.refresh(tech_cat)
        
        sports_cat = db.query(Category).filter(Category.name == "Sports").first()
        if not sports_cat:
            sports_cat = Category(name="Sports")
            db.add(sports_cat)
            db.commit()
            db.refresh(sports_cat)
        
        # Get an existing user from database
        from models.user import User
        existing_user = db.query(User).first()
        if not existing_user:
            print("❌ No users found in database. Please create a user first.")
            return
        test_user_uid = existing_user.user_uid
        print(f"👤 Using existing user: {test_user_uid}")
        
        # News articles data
        news_articles = [
            {
                "title": "Andhra Pradesh Government Announces New IT Policy",
                "summary": "The state government has unveiled a comprehensive IT policy to attract investments and create jobs in the technology sector.",
                "image_url": "https://example.com/it-policy.jpg",
                "language": telugu_lang,
                "city": vijayawada_city,
                "categories": [politics_cat, tech_cat],
                "is_breaking": True,
                "breaking_priority": 5
            },
            {
                "title": "Hyderabad Metro Rail Expansion Project Approved",
                "summary": "The central government has approved the expansion of Hyderabad Metro Rail to connect more areas of the city.",
                "image_url": "https://example.com/metro-rail.jpg",
                "language": telugu_lang,
                "city": hyderabad_city,
                "categories": [politics_cat],
                "is_breaking": False
            },
            {
                "title": "Cricket World Cup: India Wins Against Australia",
                "summary": "In a thrilling match, the Indian cricket team defeated Australia by 5 wickets in the World Cup semi-final.",
                "image_url": "https://example.com/cricket.jpg",
                "language": english_lang,
                "city": hyderabad_city,
                "categories": [sports_cat],
                "is_breaking": True,
                "breaking_priority": 8
            },
            {
                "title": "Telangana Launches Startup Fund for Young Entrepreneurs",
                "summary": "The Telangana government has launched a ₹500 crore fund to support startups and young entrepreneurs in the state.",
                "image_url": "https://example.com/startup-fund.jpg",
                "language": telugu_lang,
                "city": hyderabad_city,
                "categories": [politics_cat, tech_cat],
                "is_breaking": True,
                "breaking_priority": 6
            },
            {
                "title": "Guntur Farmers Protest Against New Agricultural Laws",
                "summary": "Hundreds of farmers from Guntur district have gathered to protest against the newly introduced agricultural laws.",
                "image_url": "https://example.com/farmers-protest.jpg",
                "language": telugu_lang,
                "city": guntur_city,
                "categories": [politics_cat],
                "is_breaking": False
            },
            {
                "title": "AI Technology Summit Held in Hyderabad",
                "summary": "Leading tech companies and researchers gathered in Hyderabad for the annual Artificial Intelligence Technology Summit.",
                "image_url": "https://example.com/ai-summit.jpg",
                "language": english_lang,
                "city": hyderabad_city,
                "categories": [tech_cat],
                "is_breaking": False
            },
            {
                "title": "Andhra Pradesh Chief Minister Visits Delhi for Key Meetings",
                "summary": "The Chief Minister of Andhra Pradesh is in Delhi for crucial meetings with central government officials regarding state development.",
                "image_url": "https://example.com/cm-delhi.jpg",
                "language": telugu_lang,
                "city": vijayawada_city,
                "categories": [politics_cat],
                "is_breaking": True,
                "breaking_priority": 7
            },
            {
                "title": "New Medical College Announced in Vijayawada",
                "summary": "The state government has sanctioned a new medical college in Vijayawada to improve healthcare infrastructure.",
                "image_url": "https://example.com/medical-college.jpg",
                "language": telugu_lang,
                "city": vijayawada_city,
                "categories": [politics_cat],
                "is_breaking": False
            },
            {
                "title": "Telugu Film Industry Records Highest Box Office Collection",
                "summary": "The Telugu film industry has achieved its highest-ever box office collection with multiple blockbuster releases this year.",
                "image_url": "https://example.com/tollywood.jpg",
                "language": telugu_lang,
                "city": hyderabad_city,
                "categories": [tech_cat],
                "is_breaking": False
            }
        ]
        
        # Create news articles
        created_news = []
        for i, news_data in enumerate(news_articles, 1):
            # Generate unique news_uid
            import string
            import random
            news_uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Set breaking expiry for breaking news
            breaking_expires_at = None
            if news_data["is_breaking"]:
                breaking_expires_at = datetime.now() + timedelta(hours=24)
            
            news = News(
                news_uid=news_uid,
                title=news_data["title"],
                summary=news_data["summary"],
                image_url=news_data["image_url"],
                language_id=news_data["language"].id,
                city_id=news_data["city"].id if news_data["city"] else None,
                user_uid=test_user_uid,
                is_approved=1,  # Auto-approve
                is_breaking=news_data["is_breaking"],
                breaking_priority=news_data.get("breaking_priority", 0),
                breaking_expires_at=breaking_expires_at,
                created_at=datetime.now()
            )
            
            db.add(news)
            db.commit()
            db.refresh(news)
            
            # Add categories
            for category in news_data["categories"]:
                news.categories.append(category)
            
            db.commit()
            created_news.append(news)
            
            breaking_status = "🔥 BREAKING" if news_data["is_breaking"] else ""
            print(f"✅ Created News {i}: {news_data['title']} {breaking_status}")
        
        # Create ads
        ads_data = [
            {
                "title": "Smartphone Sale - Up to 50% Off",
                "image_url": "https://example.com/phone-ad.jpg",
                "redirect_url": "https://example.com/phones",
                "placement": "feed"
            },
            {
                "title": "Travel Deals - Book Now & Save",
                "image_url": "https://example.com/travel-ad.jpg",
                "redirect_url": "https://example.com/travel",
                "placement": "feed"
            }
        ]
        
        created_ads = []
        for i, ad_data in enumerate(ads_data, 1):
            ad = Advertisement(
                title=ad_data["title"],
                image_url=ad_data["image_url"],
                redirect_url=ad_data["redirect_url"],
                placement=ad_data["placement"],
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                is_active=True,
                is_approved=True,
                created_at=datetime.now()
            )
            
            db.add(ad)
            db.commit()
            db.refresh(ad)
            created_ads.append(ad)
            
            print(f"📢 Created Ad {i}: {ad_data['title']}")
        
        # Display the feed pattern
        print("\n" + "=" * 60)
        print("📊 FEED PATTERN (3 News + 1 Ad):")
        print("=" * 60)
        
        position = 1
        ad_index = 0
        
        for i, news in enumerate(created_news):
            breaking_icon = "🔥 " if news.is_breaking else ""
            print(f"   {position}. 📰 {breaking_icon}{news.title}")
            position += 1
            
            # Insert ad after every 3 news
            if (i + 1) % 3 == 0 and ad_index < len(created_ads):
                ad = created_ads[ad_index]
                print(f"   {position}. 📢 ADVERTISEMENT: {ad.title}")
                position += 1
                ad_index += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Created {len(created_news)} news articles")
        print(f"✅ Created {len(created_ads)} advertisements")
        print(f"✅ Breaking news: {sum(1 for n in created_news if n.is_breaking)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_news_with_ads()
