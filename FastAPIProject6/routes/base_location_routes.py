from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import get_db
from models.base_location import Language, State, District, City
from models.news import Category
# Direct imports to avoid package conflicts
from schemas.base_location import (
    CategoryOut, LanguageCreate, LanguageOut, LanguageResponse,
    StateCreate, StateLanguageResponse, StateOut,
    DistrictCreate, DistrictOut,
    CityCreate, CityOut
)

router = APIRouter(prefix="/base", tags=["Base Location"])

# =============================
# Languages
# =============================

@router.post(
    "/languages", 
    response_model=LanguageOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new language"
)
def create_language(
    language: LanguageCreate, 
    db: Session = Depends(get_db)
):
    """Create a new language"""
    # Check if language with same code exists
    db_lang = db.query(Language).filter(
        func.lower(Language.code) == func.lower(language.code)
    ).first()
    if db_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Language already exists"
        )
    
    new_lang = Language(code=language.code.lower(), name=language.name)
    db.add(new_lang)
    db.commit()
    db.refresh(new_lang)
    return new_lang


@router.get(
    "/languages", 
    response_model=List[LanguageOut],
    summary="Get all languages"
)
def get_languages(
    search: Optional[str] = Query(None, description="Search by name or code"),
    limit: int = Query(100, ge=1, le=500, description="Number of records"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """Get all languages with optional search"""
    query = db.query(Language)
    
    if search:
        query = query.filter(
            or_(
                Language.name.ilike(f"%{search}%"),
                Language.code.ilike(f"%{search}%")
            )
        )
    
    query = query.offset(offset).limit(limit)
    return query.all()


@router.get(
    "/languages/{language_id}", 
    response_model=LanguageOut,
    summary="Get language by ID"
)
def get_language(
    language_id: int,
    db: Session = Depends(get_db)
):
    """Get language details by ID"""
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language with id {language_id} not found"
        )
    return language


@router.put(
    "/languages/{language_id}", 
    response_model=LanguageOut,
    summary="Update language"
)
def update_language(
    language_id: int,
    language: LanguageCreate,
    db: Session = Depends(get_db)
):
    """Update language details"""
    db_lang = db.query(Language).filter(Language.id == language_id).first()
    if not db_lang:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language with id {language_id} not found"
        )
    
    # Check for duplicate code if updating
    if language.code and language.code != db_lang.code:
        existing = db.query(Language).filter(
            func.lower(Language.code) == func.lower(language.code)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language with this code already exists"
            )
        db_lang.code = language.code.lower()
    
    if language.name:
        db_lang.name = language.name
    
    db.commit()
    db.refresh(db_lang)
    return db_lang


@router.delete(
    "/languages/{language_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete language"
)
def delete_language(
    language_id: int,
    db: Session = Depends(get_db)
):
    """Delete a language"""
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language with id {language_id} not found"
        )
    
    db.delete(language)
    db.commit()
    return None


# =============================
# States
# =============================

@router.post(
    "/states", 
    response_model=StateOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new state"
)
def create_state(
    state: StateCreate,
    db: Session = Depends(get_db)
):
    """Create a new state"""
    existing = db.query(State).filter(
        func.lower(State.name) == func.lower(state.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="State already exists"
        )
    
    db_state = State(name=state.name)
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state


@router.get(
    "/states", 
    response_model=List[StateOut],
    summary="Get all states"
)
def get_states(
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all states with optional search"""
    query = db.query(State)
    
    if search:
        query = query.filter(State.name.ilike(f"%{search}%"))
    
    query = query.offset(offset).limit(limit)
    return query.all()


@router.get(
    "/states/{state_id}", 
    response_model=StateOut,
    summary="Get state details"
)
def get_state(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Get state details by ID"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with id {state_id} not found"
        )
    return state


@router.put(
    "/states/{state_id}", 
    response_model=StateOut,
    summary="Update state"
)
def update_state(
    state_id: int,
    state: StateCreate,
    db: Session = Depends(get_db)
):
    """Update state details"""
    db_state = db.query(State).filter(State.id == state_id).first()
    if not db_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with id {state_id} not found"
        )
    
    if state.name:
        # Check for duplicate name
        existing = db.query(State).filter(
            func.lower(State.name) == func.lower(state.name),
            State.id != state_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State with this name already exists"
            )
        db_state.name = state.name
    
    db.commit()
    db.refresh(db_state)
    return db_state


@router.delete(
    "/states/{state_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete state"
)
def delete_state(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Delete a state"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with id {state_id} not found"
        )
    
    db.delete(state)
    db.commit()
    return None


# =============================
# Language-State Mapping (Consistent with your original)
# =============================

@router.post(
    "/states/{state_id}/language", 
    status_code=status.HTTP_201_CREATED,
    response_model=LanguageResponse,
    summary="Link language to state"
)
def link_language_to_state(
    state_id: int, 
    language_id: int = Query(..., description="Language ID to link"),
    db: Session = Depends(get_db)
):
    """Link a language to a state"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="State not found"
        )
    
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Language not found"
        )
    
    state.language_id = language.id
    db.commit()
    db.refresh(language)
    return language


