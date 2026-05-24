#!/usr/bin/env python3
"""
Check what districts and cities exist for Andhra Pradesh and Telangana
"""

from database import SessionLocal
from models.base_location import State, District, City

def check_telangana_andhra():
    """Check districts and cities for Andhra Pradesh and Telangana"""
    print("🔍 Checking Telangana and Andhra Pradesh Data")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        states_to_check = ["Andhra Pradesh", "Telangana"]
        
        for state_name in states_to_check:
            state = db.query(State).filter(State.name == state_name).first()
            
            if not state:
                print(f"❌ State not found: {state_name}")
                continue
            
            print(f"\n🏛️  {state_name} (ID: {state.id})")
            print("-" * 50)
            
            # Get districts
            districts = db.query(District).filter(District.state_id == state.id).all()
            print(f"   Districts: {len(districts)}")
            
            for district in districts:
                # Get cities for this district
                cities = db.query(City).filter(City.district_id == district.id).all()
                print(f"      - {district.name}: {len(cities)} cities")
                if cities:
                    for city in cities[:3]:  # Show first 3 cities
                        print(f"         • {city.name}")
                    if len(cities) > 3:
                        print(f"         ... and {len(cities) - 3} more")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_telangana_andhra()
