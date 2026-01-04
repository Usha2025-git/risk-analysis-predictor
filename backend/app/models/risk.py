"""Risk model."""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from backend.app.database import Base
import enum


class RiskSeverity(str, enum.Enum):
    """Risk severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, enum.Enum):
    """Risk category enumeration."""
    SCHEDULE = "schedule"
    BUDGET = "budget"
    RESOURCE = "resource"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    VENDOR = "vendor"
    OTHER = "other"


class RiskStatus(str, enum.Enum):
    """Risk status enumeration."""
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Risk(Base):
    """Risk model."""
    __tablename__ = "risks"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    
    # Risk Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(Enum(RiskCategory), nullable=False)
    severity = Column(Enum(RiskSeverity), default=RiskSeverity.MEDIUM, index=True)
    status = Column(Enum(RiskStatus), default=RiskStatus.IDENTIFIED)
    
    # Risk Assessment
    probability = Column(Float, default=0.5)  # 0-1
    impact = Column(Float, default=0.5)  # 0-1
    risk_score = Column(Float)  # probability * impact * 100
    
    # Mitigation
    mitigation_strategy = Column(Text)
    mitigation_owner = Column(String(255))
    mitigation_deadline = Column(DateTime(timezone=True))
    
    # Historical Context
    similar_incidents = Column(Integer, default=0)
    occurrence_frequency = Column(String(50))  # rare, occasional, frequent
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    def __repr__(self):
        return f"<Risk {self.title}>"
