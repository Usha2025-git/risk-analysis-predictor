"""Resource routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.models import Resource
from app.schemas import Resource as ResourceSchema, ResourceCreate, ResourceUpdate
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ResourceSchema)
async def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new resource."""
    # Check if resource with email already exists
    existing = db.query(Resource).filter(Resource.email == resource_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource with this email already exists"
        )
    
    db_resource = Resource(
        id=str(uuid.uuid4()),
        **resource_data.dict()
    )
    
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    
    return db_resource


@router.get("/", response_model=List[ResourceSchema])
async def list_resources(
    skill_category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all resources with optional filters."""
    query = db.query(Resource)
    
    if skill_category:
        query = query.filter(Resource.skill_category == skill_category)
    
    if status:
        query = query.filter(Resource.status == status)
    
    resources = query.offset(skip).limit(limit).all()
    return resources


@router.get("/{resource_id}", response_model=ResourceSchema)
async def get_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get resource by ID."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return resource


@router.put("/{resource_id}", response_model=ResourceSchema)
async def update_resource(
    resource_id: str,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Update fields
    update_data = resource_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    db.commit()
    db.refresh(resource)
    
    return resource


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    db.delete(resource)
    db.commit()
    
    return {"detail": "Resource deleted successfully"}


@router.post("/{resource_id}/allocate")
async def allocate_resource(
    resource_id: str,
    allocation: float,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Allocate a resource to a project."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Validate allocation
    if allocation < 0 or allocation > resource.max_allocation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Allocation must be between 0 and {resource.max_allocation}"
        )
    
    resource.current_allocation = allocation
    db.commit()
    db.refresh(resource)
    
    return {
        "resource_id": resource_id,
        "current_allocation": resource.current_allocation,
        "max_allocation": resource.max_allocation
    }
