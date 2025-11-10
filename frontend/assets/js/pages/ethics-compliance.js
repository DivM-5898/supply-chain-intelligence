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

            <div id="explanation-results" style="display: none;">
                <div class="card mb-4">
                    <h3 class="card-title">📊 Explanation Results</h3>
                    <div id="explanation-display"></div>
                </div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">⚖️ Bias Detection</h3>
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label class="form-label">Feature for Bias Analysis</label>
                            <select id="bias-feature" class="form-control">
                                <option value="country">Country</option>
                                <option value="industry">Industry</option>
                                <option value="years_in_business">Years in Business</option>
                                <option value="employee_count">Employee Count</option>
                            </select>
                        </div>
                    </div>
                </div>
                <button id="detect-bias-btn" class="btn btn-warning">
                    <i class="fas fa-balance-scale"></i> Detect Bias
                </button>
            </div>

            <div id="bias-results" style="display: none;">
                <div class="card mb-4">
                    <h3 class="card-title">📊 Bias Analysis Results</h3>
                    <div id="bias-display"></div>
                </div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🌱 ESG Compliance Scores</h3>
                <button id="load-esg-btn" class="btn btn-success mb-3">
                    <i class="fas fa-leaf"></i> View ESG Scores
                </button>
                <div id="esg-table" class="table-container"></div>
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
            window.app.showLoading();
            const supplierId = document.getElementById('explain-supplier-id').value;
            const explanationType = document.getElementById('explanation-type').value;

            const result = await (window.api).explainPrediction(supplierId, 'supplier_scoring', explanationType);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            document.getElementById('explanation-results').style.display = 'block';
            const explanation = result.explanation || {};

            if (explanationType === 'lime') {
                const expList = explanation.explanation || [];
                let html = `<h5>Feature Contributions:</h5><ul>`;
                expList.slice(0, 10).forEach(([feature, contribution]) => {
                    const color = contribution > 0 ? 'green' : 'red';
                    html += `<li><strong>${feature}</strong>: <span style="color: ${color}">${utils.formatNumber(contribution, 4)}</span></li>`;
                });
                html += `</ul><p><strong>Prediction:</strong> ${utils.formatNumber(explanation.prediction, 3)}</p>`;
                document.getElementById('explanation-display').innerHTML = html;
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
                    y: sorted.map(([k, _]) => k),
                    type: 'bar',
                    orientation: 'h',
                    marker: { color: sorted.map(([_, v]) => v), colorscale: 'RdBu' }
                }];
                Plotly.newPlot('explanation-display', chartData, {
                    title: 'SHAP Feature Importance',
                    xaxis: { title: 'SHAP Value' },
                    yaxis: { title: 'Feature' },
                    height: 400
                });
            }

            window.app.showSuccess('Explanation generated successfully!');
        } catch (error) {
            window.app.showError('Failed to generate explanation: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async detectBias() {
        try {
            window.app.showLoading();
            const featureName = document.getElementById('bias-feature').value;

            const result = await (window.api).detectBias(featureName);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            document.getElementById('bias-results').style.display = 'block';
            const correlation = result.correlation || 0;
            let html = `<p><strong>Correlation with Predictions:</strong> ${utils.formatNumber(correlation, 3)}</p>`;

            if (Math.abs(correlation) > 0.3) {
                html += `<div class="alert alert-warning">⚠️ Potential bias detected! High correlation with predictions.</div>`;
            } else {
                html += `<div class="alert alert-success">✅ Low correlation - bias unlikely</div>`;
            }

            if (result.bias_analysis) {
                html += `<div class="table-container mt-3"></div>`;
                document.getElementById('bias-display').innerHTML = html;
                utils.createTable(result.bias_analysis, 'bias-display .table-container');
            } else {
                document.getElementById('bias-display').innerHTML = html;
            }

            window.app.showSuccess('Bias analysis complete!');
        } catch (error) {
            window.app.showError('Failed to detect bias: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async loadESGScores() {
        try {
            window.app.showLoading();
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
            window.app.hideLoading();
        }
    }
};

