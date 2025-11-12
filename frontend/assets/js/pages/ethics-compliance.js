// Ethics & Compliance Page JavaScript
window.EthicsCompliancePage = {
    async init() {
        const container = document.getElementById('page-ethics-compliance');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
    },

    getHTML() {
        return `
            <div class="card mb-4">
                <h1 class="card-title">✅ Ethics & Compliance</h1>
                <p class="lead">What are the ethical and compliance considerations in AI-driven supplier management?</p>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🔍 Model Explainability</h3>
                <div id="explain-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                    <div style="display: inline-block;">
                        <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                            <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                            <div style="font-size: 1rem; font-weight: 500;">
                                Generating explanation... Please wait
                            </div>
                        </div>
                    </div>
                </div>
                <div id="explain-content">
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label class="form-label">Supplier ID</label>
                            <input type="text" id="explain-supplier-id" class="form-control" value="SUP_0001" placeholder="SUP_0001">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group">
                            <label class="form-label">Explanation Type</label>
                            <select id="explanation-type" class="form-control">
                                <option value="lime">LIME</option>
                                <option value="shap">SHAP</option>
                            </select>
                        </div>
                    </div>
                </div>
                <button id="explain-btn" class="btn btn-primary">
                    <i class="fas fa-search"></i> Explain Prediction
                </button>
                </div>
            </div>

            <div id="explanation-results" style="display: none;">
                <div class="card mb-4">
                    <h3 class="card-title">📊 Explanation Results</h3>
                    <div id="explanation-display"></div>
                </div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">⚖️ Bias Detection</h3>
                <div id="bias-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                    <div style="display: inline-block;">
                        <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                            <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                            <div style="font-size: 1rem; font-weight: 500;">
                                Detecting bias... Please wait
                            </div>
                        </div>
                    </div>
                </div>
                <div id="bias-content">
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label class="form-label">Feature for Bias Analysis</label>
                            <select id="bias-feature" class="form-control">
                                <option value="years_in_business">Years in Business</option>
                                <option value="credit_score">Credit Score</option>
                                <option value="profit_margin">Profit Margin</option>
                                <option value="utilization_rate">Utilization Rate</option>
                                <option value="geopolitical_risk_score">Geopolitical Risk Score</option>
                                <option value="esg_score">ESG Score</option>
                                <option value="compliance_score">Compliance Score</option>
                                <option value="on_time_delivery_rate">On-Time Delivery Rate</option>
                                <option value="quality_score">Quality Score</option>
                            </select>
                        </div>
                    </div>
                </div>
                <button id="detect-bias-btn" class="btn btn-warning">
                    <i class="fas fa-balance-scale"></i> Detect Bias
                </button>
                </div>
            </div>

            <div id="bias-results" style="display: none;">
                <div class="card mb-4">
                    <h3 class="card-title">📊 Bias Analysis Results</h3>
                    <div id="bias-display"></div>
                </div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🌱 ESG Compliance Scores</h3>
                <div id="esg-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                    <div style="display: inline-block;">
                        <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                            <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                            <div style="font-size: 1rem; font-weight: 500;">
                                Loading ESG scores... Please wait
                            </div>
                        </div>
                    </div>
                </div>
                <div id="esg-content">
                <button id="load-esg-btn" class="btn btn-success mb-3">
                    <i class="fas fa-leaf"></i> View ESG Scores
                </button>
                <div id="esg-table" class="table-container"></div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('explain-btn').addEventListener('click', () => this.explainPrediction());
        document.getElementById('detect-bias-btn').addEventListener('click', () => this.detectBias());
        document.getElementById('load-esg-btn').addEventListener('click', () => this.loadESGScores());
    },

    async explainPrediction() {
        try {
            this.showLoading('explain');
            const supplierId = document.getElementById('explain-supplier-id').value;
            const explanationType = document.getElementById('explanation-type').value;

            const result = await (window.api).explainPrediction(supplierId, 'xgboost', explanationType);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            document.getElementById('explanation-results').style.display = 'block';
            
            // The API returns {explanation: {...data}, supplier_id: ...}
            // For LIME: result.explanation is the direct list
            // For SHAP: result.explanation contains shap_values, feature_names, etc.
            const explanation = result.explanation || {};

            if (explanationType === 'lime') {
                // LIME: explanation is already the list of tuples, not nested
                const expList = Array.isArray(explanation) ? explanation : (explanation.explanation || []);
                
                console.log('[Ethics] LIME explanation:', expList);
                
                if (!expList || expList.length === 0) {
                    document.getElementById('explanation-display').innerHTML = 
                        '<div class="alert alert-warning">No explanation data available. Make sure the supplier exists and the model is trained.</div>';
                    return;
                }
                
                // Sort by absolute contribution
                const sortedExp = expList.sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
                
                // Create horizontal bar chart
                const chartData = [{
                    x: sortedExp.map(([_, v]) => v),
                    y: sortedExp.map(([k, _]) => k),
                    type: 'bar',
                    orientation: 'h',
                    marker: {
                        color: sortedExp.map(([_, v]) => v > 0 ? '#10b981' : '#ef4444'),
                        line: { color: 'white', width: 1 }
                    },
                    text: sortedExp.map(([_, v]) => utils.formatNumber(v, 4)),
                    textposition: 'outside'
                }];
                
                const chartLayout = {
                    title: {
                        text: `LIME Explanation for ${supplierId}`,
                        font: { size: 18, color: '#1A1A2E', family: 'Inter, sans-serif' }
                    },
                    xaxis: { 
                        title: 'Feature Contribution',
                        gridcolor: '#E9ECEF',
                        zeroline: true,
                        zerolinecolor: '#666',
                        zerolinewidth: 2
                    },
                    yaxis: { 
                        title: 'Feature',
                        gridcolor: '#E9ECEF'
                    },
                    height: Math.max(400, sortedExp.length * 40),
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'white',
                    font: { family: 'Inter, sans-serif', color: '#495057' },
                    margin: { l: 200, r: 100, t: 80, b: 80 }
                };
                
                Plotly.newPlot('explanation-display', chartData, chartLayout, {responsive: true});
                
                // Add prediction info below chart
                const predInfo = document.createElement('div');
                predInfo.style.cssText = 'margin-top: 1rem; padding: 1rem; background: var(--corp-gray-50); border-radius: 8px;';
                const predValue = result.prediction || explanation.prediction || 0;
                predInfo.innerHTML = `
                    <strong>Predicted Score:</strong> <span style="font-size: 1.2rem; color: var(--corp-primary);">${utils.formatNumber(predValue, 4)}</span>
                    <br>
                    <small class="text-muted">Green bars indicate positive contributions, red bars indicate negative contributions</small>
                `;
                document.getElementById('explanation-display').appendChild(predInfo);
            } else {
                const shapValues = explanation.shap_values || [];
                const featureNames = explanation.feature_names || [];
                const importance = {};
                featureNames.forEach((name, i) => {
                    importance[name] = shapValues[i];
                });

                const sorted = Object.entries(importance)
                    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                    .slice(0, 10);

                const chartData = [{
                    x: sorted.map(([_, v]) => v),
                    y: sorted.map(([k, _]) => k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())),
                    type: 'bar',
                    orientation: 'h',
                    marker: {
                        color: sorted.map(([_, v]) => v),
                        colorscale: [
                            [0, '#ef4444'],      // Red for negative
                            [0.5, '#f3f4f6'],    // Gray for neutral
                            [1, '#10b981']       // Green for positive
                        ],
                        line: { color: 'white', width: 1 }
                    },
                    text: sorted.map(([_, v]) => utils.formatNumber(v, 4)),
                    textposition: 'outside'
                }];
                
                const chartLayout = {
                    title: {
                        text: `SHAP Feature Importance for ${supplierId}`,
                        font: { size: 18, color: '#1A1A2E', family: 'Inter, sans-serif' }
                    },
                    xaxis: { 
                        title: 'SHAP Value',
                        gridcolor: '#E9ECEF',
                        zeroline: true,
                        zerolinecolor: '#666',
                        zerolinewidth: 2
                    },
                    yaxis: { 
                        title: 'Feature',
                        gridcolor: '#E9ECEF'
                    },
                    height: Math.max(400, sorted.length * 40),
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'white',
                    font: { family: 'Inter, sans-serif', color: '#495057' },
                    margin: { l: 200, r: 100, t: 80, b: 80 }
                };
                
                Plotly.newPlot('explanation-display', chartData, chartLayout, {responsive: true});
                
                // Add interpretation info
                const interpInfo = document.createElement('div');
                interpInfo.style.cssText = 'margin-top: 1rem; padding: 1rem; background: var(--corp-gray-50); border-radius: 8px;';
                interpInfo.innerHTML = `
                    <small class="text-muted">
                        <strong>How to read:</strong> Positive SHAP values (green) increase the prediction, 
                        negative values (red) decrease it. The larger the absolute value, the stronger the effect.
                    </small>
                `;
                document.getElementById('explanation-display').appendChild(interpInfo);
            }

            window.app.showSuccess('Explanation generated successfully!');
        } catch (error) {
            window.app.showError('Failed to generate explanation: ' + error.message);
        } finally {
            this.hideLoading('explain');
        }
    },

    async detectBias() {
        try {
            this.showLoading('bias');
            const featureName = document.getElementById('bias-feature').value;

            const result = await (window.api).detectBias(featureName);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            document.getElementById('bias-results').style.display = 'block';
            const correlation = result.correlation || 0;
            const interpretation = result.interpretation || '';
            const pValue = result.p_value || 0;
            
            let html = `
                <div style="padding: 1.5rem; background: var(--corp-gray-50); border-radius: 8px; margin-bottom: 1rem;">
                    <h5 style="margin-bottom: 1rem; color: var(--corp-primary);">📊 Statistical Analysis</h5>
                    <div class="row">
                        <div class="col-md-4">
                            <strong>Correlation:</strong> 
                            <span style="font-size: 1.5rem; color: var(--corp-primary);">${utils.formatNumber(correlation, 3)}</span>
                        </div>
                        <div class="col-md-4">
                            <strong>P-Value:</strong> 
                            <span style="font-size: 1.5rem; color: ${pValue < 0.05 ? '#ef4444' : '#10b981'};">${pValue < 0.0001 ? '< 0.0001' : utils.formatNumber(pValue, 4)}</span>
                            ${pValue < 0.05 ? '<br><small class="text-danger">Statistically significant</small>' : '<br><small class="text-success">Not significant</small>'}
                        </div>
                        <div class="col-md-4">
                            <strong>Type:</strong> 
                            <span>${result.correlation_type || 'pearson'}</span>
                        </div>
                    </div>
                </div>
            `;

            // Features where high correlation is expected/desired (positive indicators)
            const desirableFeatures = ['esg_score', 'compliance_score', 'quality_score', 'on_time_delivery_rate'];
            // Features where correlation might indicate bias (demographic/geographic)
            const sensitiveFeatures = ['country', 'region', 'industry'];
            
            const isDesirable = desirableFeatures.includes(featureName);
            const isSensitive = sensitiveFeatures.includes(featureName);
            
            if (Math.abs(correlation) > 0.5) {
                if (isDesirable) {
                    html += `<div class="alert alert-info">📊 <strong>Strong Correlation (Expected):</strong> High ${featureName.replace(/_/g, ' ')} correlates with better predictions, which is desired model behavior.</div>`;
                } else if (isSensitive) {
                    html += `<div class="alert alert-danger">🚨 <strong>Strong Bias Detected!</strong> High correlation with ${featureName} suggests potential discrimination. Review model fairness.</div>`;
                } else {
                    html += `<div class="alert alert-warning">⚠️ <strong>Strong Correlation:</strong> High correlation detected. Evaluate if this is expected behavior.</div>`;
                }
            } else if (Math.abs(correlation) > 0.3) {
                if (isSensitive) {
                    html += `<div class="alert alert-warning">⚠️ <strong>Potential Bias:</strong> Moderate correlation with ${featureName} detected. Further investigation recommended.</div>`;
                } else {
                    html += `<div class="alert alert-info">ℹ️ <strong>Moderate Correlation:</strong> Some correlation detected with ${featureName}.</div>`;
                }
            } else {
                html += `<div class="alert alert-success">✅ <strong>Low Correlation:</strong> Weak correlation suggests ${isSensitive ? 'minimal bias concerns' : 'minimal influence from this feature'}.</div>`;
            }

            if (result.bias_analysis && result.bias_analysis.length > 0) {
                html += `<h5 style="margin-top: 1.5rem; margin-bottom: 1rem;">Group Analysis</h5><div id="bias-group-table" class="table-container mt-3"></div>`;
                document.getElementById('bias-display').innerHTML = html;
                
                // Detect if we have Category or Range
                const firstRow = result.bias_analysis[0];
                const groupKey = firstRow.hasOwnProperty('Category') ? 'Category' : 'Range';
                const groupLabel = groupKey === 'Category' ? 'Category' : 'Range';
                
                utils.createTable(result.bias_analysis, 'bias-group-table', [
                    { key: groupKey, label: groupLabel },
                    { key: 'Avg_Prediction', label: 'Average Prediction', format: (v) => utils.formatNumber(v, 4) },
                    { key: 'Std_Prediction', label: 'Std Dev', format: (v) => utils.formatNumber(v, 4) },
                    { key: 'Count', label: 'Sample Size' }
                ]);
            } else {
                document.getElementById('bias-display').innerHTML = html;
            }

            window.app.showSuccess('Bias analysis complete!');
        } catch (error) {
            window.app.showError('Failed to detect bias: ' + error.message);
        } finally {
            this.hideLoading('bias');
        }
    },

    async loadESGScores() {
        try {
            this.showLoading('esg');
            const result = await (window.api).getESGScores();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            utils.createTable(result.esg_scores || [], 'esg-table', [
                { key: 'supplier_id', label: 'Supplier ID' },
                { key: 'esg_score', label: 'ESG Score', format: (v) => utils.formatNumber(v, 3) },
                { key: 'compliance_score', label: 'Compliance Score', format: (v) => utils.formatNumber(v, 3) }
            ]);

            window.app.showSuccess('ESG scores loaded successfully!');
        } catch (error) {
            window.app.showError('Failed to load ESG scores: ' + error.message);
        } finally {
            this.hideLoading('esg');
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

