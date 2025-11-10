"""
FastAPI Main Application
Backend API entry point
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from config.settings import settings
from core.security import setup_cors
import traceback
from api.routes import (
    supplier_evaluation,
    risk_profiling,
    fraud_prediction,
    nlp_contract,
    decision_support,
    ethics_compliance,
    transparency,
    gemini
)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# Setup CORS
setup_cors(app, settings.CORS_ORIGINS)

# Include routers
app.include_router(supplier_evaluation.router, prefix="/api/v1/suppliers", tags=["Supplier Evaluation"])
app.include_router(risk_profiling.router, prefix="/api/v1/risk", tags=["Risk Profiling"])
app.include_router(fraud_prediction.router, prefix="/api/v1/fraud", tags=["Fraud Detection"])
app.include_router(nlp_contract.router, prefix="/api/v1/contracts", tags=["NLP Contract"])
app.include_router(decision_support.router, prefix="/api/v1/decision", tags=["Decision Support"])
app.include_router(ethics_compliance.router, prefix="/api/v1/ethics", tags=["Ethics & Compliance"])
app.include_router(transparency.router, prefix="/api/v1/transparency", tags=["Transparency"])
app.include_router(gemini.router, prefix="/api/v1/gemini", tags=["Gemini AI"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Supplier Selection & Risk Management API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": str(request.url),
        "traceback": traceback.format_exc()
    }
    if settings.DEBUG:
        return JSONResponse(status_code=500, content=error_detail)
    else:
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

