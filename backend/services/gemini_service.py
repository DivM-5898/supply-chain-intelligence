"""
Google Gemini AI Service
Integration with Gemini 2.5 Flash for intelligent analysis
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Any, Tuple
import os
import sys
import json
import pandas as pd
import time
import re

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from utils.data_loader import data_loader


class GeminiService:
    """Service for Google Gemini AI integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', 'AIzaSyCEkfJRwoFvdBKh6RP-gGlil80dxm4CGo8')
        genai.configure(api_key=self.api_key)
        
        # List available models first to help debug
        try:
            available_models = [m.name for m in genai.list_models()]
            print(f"Available Gemini models: {', '.join(available_models[:5])}...")
        except Exception as e:
            print(f"Could not list models: {e}")
        
        # Try different model names - prioritize 2.5 Flash and 2.0 Flash
        # Common model names for Flash models
        models_to_try = [
            ('gemini-2.5-flash', 'gemini-2.5-flash'),  # 2.5 Flash
            ('models/gemini-2.5-flash', 'gemini-2.5-flash'),
            ('gemini-2.0-flash-exp', 'gemini-2.0-flash-exp'),  # 2.0 Flash experimental
            ('models/gemini-2.0-flash-exp', 'gemini-2.0-flash-exp'),
            ('gemini-2.0-flash', 'gemini-2.0-flash'),  # 2.0 Flash stable
            ('models/gemini-2.0-flash', 'gemini-2.0-flash'),
            ('gemini-1.5-flash', 'gemini-1.5-flash'),  # Fallback to 1.5 Flash
            ('models/gemini-1.5-flash', 'gemini-1.5-flash'),
            ('gemini-pro', 'gemini-pro'),  # Last resort fallback
        ]
        
        self.model = None
        self.model_name = None
        
        for model_id, model_display_name in models_to_try:
            try:
                self.model = genai.GenerativeModel(model_id)
                self.model_name = model_display_name
                print(f"[OK] Successfully loaded Gemini model: {self.model_name}")
                break
            except Exception as e:
                error_msg = str(e)[:150]
                print(f"[FAIL] Failed to load {model_id}: {error_msg}")
                continue
        
        if self.model is None:
            raise Exception("Could not initialize any Gemini Flash model (2.5 Flash or 2.0 Flash). Please check your API key and ensure Flash models are available in your region.")
    
    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text"""
        import re
        # Remove markdown bold/italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic*
        text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__
        text = re.sub(r'_([^_]+)_', r'\1', text)  # _italic_
        
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Replace markdown bullet points with plain text
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # Replace numbered markdown lists with plain numbered lists
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _is_quota_error(self, error: Exception) -> Tuple[bool, Optional[float]]:
        """Check if error is a quota error and extract retry delay"""
        error_str = str(error)
        if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
            # Extract retry delay from error message
            retry_match = re.search(r'retry.*?(\d+\.?\d*)\s*s', error_str, re.IGNORECASE)
            retry_seconds = float(retry_match.group(1)) if retry_match else 60.0
            return True, retry_seconds
        return False, None
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content with retry logic for quota errors"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                is_quota, retry_delay = self._is_quota_error(e)
                if is_quota and attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                    print(f"Quota exceeded. Waiting {wait_time:.1f} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        raise Exception("Max retries exceeded")
    
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
    
    def explain_ranking_rationale(self, csv_data: str, model_type: str, results: List[Dict], file_name: str = None) -> Dict:
        """Explain ranking rationale using Gemini 2.5 Flash"""
        try:
            # Format results for analysis (limit to top 5 to reduce tokens)
            top_suppliers = results[:5] if len(results) > 5 else results
            results_summary = "\n".join([
                f"Rank {r.get('rank', idx+1)}: {r.get('supplier_id', 'N/A')} - Score: {r.get('predicted_score', 0):.4f}"
                for idx, r in enumerate(top_suppliers)
            ])
            
            # Limit CSV data to reduce token usage
            csv_sample = csv_data[:300] if len(csv_data) > 300 else csv_data
            
            prompt = f"""You are an AI assistant analyzing supplier rankings from a machine learning model.

