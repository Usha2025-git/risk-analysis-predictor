"""Risk routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.models import Risk, Project
from app.schemas import Risk as RiskSchema, RiskCreate
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=RiskSchema)
async def create_risk(
    risk_data: RiskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new risk for a project."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == risk_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Calculate risk score
    risk_score = risk_data.probability * risk_data.impact * 100
    
    db_risk = Risk(
        id=str(uuid.uuid4()),
        risk_score=risk_score,
        **risk_data.dict()
    )
    
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    
    return db_risk


@router.get("/", response_model=List[RiskSchema])
async def list_risks(
    project_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all risks with optional filters."""
    query = db.query(Risk)
    
    if project_id:
        query = query.filter(Risk.project_id == project_id)
    
    if severity:
        query = query.filter(Risk.severity == severity)
    
    risks = query.offset(skip).limit(limit).all()
    return risks


@router.get("/{risk_id}", response_model=RiskSchema)
async def get_risk(
    risk_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get risk by ID."""
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    
    return risk


@router.put("/{risk_id}", response_model=RiskSchema)
async def update_risk(
    risk_id: str,
    risk_update: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a risk."""
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    
    # Update fields
    for field, value in risk_update.items():
        if value is not None:
            setattr(risk, field, value)
    
    # Recalculate risk score if probability or impact changed
    if 'probability' in risk_update or 'impact' in risk_update:
        risk.risk_score = risk.probability * risk.impact * 100
    
    db.commit()
    db.refresh(risk)
    
    return risk


@router.delete("/{risk_id}")
async def delete_risk(
    risk_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a risk."""
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    
    db.delete(risk)
    db.commit()
    
    return {"detail": "Risk deleted successfully"}
