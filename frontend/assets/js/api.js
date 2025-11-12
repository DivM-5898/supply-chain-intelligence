// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api/v1',
    TIMEOUT: 30000
};

// API Client
// Make APIClient globally available
window.APIClient = class APIClient {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        try {
            console.log(`[API] Requesting: ${url}`, config);
            const response = await fetch(url, config);
            
            console.log(`[API] Response status: ${response.status}`, response);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`[API] Error response:`, errorText);
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch {
                    errorData = { detail: errorText };
                }
                
                // Handle 429 quota errors specifically
                if (response.status === 429) {
                    const error = new Error(errorData.detail?.message || errorData.error || 'Quota exceeded');
                    error.status = 429;
                    error.detail = errorData.detail || errorData;
                    throw error;
                }
                
                const error = new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
                error.status = response.status;
                error.detail = errorData.detail || errorData;
                throw error;
            }
            
            const data = await response.json();
            console.log(`[API] Success:`, data);
            return data;
        } catch (error) {
            console.error('[API] Request failed:', {
                url,
                error: error.message,
                stack: error.stack
            });
            throw error;
        }
    }

    // Supplier Evaluation
    async evaluateSuppliers(supplierIds = null, modelType = 'xgboost') {
        return this.request('/suppliers/evaluate', {
            method: 'POST',
            body: JSON.stringify({ supplier_ids: supplierIds, model_type: modelType })
        });
    }

    async compareSupplierModels(supplierIds = null, models = null) {
        let params = [];
        if (supplierIds) params.push(`supplier_ids=${supplierIds.join(',')}`);
        if (models) params.push(`models=${models}`);
        const queryString = params.length > 0 ? `?${params.join('&')}` : '';
        return this.request(`/suppliers/compare-models${queryString}`);
    }

    async getAvailableModels() {
        return this.request('/suppliers/available-models');
    }

    async getFeatureImportance(modelType) {
        return this.request(`/suppliers/feature-importance/${modelType}`);
    }

    async uploadAndEvaluate(file, modelType = 'xgboost', topN = null) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('model_type', modelType);
        if (topN !== null && topN !== undefined) {
            formData.append('top_n', topN.toString());
        }
        
        console.log('[API] Uploading file:', file.name, 'Model:', modelType, 'TopN:', topN);
        
        try {
            const response = await fetch(`${this.baseURL}/suppliers/upload-and-evaluate`, {
                method: 'POST',
                body: formData
            });
            
            console.log('[API] Upload response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('[API] Upload error response:', errorText);
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch {
                    errorData = { detail: errorText };
                }
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('[API] Upload success:', data);
            return data;
        } catch (error) {
            console.error('[API] Upload request failed:', error);
            throw error;
        }
    }

    // Risk Profiling
    async predictRisk(supplierIds = null) {
        return this.request('/risk/predict', {
            method: 'POST',
            body: JSON.stringify({ supplier_ids: supplierIds })
        });
    }

    async detectAnomalies(supplierIds = null) {
        return this.request('/risk/anomalies', {
            method: 'POST',
            body: JSON.stringify({ supplier_ids: supplierIds })
        });
    }

    async getDataSources() {
        return this.request('/risk/data-sources');
    }

    async getRiskAnalysisRationale(data) {
        return this.request('/gemini/risk-analysis-rationale', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async chatAboutRisks(data) {
        return this.request('/gemini/chat-risks', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Fraud Detection
    async predictFraud(supplierIds = null, modelType = 'random_forest') {
        return this.request('/fraud/predict', {
            method: 'POST',
            body: JSON.stringify({ supplier_ids: supplierIds, model_type: modelType })
        });
    }

    async compareFraudModels(supplierIds = null) {
        return this.request('/fraud/compare-models', {
            method: 'POST',
            body: JSON.stringify({ supplier_ids: supplierIds })
        });
    }

    async getContractAnalysisRationale(data) {
        return this.request('/gemini/contract-analysis-rationale', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async chatAboutContract(data) {
        return this.request('/gemini/chat-contract', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // NLP Contract
    async analyzeContract(contractText = null, contractId = null) {
        return this.request('/contracts/analyze', {
            method: 'POST',
            body: JSON.stringify({ contract_text: contractText, contract_id: contractId })
        });
    }

    async uploadContract(file) {
        const formData = new FormData();
        formData.append('file', file);
        return fetch(`${this.baseURL}/contracts/upload`, {
            method: 'POST',
            body: formData
        }).then(res => res.json());
    }

    async listContracts() {
        return this.request('/contracts/contracts');
    }

    // Decision Support
    async topsisRanking(criteriaWeights, benefitCriteria = null, supplierIds = null) {
        return this.request('/decision/topsis', {
            method: 'POST',
            body: JSON.stringify({
                criteria_weights: criteriaWeights,
                benefit_criteria: benefitCriteria,
                supplier_ids: supplierIds
            })
        });
    }

    async ahpRanking(criteria, pairwiseComparisons, supplierIds = null) {
        return this.request('/decision/ahp', {
            method: 'POST',
            body: JSON.stringify({
                criteria: criteria,
                pairwise_comparisons: pairwiseComparisons,
                supplier_ids: supplierIds
            })
        });
    }

    // Ethics & Compliance
    async explainPrediction(supplierId, modelType = 'xgboost', explanationType = 'lime') {
        return this.request('/ethics/explain', {
            method: 'POST',
            body: JSON.stringify({
                supplier_id: supplierId,
                model_type: modelType,
                explanation_type: explanationType
            })
        });
    }

    async getShapValues(supplierIds, modelType = 'xgboost') {
        return this.request('/ethics/shap-values', {
            method: 'POST',
            body: JSON.stringify({ supplier_ids: supplierIds, model_type: modelType })
        });
    }

    async detectBias(featureName, modelType = 'xgboost') {
        return this.request('/ethics/bias-detection', {
            method: 'POST',
            body: JSON.stringify({ feature_name: featureName, model_type: modelType })
        });
    }

    async getESGScores() {
        return this.request('/ethics/esg-scores');
    }

    // Transparency
    async getGeographicRisk() {
        return this.request('/transparency/geographic-risk');
    }

    async getSupplierNetwork() {
        return this.request('/transparency/supplier-network');
    }

    async getResilienceMetrics() {
        return this.request('/transparency/resilience-metrics');
    }

    async getTransparencyScores() {
        return this.request('/transparency/transparency-scores');
    }

    async getRankingRationale(data) {
        return this.request('/gemini/ranking-rationale', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async chatAboutRankings(data) {
        return this.request('/gemini/chat-rankings', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Gemini AI
    async analyzeContractWithGemini(contractText) {
        return this.request('/gemini/analyze-contract', {
            method: 'POST',
            body: JSON.stringify({ contract_text: contractText })
        });
    }

    async getSupplierRecommendations(supplierId, context = '') {
        return this.request('/gemini/supplier-recommendations', {
            method: 'POST',
            body: JSON.stringify({ supplier_id: supplierId, context: context })
        });
    }

    async analyzeRiskWithGemini(supplierId) {
        return this.request('/gemini/analyze-risk', {
            method: 'POST',
            body: JSON.stringify({ supplier_id: supplierId })
        });
    }

    async generateSupplierReport(supplierIds, reportType = 'comprehensive') {
        return this.request('/gemini/generate-report', {
            method: 'POST',
            body: JSON.stringify({ supplier_ids: supplierIds, report_type: reportType })
        });
    }

    async askGemini(query, contextData = null) {
        return this.request('/gemini/query', {
            method: 'POST',
            body: JSON.stringify({ query: query, context_data: contextData })
        });
    }

    async checkGeminiHealth() {
        return this.request('/gemini/health');
    }
};

// Global API instance
const api = new window.APIClient();

// CRITICAL: Expose to window for global access - MUST be done immediately
// Use Object.defineProperty to prevent overwriting
Object.defineProperty(window, 'api', {
    value: api,
    writable: false,
    configurable: false,
    enumerable: true
});

// Also set it as a global variable (for compatibility)
if (typeof globalThis !== 'undefined') {
    globalThis.api = api;
}

// Verify it's set correctly
console.log('[API] API client initialized');
console.log('[API] window.api:', window.api);
console.log('[API] window.api.getAvailableModels:', typeof window.api.getAvailableModels);
console.log('[API] window.api instanceof window.APIClient:', window.api instanceof window.APIClient);
console.log('[API] window.APIClient:', window.APIClient);

