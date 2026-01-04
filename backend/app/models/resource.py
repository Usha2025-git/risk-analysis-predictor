"""Resource model."""
from sqlalchemy import Column, String, Float, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class SkillLevel(str, enum.Enum):
    """Skill level enumeration."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXPERT = "expert"


class ResourceStatus(str, enum.Enum):
    """Resource availability status."""
    AVAILABLE = "available"
    ON_LEAVE = "on_leave"
    UNAVAILABLE = "unavailable"


class Resource(Base):
    """Resource/Team member model."""
    __tablename__ = "resources"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    
    # Skill Information
    skill_category = Column(String(100), nullable=False)  # Backend, Frontend, DevOps, QA, etc.
    skill_level = Column(Enum(SkillLevel), default=SkillLevel.MID)
    specializations = Column(Text)  # Comma-separated
    certifications = Column(Text)
    
    # Allocation
    current_allocation = Column(Float, default=0)  # 0-1 (0-100%)
    max_allocation = Column(Float, default=1.0)  # Maximum 100%
    hourly_rate = Column(Float, default=0)
    
    # Availability
    status = Column(Enum(ResourceStatus), default=ResourceStatus.AVAILABLE)
    availability_from = Column(DateTime(timezone=True))
    availability_to = Column(DateTime(timezone=True))
    
    # Performance
    productivity_score = Column(Float)  # 0-1
    quality_score = Column(Float)  # 0-1
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    def __repr__(self):
        return f"<Resource {self.name}>"
