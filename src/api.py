"""
FastAPI REST API endpoints for the Predictive Risk & Resource Management System.
"""
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import io

from src.data_ingestion import create_data_ingestor
from src.embeddings import VectorStore, ProjectEmbedder
from src.agents.risk_agent import create_risk_analyzer
from src.agents.resource_agent import create_resource_optimizer
from src.agents.bottleneck_agent import create_bottleneck_detector
from src.agents.orchestrator import create_orchestrator
from src.utils import AnalysisCache, serialize_analysis

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Predictive Risk & Resource Management System",
    description="AI-powered platform for project risk analysis and resource optimization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache
analysis_cache = AnalysisCache(max_size=1000)

# Global state (in production, use database)
ingestor = None
vector_store = None
embedder = None
risk_analyzer = None
resource_optimizer = None
bottleneck_detector = None
orchestrator = None


# Pydantic models
class ProjectInput(BaseModel):
    """Input model for project analysis."""
    project_id: str
    project_name: str
    industry: str
    team_size: int
    budget: float
    planned_duration_days: int
    project_phase: str = "Development"
    start_date: str = None
    planned_end_date: str = None
    risk_description: Optional[str] = None


class ResourceAllocationInput(BaseModel):
    """Input model for resource optimization."""
    project_id: str
    required_skills: Dict[str, int]
    team_size: int
    priority: str = "Medium"


class WorkflowTask(BaseModel):
    """Model for workflow tasks."""
    name: str
    duration_days: int
    dependencies: List[str] = []
    required_skill: str = "General"


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    project_id: str
    analysis_timestamp: str
    overall_risk_score: float
    confidence_level: float
    risks_count: int
    bottlenecks_count: int
    resource_recommendations_count: int


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    global ingestor, vector_store, embedder, risk_analyzer
    global resource_optimizer, bottleneck_detector, orchestrator
    
    try:
        logger.info("Initializing Predictive Risk & Resource Management System")
        
        # Initialize data ingestor
        ingestor = create_data_ingestor("data")
        projects_df, resources_df, incidents = ingestor.load_all()
        
        # Initialize vector store
        vector_store = VectorStore(embedding_dim=768, persist_dir=".vector_store")
        embedder = ProjectEmbedder(vector_store)
        
        # Process and embed data
        projects_df = ingestor.clean_project_data()
        projects_df = ingestor.add_calculated_fields(projects_df)
        projects_list = projects_df.to_dict('records')
        
        embedder.embed_projects(projects_list)
        embedder.embed_incidents(incidents)
        
        # Initialize agents
        risk_analyzer = create_risk_analyzer(embedder, projects_list, incidents)
        resource_optimizer = create_resource_optimizer(resources_df.to_dict('records'))
        bottleneck_detector = create_bottleneck_detector(projects_list, incidents)
        orchestrator = create_orchestrator(
            risk_analyzer,
            resource_optimizer,
            bottleneck_detector,
            ingestor,
            embedder
        )
        
        logger.info("System initialization completed successfully")
    
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": "Predictive Risk & Resource Management System v1.0"
    }


@app.get("/statistics")
async def get_statistics():
    """Get system statistics."""
    if not ingestor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    stats = ingestor.get_statistics()
    return {
        "total_projects": stats.get('total_projects', 0),
        "total_resources": len(ingestor.resources_df) if ingestor.resources_df is not None else 0,
        "total_incidents": stats.get('total_incidents', 0),
        "avg_budget": stats.get('avg_budget', 0),
        "avg_delay_days": stats.get('avg_delay_days', 0),
        "projects_by_risk_level": stats.get('projects_by_risk_level', {}),
        "industries": stats.get('industries', [])
    }


