"""
Google Gemini AI Service
Integration with Gemini 2.5 Flash for intelligent analysis
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Any
import os
import sys
import json
import pandas as pd

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from utils.data_loader import data_loader


class GeminiService:
    """Service for Google Gemini AI integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', 'AIzaSyA8b_9uzdOv7NLxYx4VV88SPHU4pPf65-Y')
        genai.configure(api_key=self.api_key)
        # Try gemini-2.0-flash-exp first, fallback to gemini-1.5-flash
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.model_name = 'gemini-2.0-flash-exp'
        except Exception:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.model_name = 'gemini-1.5-flash'
            except Exception:
                self.model = genai.GenerativeModel('gemini-pro')
                self.model_name = 'gemini-pro'
    
    def analyze_contract_with_gemini(self, contract_text: str) -> Dict:
        """Analyze contract using Gemini AI"""
        try:
            prompt = f"""
            Analyze the following supplier contract and provide:
            1. Key terms and conditions
            2. Risk factors (high/medium/low)
            3. Payment terms and deadlines
            4. Termination clauses
            5. Liability and warranty information
            6. Compliance requirements
            7. Overall risk assessment (1-10 scale)
            8. Recommendations
            
            Contract Text:
            {contract_text[:8000]}  # Limit to avoid token limits
            
            Provide your analysis in JSON format with the following structure:
            {{
                "risk_level": "high/medium/low",
                "risk_score": 1-10,
                "key_terms": ["term1", "term2"],
                "payment_terms": "description",
                "termination_clauses": ["clause1", "clause2"],
                "liability_info": "description",
                "compliance_requirements": ["req1", "req2"],
                "recommendations": ["rec1", "rec2"],
                "summary": "brief summary"
            }}
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                else:
                    # Fallback: create structured response from text
                    result_json = {
                        "risk_level": "medium",
                        "risk_score": 5,
                        "key_terms": [],
                        "payment_terms": "",
                        "termination_clauses": [],
                        "liability_info": "",
                        "compliance_requirements": [],
                        "recommendations": [],
                        "summary": result_text[:500],
                        "full_analysis": result_text
                    }
            except json.JSONDecodeError:
                result_json = {
                    "risk_level": "medium",
                    "risk_score": 5,
                    "summary": result_text[:500],
                    "full_analysis": result_text
                }
            
            return {
                "gemini_analysis": result_json,
                "model_used": self.model_name,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def get_supplier_recommendations(self, supplier_data: Dict, context: str = "") -> Dict:
        """Get AI-powered supplier recommendations"""
        try:
            prompt = f"""
            Based on the following supplier data, provide intelligent recommendations:
            
            Supplier Data:
            {json.dumps(supplier_data, indent=2)}
            
            Context: {context}
            
            Provide recommendations in JSON format:
            {{
                "overall_assessment": "assessment text",
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"],
                "recommendations": ["rec1", "rec2"],
                "risk_factors": ["risk1", "risk2"],
                "action_items": ["action1", "action2"],
                "confidence_score": 0-1
            }}
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            try:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                else:
                    result_json = {
                        "overall_assessment": result_text[:300],
                        "recommendations": [],
                        "full_response": result_text
                    }
            except json.JSONDecodeError:
                result_json = {
                    "overall_assessment": result_text[:300],
                    "full_response": result_text
                }
            
            return {
                "recommendations": result_json,
                "model_used": self.model_name,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def analyze_risk_with_gemini(self, supplier_id: str, risk_data: Dict) -> Dict:
        """Analyze supplier risk using Gemini AI"""
        try:
            prompt = f"""
            Analyze the risk profile for supplier {supplier_id}:
            
            Risk Data:
            {json.dumps(risk_data, indent=2)}
            
            Provide comprehensive risk analysis in JSON:
            {{
                "risk_summary": "summary text",
                "primary_risks": ["risk1", "risk2"],
                "mitigation_strategies": ["strategy1", "strategy2"],
                "monitoring_recommendations": ["rec1", "rec2"],
                "risk_level": "high/medium/low",
                "confidence": 0-1
            }}
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            try:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                else:
                    result_json = {
                        "risk_summary": result_text[:300],
                        "full_analysis": result_text
                    }
            except json.JSONDecodeError:
                result_json = {
                    "risk_summary": result_text[:300],
                    "full_analysis": result_text
                }
            
            return {
                "risk_analysis": result_json,
                "model_used": self.model_name,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def generate_supplier_report(self, supplier_ids: List[str], report_type: str = "comprehensive") -> Dict:
        """Generate comprehensive supplier report using Gemini"""
        try:
            # Load supplier data
            suppliers_df = data_loader.load_suppliers()
            selected_suppliers = suppliers_df[suppliers_df['supplier_id'].isin(supplier_ids)]
            
            if selected_suppliers.empty:
                return {"error": "No suppliers found", "success": False}
            
            supplier_data = selected_suppliers.to_dict('records')
            
            prompt = f"""
            Generate a {report_type} supplier evaluation report for the following suppliers:
            
            Supplier Data:
            {json.dumps(supplier_data[:5], indent=2)}  # Limit to first 5 for token management
            
            Provide a comprehensive report in JSON format:
            {{
                "executive_summary": "summary text",
                "key_findings": ["finding1", "finding2"],
                "supplier_comparison": {{
                    "best_overall": "supplier_id",
                    "best_cost": "supplier_id",
                    "best_quality": "supplier_id",
                    "best_reliability": "supplier_id"
                }},
                "recommendations": ["rec1", "rec2"],
                "risk_assessment": "assessment text",
                "next_steps": ["step1", "step2"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            try:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                else:
                    result_json = {
                        "executive_summary": result_text[:500],
                        "full_report": result_text
                    }
            except json.JSONDecodeError:
                result_json = {
                    "executive_summary": result_text[:500],
                    "full_report": result_text
                }
            
            return {
                "report": result_json,
                "model_used": self.model_name,
                "suppliers_analyzed": len(supplier_data),
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def answer_natural_language_query(self, query: str, context_data: Dict = None) -> Dict:
        """Answer natural language questions about suppliers"""
        try:
            context_str = ""
            if context_data:
                context_str = f"\n\nContext Data:\n{json.dumps(context_data, indent=2)}"
            
            prompt = f"""
            Answer the following question about supplier management:
            
            Question: {query}
            {context_str}
            
            Provide a clear, concise answer. If you need specific data, indicate what data would be needed.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "answer": response.text,
                "model_used": self.model_name,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }


# Global instance
gemini_service = GeminiService()

