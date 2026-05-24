"""
Enhanced Location Routes for Hyperlocal News Application
Missing critical endpoints for location data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any

from database import get_db
from models.base_location import State, District, City
from models.news import News

router = APIRouter(prefix="/location", tags=["Location Enhanced"])

@router.get("/states")
def get_all_states(
    db: Session = Depends(get_db)
):
    """
    Get all states with news count
    """
    try:
        states = db.query(State).all()
        
        states_data = []
        for state in states:
            # Count news in this state
            news_count = db.query(News).join(City, News.city_id == City.id).join(
                District, City.district_id == District.id
            ).filter(
                and_(District.state_id == state.id, News.is_approved == 1)
            ).count()
            
            states_data.append({
                "id": state.id,
                "name": state.name,
                "language_id": state.language_id,
                "news_count": news_count
            })
        
        return {
            "success": True,
            "states": sorted(states_data, key=lambda x: x["name"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get states: {str(e)}")

@router.get("/states/{state_id}/districts")
def get_districts_in_state(
    state_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all districts in a state
    """
    try:
        # Verify state exists
        state = db.query(State).filter(State.id == state_id).first()
        if not state:
            raise HTTPException(status_code=404, detail="State not found")
        
        districts = db.query(District).filter(District.state_id == state_id).all()
        
        districts_data = []
        for district in districts:
            # Count news in this district
            news_count = db.query(News).join(City, News.city_id == City.id).filter(
                and_(City.district_id == district.id, News.is_approved == 1)
            ).count()
            
            districts_data.append({
                "id": district.id,
                "name": district.name,
                "state_id": district.state_id,
                "state_name": state.name,
                "news_count": news_count
            })
        
        return {
            "success": True,
            "state": {
                "id": state.id,
                "name": state.name
            },
            "districts": sorted(districts_data, key=lambda x: x["name"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get districts: {str(e)}")

@router.get("/districts/{district_id}/cities")
def get_cities_in_district(
    district_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all cities in a district
    """
    try:
        # Verify district exists
        district = db.query(District).filter(District.id == district_id).first()
        if not district:
            raise HTTPException(status_code=404, detail="District not found")
        
        cities = db.query(City).filter(City.district_id == district_id).all()
        
        cities_data = []
        for city in cities:
            # Count news in this city
            news_count = db.query(News).filter(
                and_(News.city_id == city.id, News.is_approved == 1)
            ).count()
            
            cities_data.append({
                "id": city.id,
                "name": city.name,
                "district_id": city.district_id,
                "district_name": district.name,
                "news_count": news_count
            })
        
        return {
            "success": True,
            "district": {
                "id": district.id,
                "name": district.name,
                "state_id": district.state_id
            },
            "cities": sorted(cities_data, key=lambda x: x["name"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cities: {str(e)}")

@router.get("/stats")
def get_location_stats(
    db: Session = Depends(get_db)
):
    """
    Get location statistics
    """
    try:
        # Count states, districts, cities
        total_states = db.query(State).count()
        total_districts = db.query(District).count()
        total_cities = db.query(City).count()
        
        # News distribution by location
        news_by_state = db.query(
            State.name,
            func.count(News.id).label('news_count')
        ).join(City, News.city_id == City.id).join(
            District, City.district_id == District.id
        ).join(State, District.state_id == State.id).filter(
            News.is_approved == 1
        ).group_by(State.id, State.name).order_by(
            func.count(News.id).desc()
        ).all()
        
        # Top active locations
        top_states = [{"name": state[0], "news_count": state[1]} for state in news_by_state[:5]]
        
        return {
            "success": True,
            "location_counts": {
                "states": total_states,
                "districts": total_districts,
                "cities": total_cities
            },
            "news_distribution": {
                "top_states": top_states,
                "total_news_with_location": sum(state[1] for state in news_by_state)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location stats: {str(e)}")

@router.get("/search")
def search_locations(
    q: str = Query(..., min_length=2, description="Search query"),
    search_type: str = Query("all", description="Search type: states, districts, cities, all"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db)
):
    """
    Search locations by name
    """
    try:
        results = []
        
        if search_type in ["all", "states"]:
            states = db.query(State).filter(State.name.ilike(f"%{q}%")).limit(limit).all()
            for state in states:
                results.append({
                    "type": "state",
                    "id": state.id,
                    "name": state.name,
                    "language_id": state.language_id
                })
        
        if search_type in ["all", "districts"]:
            districts = db.query(District).join(State).filter(
                District.name.ilike(f"%{q}%")
            ).limit(limit).all()
            for district in districts:
                results.append({
                    "type": "district",
                    "id": district.id,
                    "name": district.name,
                    "state_id": district.state_id,
                    "state_name": district.state.name if district.state else None
                })
        
        if search_type in ["all", "cities"]:
            cities = db.query(City).join(District).join(State).filter(
                City.name.ilike(f"%{q}%")
            ).limit(limit).all()
            for city in cities:
                results.append({
                    "type": "city",
                    "id": city.id,
                    "name": city.name,
                    "district_id": city.district_id,
                    "district_name": city.district.name if city.district else None,
                    "state_name": city.district.state.name if city.district and city.district.state else None
                })
        
        # Sort by relevance (exact matches first)
        results.sort(key=lambda x: (x["name"].lower() != q.lower(), len(x["name"])))
        
        return {
            "success": True,
            "query": q,
            "search_type": search_type,
            "results": results[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search locations: {str(e)}")
