"""Pydantic schemas for validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    team_size: int = Field(default=5, ge=1)
    budget: float = Field(default=0, ge=0)
    start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    actual_cost: Optional[float] = None
    actual_end_date: Optional[datetime] = None


class Project(ProjectBase):
    id: str
    status: str
    actual_cost: float
    actual_end_date: Optional[datetime]
    risk_level: Optional[str]
    overall_health_score: Optional[float]
    success_probability: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectAnalysisResponse(BaseModel):
    project_id: str
    risks: List[dict]
    resources: dict
    bottlenecks: List[dict]
    recommendations: List[dict]
    overall_risk_score: float
    success_probability: float


# Risk Schemas
class RiskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    severity: str = "medium"
    probability: float = Field(default=0.5, ge=0, le=1)
    impact: float = Field(default=0.5, ge=0, le=1)


class RiskCreate(RiskBase):
    project_id: str
    mitigation_strategy: Optional[str] = None
    mitigation_owner: Optional[str] = None


class Risk(RiskBase):
    id: str
    project_id: str
    status: str
    risk_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Resource Schemas
class ResourceBase(BaseModel):
    name: str
    email: EmailStr
    skill_category: str
    skill_level: str = "mid"
    current_allocation: float = Field(default=0, ge=0, le=1)
    max_allocation: float = Field(default=1.0, ge=0, le=1)
    hourly_rate: float = Field(default=0, ge=0)


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    current_allocation: Optional[float] = None
    status: Optional[str] = None


class Resource(ResourceBase):
    id: str
    status: str
    productivity_score: Optional[float]
    quality_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class DashboardStats(BaseModel):
    activeProjects: int
    highRiskProjects: int
    utilization: float
    successRate: float
    riskData: List[dict]
    resourceData: List[dict]
    projects: List[dict]
    alerts: List[dict]


class AnalyticsResponse(BaseModel):
    timestamp: datetime
    total_projects: int
    total_resources: int
    total_incidents: int
    avg_budget: float
    avg_delay_days: float
    projects_by_risk_level: dict
    industries: List[str]