@router.get(
    "/states/{state_id}/language", 
    response_model=StateLanguageResponse,
    summary="Get language for a state"
)
def get_state_language(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Get language linked to a state"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="State not found"
        )
    
    if not state.language:
        return StateLanguageResponse(
            state=state,
            language=None,
            message=f"State '{state.name}' does not have a language linked yet."
        )
    
    return StateLanguageResponse(
        state=state,
        language=state.language,
        message=f"Language linked successfully for state '{state.name}'."
    )


@router.delete(
    "/states/{state_id}/language", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink language from state"
)
def unlink_state_language(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Remove language from state"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )
    
    state.language_id = None
    db.commit()
    return None


# =============================
# Districts
# =============================

@router.post(
    "/districts", 
    response_model=DistrictOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new district"
)
def create_district(
    district: DistrictCreate,
    db: Session = Depends(get_db)
):
    """Create a new district"""
    # Verify state exists
    state = db.query(State).filter(State.id == district.state_id).first()
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="State not found"
        )
    
    # Check for duplicate district in same state
    existing = db.query(District).filter(
        func.lower(District.name) == func.lower(district.name),
        District.state_id == district.state_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="District already exists in this state"
        )
    
    db_district = District(name=district.name, state_id=district.state_id)
    db.add(db_district)
    db.commit()
    db.refresh(db_district)
    return db_district


