// Fraud Prediction Page JavaScript
window.FraudPredictionPage = {
    async init() {
        const container = document.getElementById('page-fraud-prediction');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
    },

    getHTML() {
        return `
            <div class="card mb-4">
                <h1 class="card-title">⚡ Fraud & Disruption Prediction</h1>
                <p class="lead">How can machine learning models predict supplier disruptions or fraud?</p>
            </div>

            <div class="card mb-4">
                <div id="fraud-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                    <div style="display: inline-block;">
                        <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                            <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                            <div style="font-size: 1rem; font-weight: 500;">
                                Analyzing fraud predictions... Please wait
                            </div>
                        </div>
                    </div>
                </div>
                <div id="fraud-content">
                <div class="form-group">
                    <label class="form-label">Select Model</label>
                    <select id="fraud-model-type" class="form-control">
                        <option value="random_forest">Random Forest</option>
                        <option value="gradient_boosting">Gradient Boosting</option>
                    </select>
                </div>
                <button id="predict-fraud-btn" class="btn btn-primary">
                    <i class="fas fa-search"></i> Predict Fraud
                </button>
                </div>
            </div>

            <div id="fraud-results" style="display: none;">
                <div class="card mb-4">
                    <h3 class="card-title">📊 Fraud Predictions</h3>
                    <div id="fraud-distribution-chart" class="chart-container mb-3"></div>
                    <div id="fraud-table" class="table-container"></div>
                </div>

                <div class="card mb-4">
                    <h3 class="card-title">⚖️ Supplier Comparison</h3>
                    <div id="comparison-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                        <div style="display: inline-block;">
                            <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                                <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                            <div style="font-size: 1rem; font-weight: 500;">
                                Comparing suppliers... Please wait
                            </div>
                            </div>
                        </div>
                    </div>
                    <div id="comparison-content">
                    <button id="compare-fraud-models-btn" class="btn btn-secondary mb-3">
                        <i class="fas fa-balance-scale"></i> Supplier Comparison
                    </button>
                    <div id="fraud-comparison-chart" class="chart-container"></div>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('predict-fraud-btn').addEventListener('click', () => this.predictFraud());
        document.getElementById('compare-fraud-models-btn').addEventListener('click', () => this.compareModels());
    },

    async predictFraud() {
        try {
            this.showLoading('fraud');
            const modelType = document.getElementById('fraud-model-type').value;
            const result = await (window.api).predictFraud(null, modelType);
            
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const frauds = result.results || [];
            document.getElementById('fraud-results').style.display = 'block';

            // Distribution chart with proper color mapping
            const fraudCounts = {};
            frauds.forEach(f => {
                const risk = f.fraud_risk || 'Unknown';
                fraudCounts[risk] = (fraudCounts[risk] || 0) + 1;
            });

            // Define color mapping for each risk level
            const colorMap = {
                'Low': '#10b981',      // Green
                'Medium': '#f59e0b',   // Orange
                'High': '#ef4444',     // Red
                'Unknown': '#6b7280'   // Gray
            };
            
            const categories = Object.keys(fraudCounts);
            const colors = categories.map(cat => colorMap[cat] || '#6b7280');

            const chartData = [{
                x: categories,
                y: Object.values(fraudCounts),
                type: 'bar',
                marker: { 
                    color: colors,
                    line: { color: 'white', width: 1 }
                },
                text: Object.values(fraudCounts),
                textposition: 'outside'
            }];
            
            Plotly.newPlot('fraud-distribution-chart', chartData, {
                title: {
                    text: 'Fraud Risk Distribution',
                    font: { size: 18, color: '#1A1A2E', family: 'Inter, sans-serif' }
                },
                xaxis: { 
                    title: 'Fraud Risk Level',
                    categoryorder: 'array',
                    categoryarray: ['Low', 'Medium', 'High', 'Unknown']
                },
                yaxis: { title: 'Count' },
                height: 400,
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'white',
                font: { family: 'Inter, sans-serif' }
            });

            // Table
            const highRisk = frauds.filter(f => f.fraud_risk === 'High');
            if (highRisk.length > 0) {
                window.app.showError(`⚠️ ${highRisk.length} suppliers flagged as HIGH RISK`);
            }

            utils.createTable(frauds.slice(0, 20), 'fraud-table', [
                { key: 'supplier_id', label: 'Supplier ID' },
                { key: 'fraud_probability', label: 'Fraud Probability', format: (v) => utils.formatPercentage(v) },
                { key: 'is_fraud', label: 'Is Fraud' },
                { key: 'fraud_risk', label: 'Risk Level' }
            ]);

            window.app.showSuccess(`Analyzed ${result.total_suppliers} suppliers!`);
        } catch (error) {
            window.app.showError('Failed to predict fraud: ' + error.message);
        } finally {
            this.hideLoading('fraud');
        }
    },

    async compareModels() {
        try {
            this.showLoading('comparison');
            const result = await (window.api).compareFraudModels();
            
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const comparison = result.results || [];
            const top20 = comparison.slice(0, 20);

            const chartData = [{
                x: top20.map(r => r.supplier_id),
                y: top20.map(r => r.avg_fraud_probability),
                type: 'bar',
                marker: { 
                    color: top20.map(r => r.avg_fraud_probability),
                    colorscale: [
                        [0, '#10b981'],      // Green for low probability
                        [0.5, '#f59e0b'],    // Orange for medium
                        [1, '#ef4444']       // Red for high probability
                    ],
                    line: { color: 'white', width: 1 }
                },
                text: top20.map(r => (r.avg_fraud_probability * 100).toFixed(1) + '%'),
                textposition: 'outside'
            }];
            
            Plotly.newPlot('fraud-comparison-chart', chartData, {
                title: {
                    text: 'Supplier Fraud Probability Comparison',
                    font: { size: 18, color: '#1A1A2E', family: 'Inter, sans-serif' }
                },
                xaxis: { 
                    title: 'Supplier ID',
                    tickangle: -45
                },
                yaxis: { 
                    title: 'Average Fraud Probability',
                    tickformat: '.1%'
                },
                height: 500,
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'white',
                font: { family: 'Inter, sans-serif' },
                margin: { b: 100 }
            });

            window.app.showSuccess(`Model agreement rate: ${(result.agreement_rate * 100).toFixed(1)}%`);
        } catch (error) {
            window.app.showError('Failed to compare models: ' + error.message);
        } finally {
            this.hideLoading('comparison');
        }
    },

    showLoading(section) {
        const loadingEl = document.getElementById(`${section}-loading`);
        const contentEl = document.getElementById(`${section}-content`);
        if (loadingEl) loadingEl.style.display = 'block';
        if (contentEl) contentEl.style.opacity = '0.5';
        if (contentEl) contentEl.style.pointerEvents = 'none';
    },

    hideLoading(section) {
        const loadingEl = document.getElementById(`${section}-loading`);
        const contentEl = document.getElementById(`${section}-content`);
        if (loadingEl) loadingEl.style.display = 'none';
        if (contentEl) contentEl.style.opacity = '1';
        if (contentEl) contentEl.style.pointerEvents = 'auto';
    }
};

