#!/usr/bin/env python3
"""
Script to add only new states that don't exist
"""

from database import engine, Base
from sqlalchemy.orm import sessionmaker
from models.base_location import State, District

# Create session
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def add_new_states():
    """Add only new states that don't exist"""
    print("🗄️ Adding New States Only")
    print("=" * 50)
    
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
            # Add new state
            new_state = State(name=state_name)
            db.add(new_state)
            db.commit()
            db.refresh(new_state)
            
            print(f"✅ Added State: {state_name} (ID: {new_state.id})")
            added_count += 1
        else:
            print(f"⚠️  State already exists: {state_name}")
    
    print("\n" + "=" * 50)
    print(f"📊 Summary: {added_count} new states added")
    print("✅ States addition complete!")
    
    db.close()

if __name__ == "__main__":
    add_new_states()
