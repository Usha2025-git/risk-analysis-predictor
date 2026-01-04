"""Project model."""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Enum
from sqlalchemy.sql import func
from backend.app.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(Base):
    """Project model."""
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    industry = Column(String(100))
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, index=True)
    
    # Dates
    start_date = Column(DateTime(timezone=True))
    planned_end_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Team
    team_size = Column(Integer, default=5)
    project_manager = Column(String(255))
    
    # Budget
    budget = Column(Float, default=0)
    actual_cost = Column(Float, default=0)
    
    # Risk & Performance
    risk_level = Column(String(50))  # Low, Medium, High, Critical
    overall_health_score = Column(Float, nullable=True)  # 0-100
    success_probability = Column(Float, nullable=True)  # 0-100
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    def __repr__(self):
        return f"<Project {self.name}>"
