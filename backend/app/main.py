"""Main FastAPI application."""
from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import uuid

from backend.app.config import settings
from backend.app.database import init_db, get_db
from backend.app.core.websocket import manager
from backend.app.api.routes import auth, projects, risks, resources, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Project Risk & Resource Management System",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

app.include_router(
    projects.router,
    prefix=f"{settings.API_V1_STR}/projects",
    tags=["Projects"]
)

app.include_router(
    risks.router,
    prefix=f"{settings.API_V1_STR}/risks",
    tags=["Risks"]
)

app.include_router(
    resources.router,
    prefix=f"{settings.API_V1_STR}/resources",
    tags=["Resources"]
)

app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_STR}/analytics",
    tags=["Analytics"]
)


# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle subscription requests
            if data.get("action") == "subscribe":
                manager.subscribe(client_id, data.get("event_type"))
            
            elif data.get("action") == "unsubscribe":
                manager.unsubscribe(client_id, data.get("event_type"))
            
            # Broadcast to other clients
            else:
                await manager.broadcast({
                    "client_id": client_id,
                    "message": data
                }, exclude=client_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        manager.disconnect(client_id)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Predictive PM System API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