**Context:**
- Model Used: {model_type}
- File Analyzed: {file_name or 'Uploaded CSV'}
- Total Suppliers Ranked: {len(results)}

**Top Ranked Suppliers:**
{results_summary}

**CSV Data Sample:**
{csv_sample}

**Task:**
Provide a detailed, professional explanation of why these suppliers are ranked in this order. Your explanation should:

1. Explain the ranking logic: Why did the {model_type} model rank suppliers this way?
2. Identify key factors: What features/metrics most influenced the rankings?
3. Highlight top performers: What makes the top-ranked suppliers stand out?
4. Explain score differences: Why are there differences between supplier scores?
5. Provide insights: What patterns or trends do you notice in the rankings?
6. Give actionable recommendations: What should decision-makers focus on?

**IMPORTANT FORMATTING REQUIREMENTS:**
- Write in clear, professional plain text format
- Do NOT use markdown formatting (no asterisks, no bold, no bullet points with symbols)
- Do NOT use special characters like *, **, -, #, etc.
- Use simple numbered lists or plain paragraphs
- Write in a formal business report style
- Keep it concise and professional
- Use proper sentence structure and paragraphs
"""
            
            rationale = self._generate_with_retry(prompt)
            # Clean markdown formatting
            rationale = self._clean_markdown(rationale)
            
            return {
                "rationale": rationale,
                "model_used": self.model_name,
                "model_type": model_type,
                "total_suppliers": len(results),
                "success": True
            }
        except Exception as e:
            import traceback
            error_str = str(e)
            is_quota, retry_delay = self._is_quota_error(e)
            
            if is_quota:
                user_message = f"API quota exceeded. Please wait {int(retry_delay)} seconds and try again. Free tier has limited requests per minute."
            else:
                user_message = f"Error generating rationale: {error_str[:200]}"
            
            return {
                "error": user_message,
                "error_type": "quota_exceeded" if is_quota else "general_error",
                "retry_after": int(retry_delay) if is_quota else None,
                "traceback": traceback.format_exc(),
                "success": False
            }
    
    def chat_about_rankings(self, message: str, csv_data: str, model_type: str, results: List[Dict]) -> Dict:
        """Chat about rankings with context"""
        try:
            # Format results summary (limit to top 5 to reduce tokens)
            top_suppliers = results[:5] if len(results) > 5 else results
            results_summary = "\n".join([
                f"Rank {r.get('rank', idx+1)}: {r.get('supplier_id', 'N/A')} - Score: {r.get('predicted_score', 0):.4f}"
                for idx, r in enumerate(top_suppliers)
            ])
            
            # Limit CSV data to reduce token usage
            csv_sample = csv_data[:200] if len(csv_data) > 200 else csv_data
            
            prompt = f"""You are an AI assistant helping users understand supplier rankings from a machine learning model.

**Context:**
- Model Used: {model_type}
- Total Suppliers: {len(results)}

**Top Ranked Suppliers:**
{results_summary}

**CSV Data Sample:**
{csv_sample}

**User Question:**
{message}

**Instructions:**
Answer the user's question about the supplier rankings. Be helpful, specific, and reference the actual data when possible. If the question is about specific suppliers, mention their ranks and scores.

