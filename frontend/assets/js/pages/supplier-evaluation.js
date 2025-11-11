// Supplier Evaluation Page JavaScript - Enhanced
window.SupplierEvaluationPage = {
    async init() {
        const container = document.getElementById('page-supplier-evaluation');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
        this.loadAvailableModels();
        
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
                            <button id="compare-all-btn" class="btn-secondary-custom ml-2">
                                <i class="fas fa-balance-scale"></i> Compare All Models
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

                <!-- Model Comparison -->
                <div class="card mb-4" data-aos="fade-up" data-aos-delay="600">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-balance-scale"></i> Model Comparison</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label-custom">Select Models to Compare (comma-separated)</label>
                                <input type="text" id="compare-models-input" class="form-control-custom" 
                                       placeholder="xgboost,random_forest,gradient_boosting" 
                                       value="xgboost,random_forest,gradient_boosting">
                            </div>
                        </div>
                        <button id="compare-models-btn" class="btn-secondary-custom mb-3">
                            <i class="fas fa-balance-scale"></i> Compare Models
                        </button>
                        <div id="comparison-chart" class="chart-container-enhanced-large"></div>
                        <div id="comparison-table" class="table-container-enhanced mt-3"></div>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('evaluate-btn').addEventListener('click', () => this.evaluateSuppliers());
        document.getElementById('load-models-btn').addEventListener('click', () => this.loadAvailableModels());
        document.getElementById('feature-importance-btn').addEventListener('click', () => this.getFeatureImportance());
        document.getElementById('compare-models-btn').addEventListener('click', () => this.compareModels());
        document.getElementById('compare-all-btn').addEventListener('click', () => this.compareAllModels());
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
            
            window.app.showLoading();
            console.log('[SupplierEvaluation] API client found:', window.api);
            const result = await window.api.getAvailableModels();
            
            console.log('[SupplierEvaluation] Models loaded:', result);
            
            if (result.error) {
                window.app.showError(result.error);
                return;
            }
            
            const select = document.getElementById('model-type');
            select.innerHTML = '';
            result.available_models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model.charAt(0).toUpperCase() + model.slice(1).replace(/_/g, ' ');
                select.appendChild(option);
            });
            
            document.getElementById('total-models').textContent = result.total_models;
            window.app.showSuccess(`Loaded ${result.total_models} available models!`);
        } catch (error) {
            console.error('[SupplierEvaluation] Error loading models:', error);
            window.app.showError('Failed to load models: ' + error.message);
        } finally {
            window.app.hideLoading();
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

    async compareModels() {
        try {
            window.app.showLoading();
            const modelsInput = document.getElementById('compare-models-input').value;
            const models = modelsInput.split(',').map(m => m.trim());
            if (!window.api) {
                throw new Error('API client not available. Please refresh the page.');
            }
            const result = await window.api.compareSupplierModels(null, models.join(','));
            
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const comparison = result.results || [];
            const top20 = comparison.slice(0, 20);

            // Enhanced 3D scatter plot
            const scoreCols = Object.keys(comparison[0] || {}).filter(k => k.startsWith('score_'));
            if (scoreCols.length >= 3) {
                const chartData = [{
                    x: top20.map(r => r[scoreCols[0]] || 0),
                    y: top20.map(r => r[scoreCols[1]] || 0),
                    z: top20.map(r => r[scoreCols[2]] || 0),
                    mode: 'markers',
                    type: 'scatter3d',
                    marker: {
                        size: 10,
                        color: top20.map(r => r.avg_score || 0),
                        colorscale: 'Blues',
                        showscale: true,
                        line: { color: 'white', width: 1 }
                    },
                    text: top20.map(r => r.supplier_id)
                }];
                const chartLayout = {
                    title: {
                        text: '3D Model Comparison',
                        font: { size: 18, color: '#1A1A2E' }
                    },
                    scene: {
                        xaxis: { title: scoreCols[0].replace('score_', '').replace(/_/g, ' ').toUpperCase() },
                        yaxis: { title: scoreCols[1].replace('score_', '').replace(/_/g, ' ').toUpperCase() },
                        zaxis: { title: scoreCols[2].replace('score_', '').replace(/_/g, ' ').toUpperCase() },
                        bgcolor: '#F8F9FA'
                    },
                    height: 600,
                    paper_bgcolor: 'transparent',
                    font: { family: 'Inter, sans-serif', color: '#495057' }
                };
                Plotly.newPlot('comparison-chart', chartData, chartLayout, {responsive: true});
            } else {
                // Enhanced 2D comparison chart
                const chartData = scoreCols.map(col => ({
                    x: top20.map(r => r.supplier_id),
                    y: top20.map(r => r[col] || 0),
                    name: col.replace('score_', '').replace(/_/g, ' ').toUpperCase(),
                    type: 'bar'
                }));
                Plotly.newPlot('comparison-chart', chartData, {
                    title: {
                        text: 'Model Comparison',
                        font: { size: 18, color: '#1A1A2E' }
                    },
                    xaxis: { title: 'Supplier ID', gridcolor: '#E9ECEF' },
                    yaxis: { title: 'Score', gridcolor: '#E9ECEF' },
                    barmode: 'group',
                    height: 500,
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    font: { family: 'Inter, sans-serif', color: '#495057' }
                }, {responsive: true});
            }

            // Enhanced comparison table
            utils.createTable(top20, 'comparison-table', [
                { key: 'supplier_id', label: 'Supplier ID' },
                ...scoreCols.map(col => ({
                    key: col,
                    label: col.replace('score_', '').replace(/_/g, ' ').toUpperCase(),
                    format: (v) => utils.formatNumber(v, 3)
                })),
                { key: 'avg_score', label: 'Avg Score', format: (v) => `<strong>${utils.formatNumber(v, 3)}</strong>` },
                { key: 'score_variance', label: 'Variance', format: (v) => utils.formatNumber(v, 4) }
            ]);

            window.app.showSuccess(`Compared ${result.models_compared.length} models successfully!`);
        } catch (error) {
            window.app.showError('Failed to compare models: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async compareAllModels() {
        document.getElementById('compare-models-input').value = 'xgboost,random_forest,gradient_boosting,svm,neural_network,adaboost,ensemble';
        this.compareModels();
    }
};
