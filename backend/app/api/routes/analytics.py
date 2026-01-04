"""Analytics routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import math

from app.database import get_db
from app.models import Project, Risk, Resource
from app.schemas import DashboardStats, AnalyticsResponse
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard statistics."""
    try:
        # Count projects by status
        total_projects = db.query(func.count(Project.id)).scalar() or 0
        active_projects = db.query(func.count(Project.id)).filter(
            Project.status == "active"
        ).scalar() or 0
        completed_projects = db.query(func.count(Project.id)).filter(
            Project.status == "completed"
        ).scalar() or 0
        
        # Calculate average metrics
        avg_health = db.query(func.avg(Project.health_score)).scalar() or 0
        avg_success_prob = db.query(func.avg(Project.success_probability)).scalar() or 0
        
        # Count risks by severity
        high_risk_count = db.query(func.count(Risk.id)).filter(
            Risk.severity == "critical"
        ).scalar() or 0
        medium_risk_count = db.query(func.count(Risk.id)).filter(
            Risk.severity == "high"
        ).scalar() or 0
        
        # Calculate overall risk
        all_risks = db.query(Risk).all()
        overall_risk_score = sum([r.risk_score for r in all_risks]) / len(all_risks) if all_risks else 0
        
        # Resource utilization
        total_resources = db.query(func.count(Resource.id)).scalar() or 0
        avg_allocation = db.query(func.avg(Resource.current_allocation)).scalar() or 0
        
        return DashboardStats(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            average_health_score=round(avg_health, 2),
            average_success_probability=round(avg_success_prob, 2),
            high_risk_projects=high_risk_count,
            critical_risks=high_risk_count,
            total_resources=total_resources,
            average_resource_utilization=round(avg_allocation * 100, 2),
            overall_risk_score=round(overall_risk_score, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/trends", response_model=AnalyticsResponse)
async def get_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get risk and project trends."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get projects created in range
        projects_created = db.query(func.count(Project.id)).filter(
            Project.created_at >= start_date
        ).scalar() or 0
        
        # Get risks created in range
        risks_created = db.query(func.count(Risk.id)).filter(
            Risk.created_at >= start_date
        ).scalar() or 0
        
        # Get completed projects in range
        projects_completed = db.query(func.count(Project.id)).filter(
            Project.status == "completed",
            Project.updated_at >= start_date
        ).scalar() or 0
        
        # Calculate success rate
        recent_projects = db.query(Project).filter(
            Project.created_at >= start_date
        ).all()
        success_rate = 0
        if recent_projects:
            completed = sum(1 for p in recent_projects if p.status == "completed")
            success_rate = round((completed / len(recent_projects)) * 100, 2)
        
        # Get risk trends
        high_severity_risks = db.query(func.count(Risk.id)).filter(
            Risk.severity == "critical",
            Risk.created_at >= start_date
        ).scalar() or 0
        
        # Average risk score trend
        recent_risks = db.query(Risk).filter(
            Risk.created_at >= start_date
        ).all()
        avg_risk_trend = sum([r.risk_score for r in recent_risks]) / len(recent_risks) if recent_risks else 0
        
        return AnalyticsResponse(
            time_period=f"Last {days} days",
            projects_created=projects_created,
            projects_completed=projects_completed,
            success_rate=success_rate,
            risks_identified=risks_created,
            high_severity_risks=high_severity_risks,
            average_risk_score=round(avg_risk_trend, 2),
            total_data_points=projects_created + risks_created,
            recommendations=[
                "Monitor high-severity risks closely",
                "Allocate resources to at-risk projects",
                "Review completed projects for lessons learned"
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/predictions/success-rate")
async def predict_success_rate(
    project_id: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict project success rate."""
    try:
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            success_prob = project.success_probability or 0.7
        else:
            # Calculate average for all projects
            all_projects = db.query(Project).all()
            success_prob = sum([p.success_probability for p in all_projects]) / len(all_projects) if all_projects else 0.7
        
        return {
            "project_id": project_id,
            "predicted_success_rate": round(success_prob * 100, 2),
            "confidence_level": "high" if success_prob > 0.8 else "medium" if success_prob > 0.5 else "low",
            "risk_factors": [
                "Resource constraints",
                "Schedule risks",
                "Technical complexity"
            ],
            "recommendations": [
                "Increase team size if possible",
                "Add buffer to schedule",
                "Implement risk mitigation strategies"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/bottlenecks")
async def identify_bottlenecks(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Identify project bottlenecks and resource constraints."""
    try:
        bottlenecks = []
        
        # Find over-allocated resources
        resources = db.query(Resource).all()
        for resource in resources:
            if resource.current_allocation > resource.max_allocation:
                bottlenecks.append({
                    "type": "Over-allocation",
                    "resource_id": resource.id,
                    "resource_name": resource.name,
                    "current": resource.current_allocation,
                    "max": resource.max_allocation,
                    "severity": "high"
                })
        
        # Find high-risk projects with low resources
        high_risk_projects = db.query(Project).filter(
            Project.risk_level == "high"
        ).all()
        
        for project in high_risk_projects:
            # Count assigned resources
            project_resources = db.query(Resource).filter(
                Resource.current_allocation > 0
            ).count()
            
            if project_resources < project.team_size * 0.7:
                bottlenecks.append({
                    "type": "Resource shortage",
                    "project_id": project.id,
                    "project_name": project.name,
                    "required": project.team_size,
                    "assigned": project_resources,
                    "severity": "high"
                })
        
        # Find at-risk resources (low performance)
        underperforming = db.query(Resource).filter(
            Resource.productivity_score < 0.6
        ).all()
        
        for resource in underperforming:
            bottlenecks.append({
                "type": "Performance issue",
                "resource_id": resource.id,
                "resource_name": resource.name,
                "productivity_score": resource.productivity_score,
                "severity": "medium"
            })
        
        return {
            "bottleneck_count": len(bottlenecks),
            "bottlenecks": bottlenecks,
            "critical_count": sum(1 for b in bottlenecks if b["severity"] == "high"),
            "recommendations": [
                "Review resource allocation strategy",
                "Redistribute workload to match capacity",
                "Consider hiring or training additional resources"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