**IMPORTANT FORMATTING REQUIREMENTS:**
- Write in clear, professional plain text format
- Do NOT use markdown formatting (no asterisks, no bold, no bullet points with symbols)
- Do NOT use special characters like *, **, -, #, etc.
- Use simple numbered lists or plain paragraphs
- Write in a formal business report style
- Keep your response concise and professional
- Use proper sentence structure and paragraphs
"""
            
            answer = self._generate_with_retry(prompt)
            # Clean markdown formatting
            answer = self._clean_markdown(answer)
            
            return {
                "response": answer,
                "model_used": self.model_name,
                "success": True
            }
        except Exception as e:
            import traceback
            error_str = str(e)
            is_quota, retry_delay = self._is_quota_error(e)
            
            if is_quota:
                user_message = f"API quota exceeded. Please wait {int(retry_delay)} seconds and try again. Free tier has limited requests per minute."
            else:
                user_message = f"Error generating response: {error_str[:200]}"
            
            return {
                "error": user_message,
                "error_type": "quota_exceeded" if is_quota else "general_error",
                "retry_after": int(retry_delay) if is_quota else None,
                "traceback": traceback.format_exc(),
                "success": False
            }

    def explain_risk_analysis(self, csv_data: str, risk_results: List[Dict], anomaly_results: List[Dict], file_name: str = None) -> Dict:
        """Explain risk analysis and anomaly detection using Gemini"""
        try:
            # Format results for analysis (limit to top 10)
            top_risks = risk_results[:10] if len(risk_results) > 10 else risk_results
            top_anomalies = [a for a in anomaly_results if a.get('is_anomaly', False)][:10]
            
            risks_summary = "\n".join([
                f"Supplier {r.get('supplier_id', 'N/A')}: {r.get('risk_level', 'Unknown')} risk (Probability: {r.get('risk_probability', 0):.2%})"
                for r in top_risks
            ]) if top_risks else "No risk predictions available"
            
            anomalies_summary = "\n".join([
                f"Supplier {a.get('supplier_id', 'N/A')}: {a.get('severity', 'Unknown')} severity - {a.get('anomaly_reason', 'Anomaly detected')}"
                for a in top_anomalies
            ]) if top_anomalies else "No anomalies detected"
            
            # Limit CSV data to reduce token usage
            csv_sample = csv_data[:300] if len(csv_data) > 300 else csv_data
            
            prompt = f"""You are an AI assistant analyzing supplier risk predictions and anomaly detection results.

**Context:**
- File Analyzed: {file_name or 'Uploaded CSV'}
- Total Suppliers Analyzed: {len(risk_results)}
- Anomalies Detected: {len([a for a in anomaly_results if a.get('is_anomaly', False)])}

**Top Risk Predictions:**
{risks_summary}

**Detected Anomalies:**
{anomalies_summary}

**CSV Data Sample:**
{csv_sample}

**Task:**
Provide a detailed, professional explanation of the risk analysis and anomaly detection results. Your explanation should:

1. Explain the overall risk profile: What patterns do you see in the risk predictions?
2. Identify high-risk suppliers: Which suppliers pose the highest risk and why?
3. Explain anomalies: What makes the detected anomalies significant?
4. Analyze correlations: Are there relationships between risk levels and anomalies?
5. Provide insights: What patterns or trends do you notice?
6. Give actionable recommendations: What should decision-makers focus on?

**IMPORTANT FORMATTING REQUIREMENTS:**
- Write in clear, professional plain text format
- Do NOT use markdown formatting (no asterisks, no bold, no bullet points with symbols)
- Do NOT use special characters like *, **, -, #, etc.
- Use simple numbered lists or plain paragraphs
- Write in a formal business report style
- Keep it concise and professional
- Use proper sentence structure and paragraphs
"""
            
            rationale = self._generate_with_retry(prompt)
            rationale = self._clean_markdown(rationale)
            
            return {
                "rationale": rationale,
                "model_used": self.model_name,
                "total_suppliers": len(risk_results),
                "anomalies_detected": len([a for a in anomaly_results if a.get('is_anomaly', False)]),
                "success": True
            }
        except Exception as e:
            import traceback
            error_str = str(e)
            is_quota, retry_delay = self._is_quota_error(e)
            
            if is_quota:
                user_message = f"API quota exceeded. Please wait {int(retry_delay)} seconds and try again. Free tier has limited requests per minute."
            else:
                user_message = f"Error generating rationale: {error_str[:200]}"
            
            return {
                "error": user_message,
                "error_type": "quota_exceeded" if is_quota else "general_error",
                "retry_after": int(retry_delay) if is_quota else None,
                "traceback": traceback.format_exc(),
                "success": False
            }
    
    def chat_about_risks(self, message: str, csv_data: str, risk_results: List[Dict], anomaly_results: List[Dict]) -> Dict:
        """Chat about risks and anomalies with context"""
        try:
            # Format results summary (limit to top 5)
            top_risks = risk_results[:5] if len(risk_results) > 5 else risk_results
            top_anomalies = [a for a in anomaly_results if a.get('is_anomaly', False)][:5]
            
            risks_summary = "\n".join([
                f"Supplier {r.get('supplier_id', 'N/A')}: {r.get('risk_level', 'Unknown')} risk"
                for r in top_risks
            ]) if top_risks else "No risk predictions"
            
            anomalies_summary = "\n".join([
                f"Supplier {a.get('supplier_id', 'N/A')}: {a.get('anomaly_reason', 'Anomaly')}"
                for a in top_anomalies
            ]) if top_anomalies else "No anomalies"
            
            # Limit CSV data to reduce token usage
            csv_sample = csv_data[:200] if len(csv_data) > 200 else csv_data
            
            prompt = f"""You are an AI assistant helping users understand supplier risk analysis and anomaly detection.

**Context:**
- Total Suppliers: {len(risk_results)}
- Anomalies Detected: {len([a for a in anomaly_results if a.get('is_anomaly', False)])}

**Top Risk Predictions:**
{risks_summary}

**Detected Anomalies:**
{anomalies_summary}

**CSV Data Sample:**
{csv_sample}

**User Question:**
{message}

**Instructions:**
Answer the user's question about the risk analysis and anomalies. Be helpful, specific, and reference the actual data when possible.

**IMPORTANT FORMATTING REQUIREMENTS:**
- Write in clear, professional plain text format
- Do NOT use markdown formatting (no asterisks, no bold, no bullet points with symbols)
- Do NOT use special characters like *, **, -, #, etc.
- Use simple numbered lists or plain paragraphs
- Write in a formal business report style
- Keep your response concise and professional
- Use proper sentence structure and paragraphs
"""
            
            answer = self._generate_with_retry(prompt)
            answer = self._clean_markdown(answer)
            
            return {
                "response": answer,
                "model_used": self.model_name,
                "success": True
            }
        except Exception as e:
            import traceback
            error_str = str(e)
            is_quota, retry_delay = self._is_quota_error(e)
            
            if is_quota:
                user_message = f"API quota exceeded. Please wait {int(retry_delay)} seconds and try again. Free tier has limited requests per minute."
            else:
                user_message = f"Error generating response: {error_str[:200]}"
            
            return {
                "error": user_message,
                "error_type": "quota_exceeded" if is_quota else "general_error",
                "retry_after": int(retry_delay) if is_quota else None,
                "traceback": traceback.format_exc(),
                "success": False
            }

    def explain_contract_analysis(self, contract_text: str, analysis_results: Dict, file_name: str = None, input_method: str = None) -> Dict:
        """Explain contract analysis results and provide document overview using Gemini"""
        try:
            # Format analysis summary
            summary = analysis_results.get('summary', {})
            entities = analysis_results.get('entities', {})
            clauses = analysis_results.get('clauses', {})
            risk_terms = analysis_results.get('risk_terms', {})
            
            # Create summary text
            analysis_summary = f"""
Analysis Summary:
- Total Entities Found: {summary.get('total_entities', 0)}
- Key Clauses Found: {summary.get('key_clauses_found', 0)}
- Overall Sentiment: {summary.get('overall_sentiment', 'N/A')}
- Risk Level: {summary.get('risk_level', 'N/A')}
- Total Risk Terms: {summary.get('total_risk_terms', 0)}

Key Entities:
- Organizations: {len(entities.get('organizations', []))}
- Dates: {len(entities.get('dates', []))}
- Money Values: {len(entities.get('money', []))}

Key Clauses:
- Termination: {len(clauses.get('termination', []))}
- Payment: {len(clauses.get('payment', []))}
- Liability: {len(clauses.get('liability', []))}
- Warranty: {len(clauses.get('warranty', []))}

Risk Terms:
- High Risk: {len(risk_terms.get('high_risk', []))}
- Medium Risk: {len(risk_terms.get('medium_risk', []))}
- Low Risk: {len(risk_terms.get('low_risk', []))}
"""
            
            # Limit contract text to reduce token usage
            contract_sample = contract_text[:500] if len(contract_text) > 500 else contract_text
            
            prompt = f"""You are an AI assistant analyzing contract documents and their analysis results.

**Context:**
- File Name: {file_name or 'Contract Document'}
- Input Method: {input_method or 'Unknown'}

**Contract Text Sample (first 500 characters):**
{contract_sample}

**Analysis Results:**
{analysis_summary}

**Task:**
Provide a comprehensive explanation that includes:

1. **Document Overview**: Write a brief paragraph (3-5 sentences) explaining what this document is about. Describe the type of contract, main parties involved, primary purpose, and key subject matter.

2. **Analysis Rationale**: Explain the analysis results in detail:
   - What do the extracted entities tell us about the contract?
   - What are the key clauses and why are they important?
   - What does the sentiment analysis indicate about the contract tone?
   - What are the risk implications based on the identified risk terms?
   - Are there any concerning patterns or notable features?

3. **Key Insights**: Highlight the most important findings from the analysis.

4. **Recommendations**: Provide actionable recommendations based on the analysis.

**IMPORTANT FORMATTING REQUIREMENTS:**
- Write in clear, professional plain text format
- Do NOT use markdown formatting (no asterisks, no bold, no bullet points with symbols)
- Do NOT use special characters like *, **, -, #, etc.
- Use simple numbered lists or plain paragraphs
- Write in a formal business report style
- Keep it concise and professional
- Use proper sentence structure and paragraphs
- Start with the document overview paragraph, then provide the detailed analysis
"""
            
            rationale = self._generate_with_retry(prompt)
            rationale = self._clean_markdown(rationale)
            
            return {
                "rationale": rationale,
                "model_used": self.model_name,
                "file_name": file_name,
                "success": True
            }
        except Exception as e:
            import traceback
            error_str = str(e)
            is_quota, retry_delay = self._is_quota_error(e)
            
            if is_quota:
                user_message = f"API quota exceeded. Please wait {int(retry_delay)} seconds and try again. Free tier has limited requests per minute."
            else:
                user_message = f"Error generating rationale: {error_str[:200]}"
            
            return {
                "error": user_message,
                "error_type": "quota_exceeded" if is_quota else "general_error",
                "retry_after": int(retry_delay) if is_quota else None,
                "traceback": traceback.format_exc(),
                "success": False
            }
    
    def chat_about_contract(self, message: str, contract_text: str, analysis_results: Dict) -> Dict:
        """Chat about contract analysis with context"""
        try:
            # Format analysis summary (limit to key points)
            summary = analysis_results.get('summary', {})
            analysis_summary = f"""
- Entities: {summary.get('total_entities', 0)}
- Clauses: {summary.get('key_clauses_found', 0)}
- Sentiment: {summary.get('overall_sentiment', 'N/A')}
- Risk Level: {summary.get('risk_level', 'N/A')}
"""
            
            # Limit contract text to reduce token usage
            contract_sample = contract_text[:300] if len(contract_text) > 300 else contract_text
            
            prompt = f"""You are an AI assistant helping users understand contract analysis results.

**Context:**
- Total Entities: {summary.get('total_entities', 0)}
- Key Clauses: {summary.get('key_clauses_found', 0)}
- Risk Level: {summary.get('risk_level', 'N/A')}

**Contract Text Sample:**
{contract_sample}

**Analysis Summary:**
{analysis_summary}

**User Question:**
{message}

**Instructions:**
Answer the user's question about the contract analysis. Be helpful, specific, and reference the actual analysis results when possible.

**IMPORTANT FORMATTING REQUIREMENTS:**
- Write in clear, professional plain text format
- Do NOT use markdown formatting (no asterisks, no bold, no bullet points with symbols)
- Do NOT use special characters like *, **, -, #, etc.
- Use simple numbered lists or plain paragraphs
- Write in a formal business report style
- Keep your response concise and professional
- Use proper sentence structure and paragraphs
"""
            
            answer = self._generate_with_retry(prompt)
            answer = self._clean_markdown(answer)
            
            return {
                "response": answer,
                "model_used": self.model_name,
                "success": True
            }
        except Exception as e:
            import traceback
            error_str = str(e)
            is_quota, retry_delay = self._is_quota_error(e)
            
            if is_quota:
                user_message = f"API quota exceeded. Please wait {int(retry_delay)} seconds and try again. Free tier has limited requests per minute."
            else:
                user_message = f"Error generating response: {error_str[:200]}"
            
            return {
                "error": user_message,
                "error_type": "quota_exceeded" if is_quota else "general_error",
                "retry_after": int(retry_delay) if is_quota else None,
                "traceback": traceback.format_exc(),
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

