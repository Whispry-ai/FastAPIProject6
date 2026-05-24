#!/usr/bin/env python3
"""
Delete orphaned districts and cities (those not belonging to Andhra Pradesh or Telangana)
"""

from database import SessionLocal
from models.base_location import State, District, City

def delete_orphaned_locations():
    """Delete orphaned districts and cities"""
    print("🗑️  Deleting Orphaned Districts and Cities")
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
        
        print(f"📊 Found {len(orphaned_districts)} orphaned districts")
        
        # Delete orphaned districts
        for district in orphaned_districts:
            print(f"   Deleting district: {district.name}")
            db.delete(district)
        
        db.commit()
        print(f"✅ Deleted {len(orphaned_districts)} orphaned districts")
        
        # Get all cities
        all_cities = db.query(City).all()
        
        # Get valid district IDs (districts belonging to AP or Telangana)
        valid_district_ids = [d.id for d in db.query(District).filter(District.state_id.in_(state_ids_to_keep)).all()]
        
        orphaned_cities = [c for c in all_cities if c.district_id not in valid_district_ids]
        
        print(f"\n📊 Found {len(orphaned_cities)} orphaned cities")
        
        # Delete orphaned cities
        for city in orphaned_cities:
            print(f"   Deleting city: {city.name}")
            db.delete(city)
        
        db.commit()
        print(f"✅ Deleted {len(orphaned_cities)} orphaned cities")
        
        print("\n" + "=" * 60)
        print(f"✅ Cleanup complete!")
        print(f"   Deleted {len(orphaned_districts)} districts")
        print(f"   Deleted {len(orphaned_cities)} cities")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_orphaned_locations()
