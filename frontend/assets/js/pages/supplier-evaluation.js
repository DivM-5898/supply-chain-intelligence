// Supplier Evaluation Page JavaScript - Enhanced
window.SupplierEvaluationPage = {
    async init() {
        const container = document.getElementById('page-supplier-evaluation');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
        
        // Load models asynchronously after page renders to reduce initial latency
        setTimeout(() => {
            this.loadAvailableModels();
        }, 100);
        
        // Refresh AOS after content loads
        if (typeof AOS !== 'undefined') {
            setTimeout(() => {
                AOS.refresh();
            }, 300);
        }
    },

    getHTML() {
        return `
            <!-- Page Header -->
            <div class="page-header mb-4" data-aos="fade-up">
                <div class="page-header-content">
                    <h1 class="page-title-large"><i class="fas fa-chart-line"></i> Supplier Evaluation & Scoring</h1>
                    <p class="page-subtitle">Evaluate and rank suppliers using 7 advanced ML models with interactive visualizations</p>
                </div>
            </div>

            <!-- Quick Stats Cards -->
            <div class="stats-row mb-4" data-aos="fade-up" data-aos-delay="100">
                <div class="stat-card-mini">
                    <div class="stat-icon" style="background: var(--gradient-primary);">
                        <i class="fas fa-brain"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value-mini" id="total-models">7</div>
                        <div class="stat-label-mini">ML Models</div>
                    </div>
                </div>
                <div class="stat-card-mini">
                    <div class="stat-icon" style="background: var(--gradient-success);">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value-mini" id="total-suppliers">-</div>
                        <div class="stat-label-mini">Suppliers</div>
                    </div>
                </div>
                <div class="stat-card-mini">
                    <div class="stat-icon" style="background: linear-gradient(135deg, var(--corp-warning), #FF8F00);">
                        <i class="fas fa-star"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value-mini" id="avg-score">-</div>
                        <div class="stat-label-mini">Avg Score</div>
                    </div>
                </div>
                <div class="stat-card-mini">
                    <div class="stat-icon" style="background: linear-gradient(135deg, var(--corp-danger), #C62828);">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value-mini" id="accuracy">92%</div>
                        <div class="stat-label-mini">Accuracy</div>
                    </div>
                </div>
            </div>

            <!-- File Upload Section - MOVED TO TOP -->
            <div class="card mb-4" data-aos="fade-up" data-aos-delay="200" style="border: 2px solid var(--corp-primary);">
                <div class="card-header-custom" style="background: var(--gradient-primary); color: white;">
                    <h3><i class="fas fa-file-upload"></i> 📁 Upload & Evaluate Your CSV/Excel File</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div class="alert alert-info mb-3">
                        <i class="fas fa-info-circle"></i> 
                        <strong>File Format:</strong> Upload CSV or Excel (.xlsx, .xls) file with supplier data. 
                        Required columns: supplier_id, on_time_delivery_rate, quality_score, defect_rate, 
                        credit_score, debt_to_equity, profit_margin, years_in_business, utilization_rate, 
                        geopolitical_risk_score, esg_score, compliance_score, etc.
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label-custom"><i class="fas fa-file"></i> Select File</label>
                            <input type="file" id="file-input" class="form-control-custom" accept=".csv,.xlsx,.xls">
                            <small class="text-muted">Supported formats: CSV, Excel (.xlsx, .xls)</small>
                        </div>
                        <div class="col-md-3 mb-3">
                            <label class="form-label-custom"><i class="fas fa-robot"></i> Model</label>
                            <select id="upload-model-type" class="form-control-custom">
                                <option value="xgboost">XGBoost</option>
                                <option value="random_forest">Random Forest</option>
                                <option value="gradient_boosting">Gradient Boosting</option>
                                <option value="svm">SVM</option>
                                <option value="neural_network">Neural Network</option>
                                <option value="adaboost">AdaBoost</option>
                                <option value="ensemble">Ensemble</option>
                            </select>
                        </div>
                        <div class="col-md-3 mb-3 d-flex align-items-end">
                            <button id="upload-evaluate-btn" class="btn-primary-custom w-100" disabled>
                                <i class="fas fa-upload"></i> Upload & Evaluate
                            </button>
                        </div>
                    </div>
                    <div id="file-info" class="mt-2" style="display: none;">
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle"></i> 
                            <span id="file-name-display"></span> selected
                        </div>
                    </div>
                </div>
            </div>

            <!-- Control Panel -->
            <div class="card mb-4" data-aos="fade-up" data-aos-delay="200">
                <div class="card-header-custom">
                    <h3><i class="fas fa-cog"></i> Evaluation Controls</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label-custom"><i class="fas fa-robot"></i> Select ML Model</label>
                            <select id="model-type" class="form-control-custom">
                                <option value="xgboost">XGBoost</option>
                                <option value="random_forest">Random Forest</option>
                                <option value="gradient_boosting">Gradient Boosting</option>
                                <option value="svm">SVM</option>
                                <option value="neural_network">Neural Network</option>
                                <option value="adaboost">AdaBoost</option>
                                <option value="ensemble">Ensemble (Voting)</option>
                            </select>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label-custom"><i class="fas fa-list-ol"></i> Top N Suppliers</label>
                            <input type="number" id="top-n" class="form-control-custom" value="10" min="5" max="50">
                        </div>
                        <div class="col-md-4 mb-3 d-flex align-items-end">
                            <button id="evaluate-btn" class="btn-primary-custom w-100">
                                <i class="fas fa-search"></i> Evaluate Suppliers
                            </button>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-12">
                            <button id="load-models-btn" class="btn-secondary-custom">
                                <i class="fas fa-sync"></i> Refresh Available Models
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Results Section -->
            <div id="results-section" style="display: none;">
                <!-- Rankings Chart -->
                <div class="card mb-4" data-aos="fade-up" data-aos-delay="300">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-trophy"></i> Supplier Rankings</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <div id="ranking-chart" class="chart-container-enhanced"></div>
                    </div>
                </div>

                <!-- Rankings Table -->
                <div class="card mb-4" data-aos="fade-up" data-aos-delay="400">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-table"></i> Detailed Rankings</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <div id="rankings-table" class="table-container-enhanced"></div>
                    </div>
                </div>

                <!-- Feature Importance -->
                <div class="card mb-4" data-aos="fade-up" data-aos-delay="500">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-chart-bar"></i> Feature Importance</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <button id="feature-importance-btn" class="btn-secondary-custom mb-3">
                            <i class="fas fa-chart-bar"></i> Get Feature Importance
                        </button>
                        <div id="feature-importance-chart" class="chart-container-enhanced"></div>
                    </div>
                </div>

                <!-- AI Chatbot for Ranking Rationale -->
                <div class="card mb-4" data-aos="fade-up" data-aos-delay="600">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-robot"></i> AI Ranking Rationale Assistant</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <p class="mb-3" style="color: var(--corp-gray-600);">
                            Get AI-powered explanations for supplier rankings. The assistant analyzes your uploaded data, 
                            selected model, and results to provide detailed rationale for the rankings.
                        </p>
                        <div id="chatbot-container" style="border: 1px solid var(--corp-gray-200); border-radius: 8px; background: white; min-height: 400px; max-height: 600px; display: flex; flex-direction: column;">
                            <div id="chatbot-messages" style="flex: 1; padding: 1.5rem; overflow-y: auto; max-height: 450px;">
                                <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                    <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                                        <i class="fas fa-robot"></i> AI Assistant
                                    </div>
                                    <div style="color: var(--corp-gray-700);">
                                        Hello! I'm your AI Ranking Rationale Assistant powered by Gemini 2.5 Flash. 
                                        Upload a CSV file, select a model, and get rankings to see detailed explanations for why suppliers are ranked the way they are.
                                    </div>
                                </div>
                            </div>
                            <div id="chatbot-input-container" style="padding: 1rem; border-top: 1px solid var(--corp-gray-200); display: flex; gap: 0.5rem;">
                                <input type="text" id="chatbot-input" class="form-control-custom" 
                                       placeholder="Ask about the rankings or click 'Get Ranking Rationale' below..." 
                                       style="flex: 1;">
                                <button id="chatbot-send-btn" class="btn-primary-custom" style="white-space: nowrap;">
                                    <i class="fas fa-paper-plane"></i> Send
                                </button>
                            </div>
                        </div>
                        <div class="mt-3" style="text-align: center;">
                            <button id="get-rationale-btn" class="btn-primary-custom">
                                <i class="fas fa-brain"></i> Get Ranking Rationale
                            </button>
                            <button id="clear-chat-btn" class="btn-secondary-custom ml-2">
                                <i class="fas fa-trash"></i> Clear Chat
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('evaluate-btn').addEventListener('click', () => this.evaluateSuppliers());
        document.getElementById('load-models-btn').addEventListener('click', () => this.loadAvailableModels());
        document.getElementById('feature-importance-btn').addEventListener('click', () => this.getFeatureImportance());
        
        // File upload handlers
        const fileInput = document.getElementById('file-input');
        const uploadBtn = document.getElementById('upload-evaluate-btn');
        const fileInfo = document.getElementById('file-info');
        const fileNameDisplay = document.getElementById('file-name-display');
        
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                uploadBtn.disabled = false;
                fileNameDisplay.textContent = file.name;
                fileInfo.style.display = 'block';
            } else {
                uploadBtn.disabled = true;
                fileInfo.style.display = 'none';
            }
        });
        
        uploadBtn.addEventListener('click', () => this.uploadAndEvaluate());
        
        // Chatbot handlers
        document.getElementById('get-rationale-btn').addEventListener('click', () => this.getRankingRationale());
        document.getElementById('chatbot-send-btn').addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
        document.getElementById('clear-chat-btn').addEventListener('click', () => this.clearChat());
    },

    async loadAvailableModels() {
        try {
            console.log('[SupplierEvaluation] Loading available models...');
            console.log('[SupplierEvaluation] window.api:', window.api);
            console.log('[SupplierEvaluation] typeof window.api:', typeof window.api);
            console.log('[SupplierEvaluation] window.api instanceof APIClient:', window.api instanceof APIClient);
            console.log('[SupplierEvaluation] window.api.getAvailableModels:', typeof window.api?.getAvailableModels);
            
            if (!window.api) {
                console.error('[SupplierEvaluation] window.api is not defined!');
                throw new Error('API client not available. Please refresh the page.');
            }
            
            // Check if it's actually an APIClient instance
            if (typeof window.api.getAvailableModels !== 'function') {
                console.error('[SupplierEvaluation] window.api.getAvailableModels is not a function!');
                console.error('[SupplierEvaluation] window.api keys:', Object.keys(window.api));
                console.error('[SupplierEvaluation] window.api constructor:', window.api.constructor?.name);
                
                // Try to reinitialize
                if (typeof window.APIClient !== 'undefined') {
                    console.log('[SupplierEvaluation] Reinitializing API client...');
                    try {
                        Object.defineProperty(window, 'api', {
                            value: new window.APIClient(),
                            writable: false,
                            configurable: true,
                            enumerable: true
                        });
                    } catch (e) {
                        window.api = new window.APIClient();
                    }
                    console.log('[SupplierEvaluation] New window.api:', window.api);
                } else {
                    throw new Error('API client is not properly initialized. Please refresh the page.');
                }
            }
            
            // Don't show full page loading, just load silently
            console.log('[SupplierEvaluation] API client found:', window.api);
            const result = await window.api.getAvailableModels();
            
            console.log('[SupplierEvaluation] Models loaded:', result);
            
            if (result.error) {
                console.error('[SupplierEvaluation] Error loading models:', result.error);
                // Set default models if API fails
                this.setDefaultModels();
                return;
            }
            
            const select = document.getElementById('model-type');
            if (select) {
                select.innerHTML = '';
                result.available_models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model.charAt(0).toUpperCase() + model.slice(1).replace(/_/g, ' ');
                    select.appendChild(option);
                });
            }
            
            const totalModelsEl = document.getElementById('total-models');
            if (totalModelsEl) {
                totalModelsEl.textContent = result.total_models;
            }
        } catch (error) {
            console.error('[SupplierEvaluation] Error loading models:', error);
            // Set default models on error
            this.setDefaultModels();
        }
    },

    setDefaultModels() {
        // Set default models if API call fails
        const select = document.getElementById('model-type');
        if (select) {
            const defaultModels = ['xgboost', 'random_forest', 'gradient_boosting', 'svm', 'neural_network', 'adaboost', 'ensemble'];
            select.innerHTML = '';
            defaultModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model.charAt(0).toUpperCase() + model.slice(1).replace(/_/g, ' ');
                select.appendChild(option);
            });
        }
        const totalModelsEl = document.getElementById('total-models');
        if (totalModelsEl) {
            totalModelsEl.textContent = '7';
        }
    },

    async evaluateSuppliers() {
        try {
            console.log('[SupplierEvaluation] evaluateSuppliers called');
            console.log('[SupplierEvaluation] window.api:', window.api);
            console.log('[SupplierEvaluation] typeof api:', typeof api);
            
            window.app.showLoading();
            
            // Always use window.api - never the bare api variable
            if (!window.api) {
                console.error('[SupplierEvaluation] window.api is not defined!');
                throw new Error('API client not available. Please refresh the page.');
            }
            
            const modelType = document.getElementById('model-type').value;
            console.log('[SupplierEvaluation] Calling evaluateSuppliers with model:', modelType);
            const result = await window.api.evaluateSuppliers(null, modelType);
            
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            this.displayResults(result);
            document.getElementById('total-suppliers').textContent = result.total_suppliers;
            const avgScore = result.results.reduce((sum, r) => sum + r.predicted_score, 0) / result.results.length;
            document.getElementById('avg-score').textContent = avgScore.toFixed(2);
            window.app.showSuccess(`Evaluated ${result.total_suppliers} suppliers successfully!`);
        } catch (error) {
            window.app.showError('Failed to evaluate suppliers: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async uploadAndEvaluate() {
        try {
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0];
            
            if (!file) {
                window.app.showError('Please select a file to upload');
                return;
            }
            
            const modelType = document.getElementById('upload-model-type').value;
            const topN = parseInt(document.getElementById('top-n').value) || null;
            
            window.app.showLoading();
            
            if (!window.api) {
                throw new Error('API client not available. Please refresh the page.');
            }
            
            console.log('[SupplierEvaluation] Uploading file:', file.name, 'Model:', modelType);
            
            const result = await window.api.uploadAndEvaluate(file, modelType, topN);
            
            if (result.error) {
                window.app.showError(result.error);
                return;
            }
            
            // Store data for chatbot
            // Read CSV content for chatbot
            const csvText = await file.text();
            this.currentEvaluationData = {
                csvData: csvText,
                modelType: modelType,
                results: result.results || [],
                fileName: file.name
            };
            
            // Display results
            this.displayResults(result);
            document.getElementById('total-suppliers').textContent = result.total_suppliers;
            const avgScore = result.results.reduce((sum, r) => sum + r.predicted_score, 0) / result.results.length;
            document.getElementById('avg-score').textContent = avgScore.toFixed(2);
            
            window.app.showSuccess(result.message || `Successfully evaluated ${result.total_suppliers} suppliers from uploaded file!`);
            
        } catch (error) {
            console.error('[SupplierEvaluation] Error uploading and evaluating:', error);
            window.app.showError('Failed to upload and evaluate file: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    displayResults(result) {
        document.getElementById('results-section').style.display = 'block';
        const results = result.results || [];
        const topN = parseInt(document.getElementById('top-n').value);
        const topResults = results.slice(0, topN);

        // Enhanced ranking chart
        const chartData = [{
            y: topResults.map(r => r.supplier_id),
            x: topResults.map(r => r.predicted_score),
            type: 'bar',
            orientation: 'h',
            marker: {
                color: topResults.map(r => r.predicted_score),
                colorscale: 'Blues',
                line: { color: 'white', width: 1 }
            },
            text: topResults.map(r => `Score: ${r.predicted_score.toFixed(3)}`),
            textposition: 'outside'
        }];
        const chartLayout = {
            title: {
                text: `Top ${topN} Supplier Rankings`,
                font: { size: 18, color: '#1A1A2E' }
            },
            xaxis: { title: 'Score', gridcolor: '#E9ECEF' },
            yaxis: { title: 'Supplier ID', gridcolor: '#E9ECEF' },
            height: Math.max(400, topN * 40),
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { family: 'Inter, sans-serif' }
        };
        Plotly.newPlot('ranking-chart', chartData, chartLayout, {responsive: true});

        // Enhanced table
        utils.createTable(topResults, 'rankings-table', [
            { key: 'rank', label: 'Rank', format: (v) => `<span class="badge badge-primary">#${v}</span>` },
            { key: 'supplier_id', label: 'Supplier ID' },
            { key: 'predicted_score', label: 'Score', format: (v) => `<strong>${utils.formatNumber(v, 3)}</strong>` },
            { key: 'model_type', label: 'Model' }
        ]);
    },

    async getFeatureImportance() {
        try {
            window.app.showLoading();
            const modelType = document.getElementById('model-type').value;
            if (!window.api) {
                throw new Error('API client not available. Please refresh the page.');
            }
            const result = await window.api.getFeatureImportance(modelType);
            
            // Check if feature importance is available
            if (result.message) {
                window.app.showInfo(result.message);
                document.getElementById('feature-importance-chart').innerHTML = 
                    `<div class="alert alert-info">
                        <h5>${result.message}</h5>
                        <p>Available models with feature importance: ${result.available_models_with_importance?.join(', ') || 'xgboost, random_forest, gradient_boosting, adaboost, ensemble'}</p>
                    </div>`;
                return;
            }
            
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const importance = result.feature_importance || {};
            if (Object.keys(importance).length === 0) {
                window.app.showInfo('No feature importance data available for this model');
                return;
            }
            
            const sorted = Object.entries(importance)
                .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                .slice(0, 10);

            const chartData = [{
                x: sorted.map(([_, v]) => v),
                y: sorted.map(([k, _]) => k.replace(/_/g, ' ')),
                type: 'bar',
                orientation: 'h',
                marker: {
                    color: sorted.map(([_, v]) => v),
                    colorscale: 'Blues',
                    line: { color: 'white', width: 1 }
                }
            }];
            const chartLayout = {
                title: {
                    text: `Top 10 Feature Importances - ${modelType.toUpperCase()}`,
                    font: { size: 18, color: '#1A1A2E' }
                },
                xaxis: { title: 'Importance', gridcolor: '#E9ECEF' },
                yaxis: { title: 'Feature', gridcolor: '#E9ECEF' },
                height: 500,
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { family: 'Inter, sans-serif', color: '#495057' }
            };
            Plotly.newPlot('feature-importance-chart', chartData, chartLayout, {responsive: true});
            window.app.showSuccess('Feature importance loaded successfully!');
        } catch (error) {
            console.error('[SupplierEvaluation] Error loading feature importance:', error);
            window.app.showError('Failed to load feature importance: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    // Store current evaluation data for chatbot
    currentEvaluationData: {
        csvData: null,
        modelType: null,
        results: null,
        fileName: null
    },

    async getRankingRationale() {
        try {
            if (!this.currentEvaluationData.results || !this.currentEvaluationData.modelType) {
                window.app.showError('Please upload a CSV file and get rankings first before requesting rationale.');
                return;
            }

            this.addChatMessage('user', 'Please explain the ranking rationale for these suppliers.');
            const typingIndicator = this.showTypingIndicator();
            
            const result = await window.api.getRankingRationale({
                csv_data: this.currentEvaluationData.csvData,
                model_type: this.currentEvaluationData.modelType,
                results: this.currentEvaluationData.results,
                file_name: this.currentEvaluationData.fileName
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
                return;
            }

            this.addChatMessage('bot', result.rationale || result.response || 'Ranking rationale generated successfully.');
            window.app.showSuccess('Ranking rationale generated!');
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[SupplierEvaluation] Error getting ranking rationale:', error);
            let errorMessage = error.message || 'Failed to get ranking rationale';
            
            // Handle quota errors
            if (error.status === 429 || errorMessage.includes('quota') || errorMessage.includes('429')) {
                const retryAfter = error.detail?.retry_after || error.detail?.detail?.retry_after || 60;
                errorMessage = `⚠️ API Quota Exceeded\n\nYou've reached the free tier rate limit. Please wait ${retryAfter} seconds before trying again.\n\nTip: The free tier has limited requests per minute. Consider upgrading your Google Gemini API plan for higher limits.`;
                this.addChatMessage('bot', errorMessage, true);
                window.app.showError(`Quota exceeded. Please wait ${retryAfter} seconds.`);
            } else {
                this.addChatMessage('bot', `Error: ${errorMessage}`, true);
                window.app.showError('Failed to get ranking rationale: ' + errorMessage);
            }
        }
    },

    async sendChatMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message) return;

        if (!this.currentEvaluationData.results) {
            window.app.showError('Please upload a CSV file and get rankings first.');
            return;
        }

        this.addChatMessage('user', message);
        input.value = '';
        const typingIndicator = this.showTypingIndicator();

        try {
            const result = await window.api.chatAboutRankings({
                message: message,
                csv_data: this.currentEvaluationData.csvData,
                model_type: this.currentEvaluationData.modelType,
                results: this.currentEvaluationData.results
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
            } else {
                this.addChatMessage('bot', result.response || result.answer || 'Response generated.');
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[SupplierEvaluation] Chat error:', error);
            let errorMessage = error.message || 'Failed to get response';
            
            // Handle quota errors
            if (error.status === 429 || errorMessage.includes('quota') || errorMessage.includes('429')) {
                const retryAfter = error.detail?.retry_after || error.detail?.detail?.retry_after || 60;
                errorMessage = `⚠️ API Quota Exceeded\n\nYou've reached the free tier rate limit. Please wait ${retryAfter} seconds before trying again.\n\nTip: The free tier has limited requests per minute. Consider upgrading your Google Gemini API plan for higher limits.`;
                this.addChatMessage('bot', errorMessage, true);
            } else {
                this.addChatMessage('bot', `Error: ${errorMessage}`, true);
            }
        }
    },

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return null;

        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-message bot-message';
        typingDiv.style.cssText = `
            background: var(--corp-gray-50);
            color: var(--corp-gray-700);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            max-width: 80%;
            word-wrap: break-word;
        `;

        const header = document.createElement('div');
        header.style.cssText = 'font-weight: 600; margin-bottom: 0.5rem;';
        header.innerHTML = '<i class="fas fa-robot"></i> AI Assistant';
        typingDiv.appendChild(header);

        const typingContent = document.createElement('div');
        typingContent.style.cssText = 'display: flex; align-items: center; gap: 0.5rem;';
        typingContent.innerHTML = `
            <span class="typing-dot" style="width: 8px; height: 8px; background: var(--corp-primary); border-radius: 50%; animation: typing 1.4s infinite;"></span>
            <span class="typing-dot" style="width: 8px; height: 8px; background: var(--corp-primary); border-radius: 50%; animation: typing 1.4s infinite 0.2s;"></span>
            <span class="typing-dot" style="width: 8px; height: 8px; background: var(--corp-primary); border-radius: 50%; animation: typing 1.4s infinite 0.4s;"></span>
            <span style="margin-left: 0.5rem; color: var(--corp-gray-600);">AI is typing...</span>
        `;
        typingDiv.appendChild(typingContent);

        // Add CSS animation if not already added
        if (!document.getElementById('typing-animation-style')) {
            const style = document.createElement('style');
            style.id = 'typing-animation-style';
            style.textContent = `
                @keyframes typing {
                    0%, 60%, 100% {
                        transform: translateY(0);
                        opacity: 0.7;
                    }
                    30% {
                        transform: translateY(-10px);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return typingDiv;
    },

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    },

    addChatMessage(sender, message, isError = false) {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        messageDiv.style.cssText = `
            background: ${sender === 'user' ? 'var(--corp-primary)' : (isError ? '#fee' : 'var(--corp-gray-50)')};
            color: ${sender === 'user' ? 'white' : 'var(--corp-gray-700)'};
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            margin-left: ${sender === 'user' ? 'auto' : '0'};
            margin-right: ${sender === 'user' ? '0' : 'auto'};
            max-width: 80%;
            word-wrap: break-word;
        `;

        const header = document.createElement('div');
        header.style.cssText = 'font-weight: 600; margin-bottom: 0.5rem;';
        header.innerHTML = sender === 'user' 
            ? '<i class="fas fa-user"></i> You'
            : '<i class="fas fa-robot"></i> AI Assistant';
        messageDiv.appendChild(header);

        const content = document.createElement('div');
        content.style.cssText = 'white-space: pre-wrap; line-height: 1.6;';
        content.textContent = message;
        messageDiv.appendChild(content);

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    },

    clearChat() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                        <i class="fas fa-robot"></i> AI Assistant
                    </div>
                    <div style="color: var(--corp-gray-700);">
                        Hello! I'm your AI Ranking Rationale Assistant powered by Gemini 2.5 Flash. 
                        Upload a CSV file, select a model, and get rankings to see detailed explanations for why suppliers are ranked the way they are.
                    </div>
                </div>
            `;
        }
    },
};
