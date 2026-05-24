#!/usr/bin/env python3
"""
Script to safely add new states without conflicts
"""

from database import engine, Base
from sqlalchemy.orm import sessionmaker
from models.base_location import State, District

# Create session
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def safe_add_states():
    """Safely add new states that don't exist"""
    print("🗄️ Safely Adding States")
    print("=" * 50)
    
    # Get existing state IDs first
    existing_ids = {state.id for state in db.query(State).all()}
    print(f"📊 Existing state IDs: {sorted(existing_ids)}")
    
    # New states to add (only names, no ID conflicts)
    new_states = [
        "Uttar Pradesh",
        "Madhya Pradesh", 
        "Rajasthan",
        "Gujarat",
        "West Bengal",
        "Punjab",
        "Haryana",
        "Delhi",
        "Bihar",
        "Odisha",
        "Kerala"
    ]
    
    added_count = 0
    
    for state_name in new_states:
        # Check if state already exists
        existing_state = db.query(State).filter(State.name == state_name).first()
        
        if not existing_state:
            try:
                # Add new state
                new_state = State(name=state_name)
                db.add(new_state)
                db.commit()
                db.refresh(new_state)
                
                print(f"✅ Added State: {state_name} (ID: {new_state.id})")
                added_count += 1
                
            except Exception as e:
                print(f"❌ Error adding {state_name}: {e}")
                db.rollback()
        else:
            print(f"⚠️  State already exists: {state_name} (ID: {existing_state.id})")
    
    print("\n" + "=" * 50)
    print(f"📊 Summary: {added_count} new states added")
    print("✅ Safe states addition complete!")
    
    db.close()

if __name__ == "__main__":
    safe_add_states()