@router.get(
    "/districts", 
    response_model=List[DistrictOut],
    summary="Get all districts"
)
def get_districts(
    state_id: Optional[int] = Query(None, description="Filter by state"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all districts with optional filters"""
    query = db.query(District)
    
    if state_id:
        query = query.filter(District.state_id == state_id)
    
    if search:
        query = query.filter(District.name.ilike(f"%{search}%"))
    
    query = query.offset(offset).limit(limit)
    return query.all()


@router.get(
    "/districts/{district_id}", 
    response_model=DistrictOut,
    summary="Get district details"
)
def get_district(
    district_id: int,
    db: Session = Depends(get_db)
):
    """Get district details by ID"""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with id {district_id} not found"
        )
    return district


@router.put(
    "/districts/{district_id}", 
    response_model=DistrictOut,
    summary="Update district"
)
def update_district(
    district_id: int,
    district: DistrictCreate,
    db: Session = Depends(get_db)
):
    """Update district details"""
    db_district = db.query(District).filter(District.id == district_id).first()
    if not db_district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with id {district_id} not found"
        )
    
    if district.name:
        # Check for duplicate name in same state
        existing = db.query(District).filter(
            func.lower(District.name) == func.lower(district.name),
            District.state_id == db_district.state_id,
            District.id != district_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="District with this name already exists in this state"
            )
        db_district.name = district.name
    
    if district.state_id:
        # Verify new state exists
        state = db.query(State).filter(State.id == district.state_id).first()
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        db_district.state_id = district.state_id
    
    db.commit()
    db.refresh(db_district)
    return db_district


@router.delete(
    "/districts/{district_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete district"
)
def delete_district(
    district_id: int,
    db: Session = Depends(get_db)
):
    """Delete a district"""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with id {district_id} not found"
        )
    
    db.delete(district)
    db.commit()
    return None


# =============================
# Cities
# =============================

@router.post(
    "/cities", 
    response_model=CityOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new city"
)
def create_city(
    city: CityCreate,
    db: Session = Depends(get_db)
):
    """Create a new city"""
    # Verify district exists
    district = db.query(District).filter(District.id == city.district_id).first()
    if not district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="District not found"
        )
    
    # Check for duplicate city in same district
    existing = db.query(City).filter(
        func.lower(City.name) == func.lower(city.name),
        City.district_id == city.district_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City already exists in this district"
        )
    
    db_city = City(name=city.name, district_id=city.district_id)
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


@router.get(
    "/cities", 
    response_model=List[CityOut],
    summary="Get all cities"
)
def get_cities(
    state_id: Optional[int] = Query(None, description="Filter by state"),
    district_id: Optional[int] = Query(None, description="Filter by district"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all cities with optional filters"""
    query = db.query(City)
    
    if district_id:
        query = query.filter(City.district_id == district_id)
    elif state_id:
        query = query.join(City.district).filter(District.state_id == state_id)
    
    if search:
        query = query.filter(City.name.ilike(f"%{search}%"))
    
    query = query.offset(offset).limit(limit)
    return query.all()


@router.get(
    "/cities/{city_id}", 
    response_model=CityOut,
    summary="Get city details"
)
def get_city(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Get city details by ID"""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id {city_id} not found"
        )
    return city


@router.put(
    "/cities/{city_id}", 
    response_model=CityOut,
    summary="Update city"
)
def update_city(
    city_id: int,
    city: CityCreate,
    db: Session = Depends(get_db)
):
    """Update city details"""
    db_city = db.query(City).filter(City.id == city_id).first()
    if not db_city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id {city_id} not found"
        )
    
    if city.name:
        # Check for duplicate name in same district
        existing = db.query(City).filter(
            func.lower(City.name) == func.lower(city.name),
            City.district_id == db_city.district_id,
            City.id != city_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City with this name already exists in this district"
            )
        db_city.name = city.name
    
    if city.district_id:
        # Verify new district exists
        district = db.query(District).filter(District.id == city.district_id).first()
        if not district:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="District not found"
            )
        db_city.district_id = city.district_id
    
    db.commit()
    db.refresh(db_city)
    return db_city


@router.delete(
    "/cities/{city_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete city"
)
def delete_city(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Delete a city"""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City with id {city_id} not found"
        )
    
    db.delete(city)
    db.commit()
    return None


# =============================
# Categories
# =============================

@router.post(
    "/categories", 
    response_model=CategoryOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category"
)
def create_category(
    name: str,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    existing = db.query(Category).filter(
        func.lower(Category.name) == func.lower(name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Category already exists"
        )
    
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get(
    "/categories", 
    response_model=List[CategoryOut],
    summary="Get all categories"
)
def get_all_categories(
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all categories with optional search"""
    query = db.query(Category)
    
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))
    
    query = query.offset(offset).limit(limit)
    return query.all()


@router.put(
    "/categories/{category_id}", 
    response_model=CategoryOut,
    summary="Update category"
)
def update_category(
    category_id: int,
    name: str,
    db: Session = Depends(get_db)
):
    """Update category details"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    if name:
        existing = db.query(Category).filter(
            func.lower(Category.name) == func.lower(name),
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        category.name = name
    
    db.commit()
    db.refresh(category)
    return category


@router.delete(
    "/categories/{category_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    db.delete(category)
    db.commit()
    return None


# =============================
# Search & Stats
# =============================

@router.get(
    "/search", 
    summary="Search locations"
)
def search_locations(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search across all location types"""
    results = []
    
    # Search states
    states = db.query(State).filter(State.name.ilike(f"%{query}%")).limit(limit).all()
    for state in states:
        results.append({
            "id": state.id,
            "name": state.name,
            "type": "state"
        })
    
    # Search districts
    districts = db.query(District).filter(District.name.ilike(f"%{query}%")).limit(limit).all()
    for district in districts:
        results.append({
            "id": district.id,
            "name": district.name,
            "type": "district",
            "state_id": district.state_id
        })
    
    # Search cities
    cities = db.query(City).filter(City.name.ilike(f"%{query}%")).limit(limit).all()
    for city in cities:
        results.append({
            "id": city.id,
            "name": city.name,
            "type": "city",
            "district_id": city.district_id
        })
    
    return results[:limit]


@router.get(
    "/stats", 
    summary="Get location statistics"
)
def get_location_stats(
    db: Session = Depends(get_db)
):
    """Get statistics for locations"""
    return {
        "total_languages": db.query(Language).count(),
        "total_states": db.query(State).count(),
        "total_districts": db.query(District).count(),
        "total_cities": db.query(City).count(),
        "total_categories": db.query(Category).count()
    }