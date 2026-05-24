#!/usr/bin/env python3
"""
Delete all states except Andhra Pradesh and Telangana
This will cascade delete their districts and cities
"""

from database import SessionLocal
from models.base_location import State, District, City

def keep_only_two_states():
    """Keep only Andhra Pradesh and Telangana, delete all other states"""
    print("🗑️  Keeping Only Andhra Pradesh and Telangana")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get all states
        all_states = db.query(State).all()
        
        print(f"📊 Current states in database: {len(all_states)}")
        
        # States to keep
        states_to_keep = ["Andhra Pradesh", "Telangana"]
        
        states_to_delete = []
        states_kept = []
        
        for state in all_states:
            if state.name in states_to_keep:
                states_kept.append(state)
                print(f"✅ Keeping: {state.name} (ID: {state.id})")
            else:
                states_to_delete.append(state)
                print(f"🗑️  Will delete: {state.name} (ID: {state.id})")
        
        print(f"\n📊 Summary:")
        print(f"   States to keep: {len(states_kept)}")
        print(f"   States to delete: {len(states_to_delete)}")
        
        if len(states_to_delete) == 0:
            print("\n✅ No states to delete. Database already has only Andhra Pradesh and Telangana.")
            return
        
        # Confirm deletion
        print("\n⚠️  WARNING: This will delete all districts and cities associated with these states!")
        print("   This action cannot be undone.")
        
        # Delete states (this will cascade delete districts and cities)
        for state in states_to_delete:
            # First, get count of districts and cities to be deleted
            district_count = db.query(District).filter(District.state_id == state.id).count()
            city_count = db.query(City).join(District).filter(District.state_id == state.id).count()
            
            print(f"\n   Deleting {state.name}:")
            print(f"      - {district_count} districts")
            print(f"      - {city_count} cities")
            
            # Delete the state (cascade delete will handle districts and cities)
            db.delete(state)
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully deleted {len(states_to_delete)} states")
        print(f"✅ Kept {len(states_kept)} states: {[s.name for s in states_kept]}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    keep_only_two_states()
