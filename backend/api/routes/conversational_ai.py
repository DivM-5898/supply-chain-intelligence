"""
API Routes for Conversational AI
GPT-4 and Claude integration endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from services.conversational_ai import conversational_ai_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    model_preference: Optional[str] = "auto"  # "gpt-4", "claude", or "auto"
    conversation_history: Optional[List[Dict[str, str]]] = None
    supplier_context: Optional[str] = None


class SupplierQueryRequest(BaseModel):
    query: str
    supplier_id: Optional[str] = None
    supplier_data: Optional[Dict] = None


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with GPT-4 or Claude AI
    
    Args:
        request: Chat request with message and preferences
        
    Returns:
        AI response with answer and metadata
    """
    try:
        result = await conversational_ai_service.chat_unified(
            message=request.message,
            model_preference=request.model_preference,
            conversation_history=request.conversation_history,
            supplier_context=request.supplier_context
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "model": result["model"],
            "answer": result["answer"],
            "usage": result.get("usage", {}),
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-supplier")
async def query_supplier(request: SupplierQueryRequest):
    """
    Query about specific supplier using AI
    
    Args:
        request: Query request with supplier information
        
    Returns:
        AI response with supplier-specific answer
    """
    try:
        result = await conversational_ai_service.query_supplier(
            query=request.query,
            supplier_id=request.supplier_id,
            supplier_data=request.supplier_data
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "model": result["model"],
            "answer": result["answer"],
            "usage": result.get("usage", {}),
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """
    Get list of available AI models
    
    Returns:
        List of available models
    """
    try:
        models = conversational_ai_service.get_available_models()
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

