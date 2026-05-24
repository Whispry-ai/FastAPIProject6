#!/usr/bin/env python3
"""
Create Telangana and Andhra Pradesh states with their districts and cities
"""

from database import engine, SessionLocal
from models.base_location import State, District, City

def create_telangana_andhra():
    """Create Telangana and Andhra Pradesh states with districts and cities"""
    print("🗄️ Creating Telangana and Andhra Pradesh")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # States with districts and cities
        states_to_add = [
            {
                "name": "Andhra Pradesh",
                "districts": [
                    {"name": "Anantapur", "cities": ["Anantapur", "Guntakal", "Hindupur"]},
                    {"name": "Chittoor", "cities": ["Chittoor", "Tirupati", "Madanapalle"]},
                    {"name": "East Godavari", "cities": ["Kakinada", "Rajahmundry", "Amalapuram"]},
                    {"name": "Guntur", "cities": ["Guntur", "Tenali", "Vijayawada"]},
                    {"name": "Krishna", "cities": ["Vijayawada", "Machilipatnam", "Gudivada"]},
                    {"name": "Kurnool", "cities": ["Kurnool", "Nandyal", "Adoni"]},
                    {"name": "Nellore", "cities": ["Nellore", "Kavali", "Gudur"]},
                    {"name": "Prakasam", "cities": ["Ongole", "Markapur", "Chirala"]},
                    {"name": "Srikakulam", "cities": ["Srikakulam", "Amadalavalasa", "Palasa"]},
                    {"name": "Visakhapatnam", "cities": ["Visakhapatnam", "Vizianagaram", "Anakapalle"]},
                    {"name": "Vizianagaram", "cities": ["Vizianagaram", "Bobbili", "Salur"]},
                    {"name": "West Godavari", "cities": ["Eluru", "Bhimavaram", "Tadepalligudem"]},
                    {"name": "YSR Kadapa", "cities": ["Kadapa", "Proddatur", "Rayachoti"]}
                ]
            },
            {
                "name": "Telangana",
                "districts": [
                    {"name": "Adilabad", "cities": ["Adilabad", "Nirmal"]},
                    {"name": "Bhadradri Kothagudem", "cities": ["Kothagudem", "Bhadrachalam"]},
                    {"name": "Hyderabad", "cities": ["Hyderabad", "Secunderabad"]},
                    {"name": "Jagtial", "cities": ["Jagtial", "Korutla"]},
                    {"name": "Jangaon", "cities": ["Jangaon"]},
                    {"name": "Jayashankar Bhupalpally", "cities": ["Bhupalpally"]},
                    {"name": "Jogulamba Gadwal", "cities": ["Gadwal"]},
                    {"name": "Kamareddy", "cities": ["Kamareddy"]},
                    {"name": "Karimnagar", "cities": ["Karimnagar", "Jagitial"]},
                    {"name": "Khammam", "cities": ["Khammam", "Kothagudem"]},
                    {"name": "Kumuram Bheem Asifabad", "cities": ["Asifabad"]},
                    {"name": "Mahabubabad", "cities": ["Mahabubabad"]},
                    {"name": "Mahabubnagar", "cities": ["Mahabubnagar", "Narayanpet"]},
                    {"name": "Mancherial", "cities": ["Mancherial"]},
                    {"name": "Medak", "cities": ["Medak", "Sangareddy"]},
                    {"name": "Medchal Malkajgiri", "cities": ["Medchal", "Malkajgiri"]},
                    {"name": "Mulugu", "cities": ["Mulugu"]},
                    {"name": "Nagarkurnool", "cities": ["Nagarkurnool"]},
                    {"name": "Nalgonda", "cities": ["Nalgonda", "Miryalaguda"]},
                    {"name": "Narayanpet", "cities": ["Narayanpet"]},
                    {"name": "Nirmal", "cities": ["Nirmal"]},
                    {"name": "Nizamabad", "cities": ["Nizamabad", "Kamareddy"]},
                    {"name": "Peddapalli", "cities": ["Peddapalli"]},
                    {"name": "Rajanna Sircilla", "cities": ["Sircilla"]},
                    {"name": "Ranga Reddy", "cities": ["Shamshabad", "Chevella"]},
                    {"name": "Sangareddy", "cities": ["Sangareddy"]},
                    {"name": "Siddipet", "cities": ["Siddipet"]},
                    {"name": "Suryapet", "cities": ["Suryapet"]},
                    {"name": "Vikarabad", "cities": ["Vikarabad"]},
                    {"name": "Wanaparthy", "cities": ["Wanaparthy"]},
                    {"name": "Warangal Rural", "cities": ["Warangal"]},
                    {"name": "Warangal Urban", "cities": ["Warangal", "Hanamkonda"]},
                    {"name": "Yadadri Bhongir", "cities": ["Bhongir"]}
                ]
            }
        ]
        
        added_states = 0
        added_districts = 0
        added_cities = 0
        
        for state_data in states_to_add:
            # Check if state already exists
            existing_state = db.query(State).filter(State.name == state_data["name"]).first()
            
            if not existing_state:
                # Add new state
                new_state = State(name=state_data["name"])
                db.add(new_state)
                db.commit()
                db.refresh(new_state)
                
                print(f"✅ Added State: {state_data['name']} (ID: {new_state.id})")
                added_states += 1
                state_to_use = new_state
            else:
                print(f"⚠️  State already exists: {state_data['name']} (ID: {existing_state.id})")
                state_to_use = existing_state
            
            # Add districts and cities for this state (even if state exists)
            for district_data in state_data["districts"]:
                existing_district = db.query(District).filter(
                    District.name == district_data["name"],
                    District.state_id == state_to_use.id
                ).first()
                
                if not existing_district:
                    new_district = District(
                        name=district_data["name"],
                        state_id=state_to_use.id
                    )
                    db.add(new_district)
                    db.commit()
                    db.refresh(new_district)
                    
                    print(f"   └─ Added District: {district_data['name']} (ID: {new_district.id})")
                    added_districts += 1
                    district_to_use = new_district
                else:
                    district_to_use = existing_district
                
                # Add cities for this district
                if "cities" in district_data:
                    for city_name in district_data["cities"]:
                        existing_city = db.query(City).filter(
                            City.name == city_name,
                            City.district_id == district_to_use.id
                        ).first()
                        
                        if not existing_city:
                            new_city = City(
                                name=city_name,
                                district_id=district_to_use.id
                            )
                            db.add(new_city)
                            db.commit()
                            
                            print(f"      └─ Added City: {city_name}")
                            added_cities += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Summary:")
        print(f"   └─ States Added: {added_states}")
        print(f"   └─ Districts Added: {added_districts}")
        print(f"   └─ Cities Added: {added_cities}")
        print("✅ Telangana and Andhra Pradesh creation complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_telangana_andhra()
