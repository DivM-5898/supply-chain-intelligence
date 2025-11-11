// Risk Profiling Page JavaScript
window.RiskProfilingPage = {
    async init() {
        const container = document.getElementById('page-risk-profiling');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
    },

    getHTML() {
        return `
            <div class="card mb-4">
                <h1 class="card-title">🛡️ Risk Profiling & Comparison</h1>
                <p class="lead">What data sources are used for supplier risk profiling?</p>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">📊 Data Sources</h3>
                <button id="load-data-sources-btn" class="btn btn-primary mb-3">
                    <i class="fas fa-database"></i> View Data Sources
                </button>
                <div id="data-sources-table" class="table-container"></div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🔮 Risk Prediction</h3>
                <button id="predict-risk-btn" class="btn btn-primary mb-3">
                    <i class="fas fa-crystal-ball"></i> Predict Supplier Risk
                </button>
                <div id="risk-results" style="display: none;">
                    <div id="risk-distribution-chart" class="chart-container mb-3"></div>
                    <div id="risk-table" class="table-container"></div>
                </div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🚨 Anomaly Detection</h3>
                <button id="detect-anomalies-btn" class="btn btn-warning mb-3">
                    <i class="fas fa-exclamation-triangle"></i> Detect Anomalies
                </button>
                <div id="anomalies-results" style="display: none;">
                    <div id="anomalies-table" class="table-container"></div>
                </div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🌍 Geographic Risk Distribution</h3>
                <button id="load-geo-risk-btn" class="btn btn-primary mb-3">
                    <i class="fas fa-globe"></i> View Geographic Risk Map
                </button>
                <div id="geo-risk-chart" class="chart-container-large"></div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('load-data-sources-btn').addEventListener('click', () => this.loadDataSources());
        document.getElementById('predict-risk-btn').addEventListener('click', () => this.predictRisk());
        document.getElementById('detect-anomalies-btn').addEventListener('click', () => this.detectAnomalies());
        document.getElementById('load-geo-risk-btn').addEventListener('click', () => this.loadGeographicRisk());
    },

    async loadDataSources() {
        try {
            window.app.showLoading();
            const result = await (window.api).getDataSources();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }
            utils.createTable(result.data_sources || [], 'data-sources-table');
            window.app.showSuccess('Data sources loaded successfully!');
        } catch (error) {
            window.app.showError('Failed to load data sources: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async predictRisk() {
        try {
            window.app.showLoading();
            const result = await (window.api).predictRisk();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const risks = result.results || [];
            document.getElementById('risk-results').style.display = 'block';

            // Risk distribution chart
            const riskCounts = {};
            risks.forEach(r => {
                const level = r.risk_level || 'Unknown';
                riskCounts[level] = (riskCounts[level] || 0) + 1;
            });

            const chartData = [{
                x: Object.keys(riskCounts),
                y: Object.values(riskCounts),
                type: 'bar',
                marker: { color: ['#10b981', '#f59e0b', '#ef4444'] }
            }];
            Plotly.newPlot('risk-distribution-chart', chartData, {
                title: 'Risk Distribution',
                xaxis: { title: 'Risk Level' },
                yaxis: { title: 'Count' },
                height: 400
            });

            // Risk table
            utils.createTable(risks.slice(0, 20), 'risk-table', [
                { key: 'supplier_id', label: 'Supplier ID' },
                { key: 'risk_probability', label: 'Risk Probability', format: (v) => utils.formatPercentage(v) },
                { key: 'risk_level', label: 'Risk Level' }
            ]);

            window.app.showSuccess(`Analyzed ${result.total_suppliers} suppliers!`);
        } catch (error) {
            window.app.showError('Failed to predict risk: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async detectAnomalies() {
        try {
            window.app.showLoading();
            const result = await (window.api).detectAnomalies();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const anomalies = result.results || [];
            const detected = anomalies.filter(a => a.is_anomaly);
            
            document.getElementById('anomalies-results').style.display = 'block';
            
            if (detected.length > 0) {
                window.app.showError(`⚠️ ${detected.length} anomalies detected!`);
                utils.createTable(detected, 'anomalies-table', [
                    { key: 'supplier_id', label: 'Supplier ID' },
                    { key: 'anomaly_score', label: 'Anomaly Score', format: (v) => utils.formatNumber(v, 3) },
                    { key: 'severity', label: 'Severity' }
                ]);
            } else {
                window.app.showSuccess('No anomalies detected!');
            }
        } catch (error) {
            window.app.showError('Failed to detect anomalies: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async loadGeographicRisk() {
        try {
            window.app.showLoading();
            const result = await (window.api).getGeographicRisk();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const geoData = result.geographic_risk || [];
            const chartData = [{
                type: 'choropleth',
                locationmode: 'country names',
                locations: geoData.map(d => d.country),
                z: geoData.map(d => d.overall_risk_score),
                colorscale: 'RdYlGn_r',
                colorbar: { title: 'Risk Score' }
            }];
            const chartLayout = {
                title: 'Geographic Risk Distribution',
                geo: { projection: { type: 'natural earth' } },
                height: 600
            };
            Plotly.newPlot('geo-risk-chart', chartData, chartLayout);
            window.app.showSuccess('Geographic risk map loaded!');
        } catch (error) {
            window.app.showError('Failed to load geographic risk: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    }
};

