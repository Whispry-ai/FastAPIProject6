#!/usr/bin/env python3
"""
Check for orphaned districts and cities (those not belonging to Andhra Pradesh or Telangana)
"""

from database import SessionLocal
from models.base_location import State, District, City

def check_orphaned_locations():
    """Check for orphaned districts and cities"""
    print("🔍 Checking for Orphaned Districts and Cities")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get the two states we want to keep
        andhra_state = db.query(State).filter(State.name == "Andhra Pradesh").first()
        telangana_state = db.query(State).filter(State.name == "Telangana").first()
        
        if not andhra_state or not telangana_state:
            print("❌ Andhra Pradesh or Telangana not found in database")
            return
        
        state_ids_to_keep = [andhra_state.id, telangana_state.id]
        
        # Get all districts
        all_districts = db.query(District).all()
        orphaned_districts = [d for d in all_districts if d.state_id not in state_ids_to_keep]
        
        print(f"📊 Total districts in database: {len(all_districts)}")
        print(f"📊 Orphaned districts (not belonging to AP or Telangana): {len(orphaned_districts)}")
        
        if orphaned_districts:
            print("\n🗑️  Orphaned districts (first 10):")
            for district in orphaned_districts[:10]:
                state_name = district.state.name if district.state else "No state"
                print(f"   - {district.name} (State: {state_name}, ID: {district.id})")
            if len(orphaned_districts) > 10:
                print(f"   ... and {len(orphaned_districts) - 10} more")
        
        # Get all cities
        all_cities = db.query(City).all()
        
        # Get valid district IDs (districts belonging to AP or Telangana)
        valid_district_ids = [d.id for d in all_districts if d.state_id in state_ids_to_keep]
        
        orphaned_cities = [c for c in all_cities if c.district_id not in valid_district_ids]
        
        print(f"\n📊 Total cities in database: {len(all_cities)}")
        print(f"📊 Orphaned cities (not belonging to AP or Telangana districts): {len(orphaned_cities)}")
        
        if orphaned_cities:
            print("\n🗑️  Orphaned cities (first 10):")
            for city in orphaned_cities[:10]:
                district_name = city.district.name if city.district else "No district"
                print(f"   - {city.name} (District: {district_name}, ID: {city.id})")
            if len(orphaned_cities) > 10:
                print(f"   ... and {len(orphaned_cities) - 10} more")
        
        print("\n" + "=" * 60)
        print(f"📊 Summary:")
        print(f"   Total districts: {len(all_districts)}")
        print(f"   Valid districts: {len(all_districts) - len(orphaned_districts)}")
        print(f"   Orphaned districts: {len(orphaned_districts)}")
        print(f"   Total cities: {len(all_cities)}")
        print(f"   Valid cities: {len(all_cities) - len(orphaned_cities)}")
        print(f"   Orphaned cities: {len(orphaned_cities)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_orphaned_locations()
