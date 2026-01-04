"""Project routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.models import Project, ProjectStatus
from app.schemas import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
    ProjectAnalysisResponse
)
from app.api.dependencies import get_current_user
from app.core.websocket import manager

router = APIRouter()


@router.post("", response_model=ProjectSchema)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new project."""
    db_project = Project(
        id=str(uuid.uuid4()),
        **project_data.dict()
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Notify via WebSocket
    await manager.broadcast_to_subscriptions("project_created", {
        "project_id": db_project.id,
        "project_name": db_project.name
    })
    
    return db_project


@router.get("", response_model=List[ProjectSchema])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all projects with optional filters."""
    query = db.query(Project)
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    update_data = project_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
    
    return {"detail": "Project deleted successfully"}


@router.post("/{project_id}/analyze", response_model=ProjectAnalysisResponse)
async def analyze_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Analyze a project with AI agents."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # TODO: Implement AI analysis
    # This would integrate with the orchestrator agent
    
    return {
        "project_id": project_id,
        "risks": [],
        "resources": {},
        "bottlenecks": [],
        "recommendations": [],
        "overall_risk_score": 0.0,
        "success_probability": 1.0
    }
