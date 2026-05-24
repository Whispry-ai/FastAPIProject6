#!/usr/bin/env python3
"""
Script to display existing states and districts in database
"""

from database import engine, Base
from sqlalchemy.orm import sessionmaker
from models.base_location import State, District, City

# Create session
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def show_existing_data():
    """Display existing states and districts in database"""
    print("🗄️ Existing Database Data")
    print("=" * 50)
    
    # Get all states
    states = db.query(State).all()
    
    if not states:
        print("❌ No states found in database")
        return
    
    print(f"📊 Found {len(states)} states:")
    print()
    
    for state in sorted(states, key=lambda x: x.name):
        print(f"🏷️  State: {state.name} (ID: {state.id})")
        
        # Get districts for this state
        districts = db.query(District).filter(District.state_id == state.id).all()
        
        if districts:
            print(f"   🏘️  Districts in {state.name}:")
            for district in sorted(districts, key=lambda x: x.name):
                print(f"      ├─ {district.name} (ID: {district.id})")
        else:
            print(f"   🏘️  No districts found in {state.name}")
    
    print("\n" + "=" * 50)
    
    # Show all cities (optional)
    cities = db.query(City).all()
    if cities:
        print(f"🏙️  Total Cities: {len(cities)}")
        for city in sorted(cities[:5], key=lambda x: x.name):  # Show first 5 cities
            print(f"   ├─ {city.name} (ID: {city.id})")
    
    print("\n" + "=" * 50)
    print("✅ Database data analysis complete!")
    
    db.close()

if __name__ == "__main__":
    show_existing_data()