@app.post("/analyze-project")
async def analyze_project(project: ProjectInput):
    """
    Analyze a new or existing project.
    POST /analyze-project
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        project_data = project.dict()
        
        # Check cache first
        cache_key = f"{project.project_id}_{hash(str(project_data))}"
        cached_result = analysis_cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached analysis for {project.project_id}")
            return cached_result
        
        # Run full analysis
        analysis = orchestrator.analyze_project(
            project_id=project.project_id,
            project_data=project_data
        )
        
        # Prepare response
        response = {
            "project_id": analysis.project_id,
            "analysis_timestamp": analysis.analysis_timestamp,
            "overall_risk_score": analysis.overall_risk_score,
            "confidence_level": analysis.confidence_level,
            "risks": [
                {
                    "type": r.risk_type,
                    "probability": r.probability,
                    "impact": r.impact,
                    "description": r.description,
                    "mitigation": r.mitigation_strategy,
                    "confidence": r.confidence_score
                }
                for r in analysis.risks
            ],
            "bottlenecks": [
                {
                    "task": b.task_name,
                    "severity": b.severity,
                    "expected_delay_days": b.expected_delay_days,
                    "root_cause": b.root_cause,
                    "mitigation": b.mitigation_recommendation
                }
                for b in analysis.bottlenecks
            ],
            "resource_recommendations": [
                {
                    "resource_id": r.resource_id,
                    "resource_name": r.resource_name,
                    "current_allocation": r.current_allocation,
                    "recommended_allocation": r.recommended_allocation,
                    "conflict_risk": r.conflict_risk,
                    "efficiency_gain": r.efficiency_gain
                }
                for r in analysis.resource_recommendations
            ],
            "executive_summary": analysis.executive_summary,
            "top_recommendations": analysis.top_recommendations
        }
        
        # Cache result
        analysis_cache.set(cache_key, response)
        
        return response
    
    except Exception as e:
        logger.error(f"Error analyzing project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk-forecast/{project_id}")
async def get_risk_forecast(project_id: str):
    """
    Get risk predictions for a project.
    GET /risk-forecast/{project_id}
    """
    if not ingestor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        project = ingestor.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        similar = ingestor.get_similar_projects(project_id, limit=5)
        incidents = ingestor.get_incidents_for_project(project_id)
        
        risks = risk_analyzer.analyze_project_risks(project, similar, incidents)
        
        return {
            "project_id": project_id,
            "forecast_timestamp": datetime.now().isoformat(),
            "risks": [
                {
                    "type": r.risk_type,
                    "probability": r.probability,
                    "impact": r.impact,
                    "description": r.description,
                    "mitigation": r.mitigation_strategy,
                    "confidence": r.confidence_score
                }
                for r in risks
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting risk forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize-resources")
async def optimize_resources(request: ResourceAllocationInput):
    """
    Get resource allocation recommendations.
    POST /optimize-resources
    """
    if not resource_optimizer:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        recommendations = resource_optimizer.optimize_allocation(
            project_id=request.project_id,
            project_requirements=request.dict(exclude={'project_id'})
        )
        
        return {
            "project_id": request.project_id,
            "timestamp": datetime.now().isoformat(),
            "recommendations": [
                {
                    "resource_id": r.resource_id,
                    "resource_name": r.resource_name,
                    "current_allocation": r.current_allocation,
                    "recommended_allocation": r.recommended_allocation,
                    "justification": r.justification,
                    "conflict_risk": r.conflict_risk,
                    "efficiency_gain": r.efficiency_gain
                }
                for r in recommendations
            ]
        }
    
    except Exception as e:
        logger.error(f"Error optimizing resources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bottlenecks/{project_id}")
async def get_bottlenecks(project_id: str):
    """
    Identify workflow bottlenecks.
    GET /bottlenecks/{project_id}
    """
    if not bottleneck_detector or not ingestor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        project = ingestor.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        similar = ingestor.get_similar_projects(project_id, limit=5)
        
        bottlenecks = bottleneck_detector.analyze_project_bottlenecks(
            project_id,
            project,
            similar_projects=similar
        )
        
        return {
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "bottlenecks": [
                {
                    "task_name": b.task_name,
                    "severity": b.severity,
                    "expected_delay_days": b.expected_delay_days,
                    "root_cause": b.root_cause,
                    "mitigation_recommendation": b.mitigation_recommendation,
                    "parallel_opportunity": b.parallel_task_opportunity
                }
                for b in bottlenecks
            ]
        }
    
    except Exception as e:
        logger.error(f"Error identifying bottlenecks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """
    Upload historical project data.
    POST /upload-data
    """
    if not ingestor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        contents = await file.read()
        
        # TODO: Process uploaded file and update vector store
        
        return {
            "message": f"Data upload received: {file.filename}",
            "size": len(contents),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error uploading data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/similar-projects/{project_id}")
async def get_similar_projects(project_id: str, limit: int = 5):
    """
    Get similar historical projects.
    GET /similar-projects/{project_id}
    """
    if not ingestor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        project = ingestor.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        similar = ingestor.get_similar_projects(project_id, limit=limit)
        
        return {
            "project_id": project_id,
            "similar_projects": [
                {
                    "project_id": p.get('project_id'),
                    "project_name": p.get('project_name'),
                    "industry": p.get('industry'),
                    "budget": p.get('budget'),
                    "actual_cost": p.get('actual_cost'),
                    "delays_days": p.get('delays_days'),
                    "team_size": p.get('team_size')
                }
                for p in similar
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting similar projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/incidents/{project_id}")
async def get_incidents(project_id: str):
    """
    Get historical incidents for a project.
    GET /incidents/{project_id}
    """
    if not ingestor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        incidents = ingestor.get_incidents_for_project(project_id)
        
        return {
            "project_id": project_id,
            "incidents": [
                {
                    "incident_id": i.get('incident_id'),
                    "severity": i.get('severity'),
                    "category": i.get('category'),
                    "description": i.get('description'),
                    "impact": i.get('impact'),
                    "resolution": i.get('resolution')
                }
                for i in incidents
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resource-utilization")
async def get_resource_utilization():
    """
    Get current resource utilization analysis.
    GET /resource-utilization
    """
    if not resource_optimizer:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        utilization = resource_optimizer.analyze_utilization()
        bottlenecks = resource_optimizer.identify_bottlenecks()
        suggestions = resource_optimizer.suggest_reallocation()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "utilization": utilization,
            "bottlenecks": bottlenecks,
            "reallocation_suggestions": suggestions
        }
    
    except Exception as e:
        logger.error(f"Error getting resource utilization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
