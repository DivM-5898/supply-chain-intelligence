"""
Conversational AI Service
GPT-4 and Claude API integration for natural language supplier queries
"""

import os
from typing import Dict, List, Optional, Any
import openai
from anthropic import Anthropic
from config.settings import settings
import json


class ConversationalAIService:
    """Service for conversational AI using GPT-4 and Claude"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize Anthropic client if API key is available
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def _get_supplier_context(self) -> str:
        """Get context about suppliers for AI responses"""
        return """
        You are an AI assistant for a Supplier Selection & Risk Management Platform.
        The platform helps companies evaluate suppliers using:
        - 7 ML models (XGBoost, Random Forest, Gradient Boosting, SVM, Neural Networks, AdaBoost, Ensemble)
        - Risk profiling and anomaly detection
        - Fraud prediction
        - Contract analysis using NLP
        - Multi-criteria decision support (TOPSIS, AHP)
        - Ethics & compliance scoring
        - Transparency and resilience metrics
        
        You can answer questions about:
        - Supplier evaluation and scoring
        - Risk assessment
        - Fraud detection
        - Contract analysis
        - Decision support algorithms
        - Compliance and ethics
        - Supply chain transparency
        
        Always provide accurate, helpful information based on the platform's capabilities.
        """
    
    async def chat_gpt4(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        supplier_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with GPT-4
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            supplier_context: Additional context about suppliers
            
        Returns:
            Response dictionary with answer and metadata
        """
        if not self.openai_client:
            return {
                "error": "OpenAI API key not configured",
                "model": "gpt-4",
                "answer": None
            }
        
        try:
            # Prepare messages
            messages = []
            
            # Add system message with context
            system_context = self._get_supplier_context()
            if supplier_context:
                system_context += f"\n\nAdditional Context: {supplier_context}"
            
            messages.append({
                "role": "system",
                "content": system_context
            })
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call GPT-4
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            return {
                "model": "gpt-4",
                "answer": answer,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "error": None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "model": "gpt-4",
                "answer": None
            }
    
    async def chat_claude(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        supplier_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with Claude
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            supplier_context: Additional context about suppliers
            
        Returns:
            Response dictionary with answer and metadata
        """
        if not self.anthropic_client:
            return {
                "error": "Anthropic API key not configured",
                "model": "claude-3-opus-20240229",
                "answer": None
            }
        
        try:
            # Prepare messages
            system_context = self._get_supplier_context()
            if supplier_context:
                system_context += f"\n\nAdditional Context: {supplier_context}"
            
            # Build message list
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call Claude
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=system_context,
                messages=messages
            )
            
            answer = response.content[0].text
            
            return {
                "model": "claude-3-opus-20240229",
                "answer": answer,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "error": None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "model": "claude-3-opus-20240229",
                "answer": None
            }
    
    async def chat_unified(
        self,
        message: str,
        model_preference: str = "auto",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        supplier_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unified chat interface that tries multiple models
        
        Args:
            message: User message
            model_preference: "gpt-4", "claude", or "auto"
            conversation_history: Previous conversation messages
            supplier_context: Additional context about suppliers
            
        Returns:
            Response dictionary with answer and metadata
        """
        # Try GPT-4 first if preferred or auto
        if model_preference in ["gpt-4", "auto"]:
            if self.openai_client:
                result = await self.chat_gpt4(message, conversation_history, supplier_context)
                if not result.get("error"):
                    return result
        
        # Try Claude if GPT-4 failed or Claude preferred
        if model_preference in ["claude", "auto"]:
            if self.anthropic_client:
                result = await self.chat_claude(message, conversation_history, supplier_context)
                if not result.get("error"):
                    return result
        
        # If both failed, return error
        return {
            "error": "No AI models available. Please configure API keys.",
            "model": None,
            "answer": None
        }
    
    async def query_supplier(
        self,
        query: str,
        supplier_id: Optional[str] = None,
        supplier_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query about specific supplier
        
        Args:
            query: Natural language query
            supplier_id: Supplier ID
            supplier_data: Supplier data dictionary
            
        Returns:
            Response with supplier-specific answer
        """
        # Build supplier context
        supplier_context = ""
        if supplier_data:
            supplier_context = f"Supplier Data: {json.dumps(supplier_data, indent=2)}"
        elif supplier_id:
            supplier_context = f"Supplier ID: {supplier_id}"
        
        # Use unified chat
        return await self.chat_unified(
            message=query,
            supplier_context=supplier_context
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        models = []
        if self.openai_client:
            models.append("gpt-4")
        if self.anthropic_client:
            models.append("claude-3-opus-20240229")
        return models


# Singleton instance
conversational_ai_service = ConversationalAIService()

