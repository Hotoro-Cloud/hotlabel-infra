from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

# Create FastAPI application
app = FastAPI(
    title="HotLabel",
    description="Crowdsourced Data Labeling Solution",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "name": "HotLabel",
        "version": "0.1.0",
        "description": "Crowdsourced Data Labeling Solution",
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )