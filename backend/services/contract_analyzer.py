"""
NLP Contract Analyzer Service
BERT and spaCy for contract analysis and risk extraction
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
import os
import sys

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)
from utils.data_loader import data_loader

# Try to import transformers (may fail on Windows due to TensorFlow DLL issues)
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    TRANSFORMERS_AVAILABLE = True
except (ImportError, Exception) as e:
    TRANSFORMERS_AVAILABLE = False
    AutoTokenizer = None
    AutoModelForSequenceClassification = None
    pipeline = None
    print(f"Warning: transformers not available ({str(e)[:100]}), some NLP features will be limited")

# Try to import spaCy
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None
    displacy = None
    print("Warning: spaCy not available, some NLP features will be limited")

# Import Gemini service for enhanced analysis
try:
    from services.gemini_service import gemini_service
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    gemini_service = None


class ContractAnalyzerService:
    """Service for analyzing contracts using NLP"""
    
    def __init__(self):
        self.bert_model = None
        self.bert_tokenizer = None
        self.nlp = None
        self.sentiment_analyzer = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models"""
        try:
            # Load spaCy model
            if SPACY_AVAILABLE and spacy:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    print("spaCy model not found. Please install: python -m spacy download en_core_web_sm")
                    self.nlp = None
            else:
                self.nlp = None
            
            # Load BERT model for sentiment/classification
            if TRANSFORMERS_AVAILABLE and AutoTokenizer and AutoModelForSequenceClassification:
                try:
                    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
                    self.bert_tokenizer = AutoTokenizer.from_pretrained(model_name)
                    self.bert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
                    if pipeline:
                        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                                          model=self.bert_model,
                                                          tokenizer=self.bert_tokenizer)
                except Exception as e:
                    print(f"Could not load BERT model: {e}")
                    self.sentiment_analyzer = None
            else:
                self.sentiment_analyzer = None
        
        except Exception as e:
            print(f"Error loading NLP models: {e}")
    
    def extract_entities(self, contract_text: str) -> Dict:
        """Extract named entities from contract using spaCy"""
        if not self.nlp:
            # Fallback: simple regex-based extraction
            entities = {
                'organizations': re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|LLC|Ltd|Corp|Company)\b', contract_text),
                'persons': [],
                'dates': re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', contract_text),
                'money': re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', contract_text),
                'percentages': re.findall(r'\d+(?:\.\d+)?%', contract_text),
                'locations': []
            }
            return entities
        
        doc = self.nlp(contract_text)
        
        entities = {
            'organizations': [],
            'persons': [],
            'dates': [],
            'money': [],
            'percentages': [],
            'locations': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ == 'PERSON':
                entities['persons'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entities['money'].append(ent.text)
            elif ent.label_ == 'PERCENT':
                entities['percentages'].append(ent.text)
            elif ent.label_ in ['GPE', 'LOC']:
                entities['locations'].append(ent.text)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def extract_clauses(self, contract_text: str) -> Dict:
        """Extract key clauses from contract"""
        clauses = {
            'termination': [],
            'payment': [],
            'liability': [],
            'warranty': [],
            'confidentiality': []
        }
        
        patterns = {
            'termination': [r'terminat', r'cancel', r'end\s+agreement'],
            'payment': [r'payment', r'invoice', r'due\s+date', r'payable'],
            'liability': [r'liability', r'indemnif', r'damages'],
            'warranty': [r'warranty', r'guarantee', r'warrant'],
            'confidentiality': [r'confidential', r'non-disclosure', r'proprietary']
        }
        
        sentences = re.split(r'[.!?]+', contract_text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for clause_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, sentence_lower, re.IGNORECASE):
                        clauses[clause_type].append(sentence.strip())
                        break
        
        # Remove duplicates
        for key in clauses:
            clauses[key] = list(set(clauses[key]))
        
        return clauses
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of contract text"""
        if not self.sentiment_analyzer:
            # Fallback to simple rule-based sentiment
            positive_words = ['agree', 'benefit', 'favorable', 'advantage', 'protect']
            negative_words = ['penalty', 'breach', 'terminate', 'liability', 'risk']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return {'label': 'POSITIVE', 'score': 0.6}
            elif negative_count > positive_count:
                return {'label': 'NEGATIVE', 'score': 0.6}
            else:
                return {'label': 'NEUTRAL', 'score': 0.5}
        
        # Use BERT for sentiment analysis
        max_length = 512
        if len(text) > max_length:
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            results = [self.sentiment_analyzer(chunk)[0] for chunk in chunks]
            avg_score = np.mean([r['score'] for r in results])
            label = 'POSITIVE' if avg_score > 0.5 else 'NEGATIVE'
            return {'label': label, 'score': avg_score}
        else:
            result = self.sentiment_analyzer(text)[0]
            return {'label': result['label'], 'score': result['score']}
    
    def identify_risk_terms(self, contract_text: str) -> Dict:
        """Identify risky terms in contract"""
        risk_terms = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': []
        }
        
        risk_patterns = {
            'high_risk': [
                r'unlimited\s+liability',
                r'no\s+warranty',
                r'immediate\s+termination',
                r'exclusive\s+liability',
                r'indemnif[ication|y]\s+for\s+all'
            ],
            'medium_risk': [
                r'penalty\s+of\s+\d+%',
                r'late\s+delivery',
                r'force\s+majeure',
                r'liability\s+cap',
                r'termination\s+without\s+notice'
            ],
            'low_risk': [
                r'standard\s+warranty',
                r'standard\s+terms',
                r'mutual\s+agreement',
                r'good\s+faith'
            ]
        }
        
        for risk_level, patterns in risk_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, contract_text, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(contract_text), match.end() + 50)
                    context = contract_text[start:end]
                    risk_terms[risk_level].append({
                        'term': match.group(),
                        'context': context
                    })
        
        return risk_terms
    
    def analyze_contract(self, contract_text: str) -> Dict:
        """Comprehensive contract analysis combining NLP and Gemini AI"""
        analysis = {
            'entities': self.extract_entities(contract_text),
            'clauses': self.extract_clauses(contract_text),
            'sentiment': self.analyze_sentiment(contract_text),
            'risk_terms': self.identify_risk_terms(contract_text)
        }
        
        # Add Gemini AI analysis if available
        if GEMINI_AVAILABLE and gemini_service:
            try:
                gemini_analysis = gemini_service.analyze_contract_with_gemini(contract_text)
                if gemini_analysis.get('success'):
                    analysis['gemini_analysis'] = gemini_analysis.get('gemini_analysis', {})
                    analysis['ai_enhanced'] = True
            except Exception as e:
                print(f"Gemini analysis failed: {e}")
                analysis['ai_enhanced'] = False
        
        # Create summary
        analysis['summary'] = {
            'total_entities': sum(len(v) for v in analysis['entities'].values() if isinstance(v, list)),
            'key_clauses_found': sum(len(v) for v in analysis['clauses'].values()),
            'overall_sentiment': analysis['sentiment']['label'],
            'risk_level': 'HIGH' if len(analysis['risk_terms']['high_risk']) > 0 else
                         'MEDIUM' if len(analysis['risk_terms']['medium_risk']) > 0 else 'LOW',
            'total_risk_terms': sum(len(v) for v in analysis['risk_terms'].values())
        }
        
        return analysis
    
    def analyze_contract_by_id(self, contract_id: str) -> Dict:
        """Analyze contract by ID"""
        try:
            contract_text = data_loader.load_contract(contract_id)
            if contract_text is None:
                return {'error': f'Contract {contract_id} not found'}
            
            return self.analyze_contract(contract_text)
        except Exception as e:
            return {'error': str(e)}


# Global instance
contract_analyzer_service = ContractAnalyzerService()
