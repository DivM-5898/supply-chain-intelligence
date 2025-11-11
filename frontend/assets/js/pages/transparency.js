// Transparency & Resilience Page JavaScript
window.TransparencyPage = {
    async init() {
        const container = document.getElementById('page-transparency');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
    },

    getHTML() {
        return `
            <div class="card mb-4">
                <h1 class="card-title">🌐 Transparency & Resilience</h1>
                <p class="lead">How can AI enhance transparency and resilience in global supply chains?</p>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🌍 Geographic Risk Distribution</h3>
                <button id="load-geo-risk-btn" class="btn btn-primary mb-3">
                    <i class="fas fa-globe"></i> View Geographic Risk Map
                </button>
                <div id="geo-risk-chart" class="chart-container-large"></div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">🔗 Supplier Network Visualization</h3>
                <button id="load-network-btn" class="btn btn-primary mb-3">
                    <i class="fas fa-project-diagram"></i> View Supplier Network
                </button>
                <div id="network-stats" class="metrics-grid mb-3"></div>
                <div id="network-chart" class="chart-container"></div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">💪 Resilience Metrics</h3>
                <button id="load-resilience-btn" class="btn btn-success mb-3">
                    <i class="fas fa-shield-alt"></i> Calculate Resilience Metrics
                </button>
                <div id="resilience-results" style="display: none;">
                    <div id="resilience-distribution-chart" class="chart-container mb-3"></div>
                    <div class="row">
                        <div class="col-md-6">
                            <h5>Most Resilient Suppliers</h5>
                            <div id="top-resilient-table" class="table-container"></div>
                        </div>
                        <div class="col-md-6">
                            <h5>Least Resilient Suppliers</h5>
                            <div id="bottom-resilient-table" class="table-container"></div>
                        </div>
                    </div>
                    <div id="resilience-3d-chart" class="chart-container-large mt-3"></div>
                </div>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">👁️ Transparency Scores</h3>
                <button id="load-transparency-btn" class="btn btn-info mb-3">
                    <i class="fas fa-eye"></i> View Transparency Scores
                </button>
                <div id="transparency-table" class="table-container"></div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('load-geo-risk-btn').addEventListener('click', () => this.loadGeographicRisk());
        document.getElementById('load-network-btn').addEventListener('click', () => this.loadSupplierNetwork());
        document.getElementById('load-resilience-btn').addEventListener('click', () => this.loadResilienceMetrics());
        document.getElementById('load-transparency-btn').addEventListener('click', () => this.loadTransparencyScores());
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
                colorbar: { title: 'Risk Score' },
                text: geoData.map(d => `${d.country}: ${utils.formatNumber(d.overall_risk_score, 2)}`)
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
    },

    async loadSupplierNetwork() {
        try {
            window.app.showLoading();
            const result = await (window.api).getSupplierNetwork();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const nodes = result.nodes || [];
            
            // Display stats
            const countries = new Set(nodes.map(n => n.country)).size;
            const industries = new Set(nodes.map(n => n.industry)).size;
            const avgESG = nodes.reduce((sum, n) => sum + (n.value || 0), 0) / nodes.length;

            document.getElementById('network-stats').innerHTML = `
                <div class="metric-card">
                    <div class="metric-label">Countries</div>
                    <div class="metric-value">${countries}</div>
                </div>
                <div class="metric-card success">
                    <div class="metric-label">Industries</div>
                    <div class="metric-value">${industries}</div>
                </div>
                <div class="metric-card warning">
                    <div class="metric-label">Avg ESG Score</div>
                    <div class="metric-value">${utils.formatNumber(avgESG, 2)}</div>
                </div>
            `;

            // Country distribution chart
            const countryCounts = {};
            nodes.forEach(n => {
                countryCounts[n.country] = (countryCounts[n.country] || 0) + 1;
            });

            const sortedCountries = Object.entries(countryCounts)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10);

            const chartData = [{
                x: sortedCountries.map(([_, count]) => count),
                y: sortedCountries.map(([country, _]) => country),
                type: 'bar',
                orientation: 'h',
                marker: { color: '#2563eb' }
            }];
            Plotly.newPlot('network-chart', chartData, {
                title: 'Top 10 Countries by Supplier Count',
                xaxis: { title: 'Number of Suppliers' },
                yaxis: { title: 'Country' },
                height: 400
            });

            window.app.showSuccess(`Loaded ${nodes.length} suppliers in network!`);
        } catch (error) {
            window.app.showError('Failed to load supplier network: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async loadResilienceMetrics() {
        try {
            window.app.showLoading();
            const result = await (window.api).getResilienceMetrics();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const metrics = result.resilience_metrics || [];
            document.getElementById('resilience-results').style.display = 'block';

            // Distribution chart
            const chartData = [{
                x: metrics.map(m => m.resilience_score),
                type: 'histogram',
                marker: { color: '#10b981' }
            }];
            Plotly.newPlot('resilience-distribution-chart', chartData, {
                title: 'Resilience Score Distribution',
                xaxis: { title: 'Resilience Score' },
                yaxis: { title: 'Frequency' },
                height: 400
            });

            // Top and bottom suppliers
            const sorted = [...metrics].sort((a, b) => b.resilience_score - a.resilience_score);
            utils.createTable(sorted.slice(0, 10), 'top-resilient-table', [
                { key: 'supplier_id', label: 'Supplier ID' },
                { key: 'resilience_score', label: 'Resilience Score', format: (v) => utils.formatNumber(v, 3) }
            ]);
            utils.createTable(sorted.slice(-10).reverse(), 'bottom-resilient-table', [
                { key: 'supplier_id', label: 'Supplier ID' },
                { key: 'resilience_score', label: 'Resilience Score', format: (v) => utils.formatNumber(v, 3) }
            ]);

            // 3D scatter plot
            const top50 = sorted.slice(0, 50);
            const chart3D = [{
                x: top50.map(m => m.geographic_risk),
                y: top50.map(m => m.esg_score),
                z: top50.map(m => m.resilience_score),
                mode: 'markers',
                type: 'scatter3d',
                marker: {
                    size: 8,
                    color: top50.map(m => m.risk_event_count),
                    colorscale: 'Viridis',
                    showscale: true
                },
                text: top50.map(m => m.supplier_id)
            }];
            Plotly.newPlot('resilience-3d-chart', chart3D, {
                title: '3D Resilience Analysis',
                scene: {
                    xaxis: { title: 'Geographic Risk' },
                    yaxis: { title: 'ESG Score' },
                    zaxis: { title: 'Resilience Score' }
                },
                height: 600
            });

            window.app.showSuccess(`Calculated resilience for ${metrics.length} suppliers!`);
        } catch (error) {
            window.app.showError('Failed to load resilience metrics: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    async loadTransparencyScores() {
        try {
            window.app.showLoading();
            const result = await (window.api).getTransparencyScores();
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            utils.createTable(result.transparency_scores || [], 'transparency-table', [
                { key: 'supplier_id', label: 'Supplier ID' },
                { key: 'name', label: 'Name' },
                { key: 'country', label: 'Country' },
                { key: 'transparency_score', label: 'Transparency Score', format: (v) => utils.formatNumber(v, 3) },
                { key: 'esg_score', label: 'ESG Score', format: (v) => utils.formatNumber(v, 3) },
                { key: 'compliance_score', label: 'Compliance Score', format: (v) => utils.formatNumber(v, 3) }
            ]);

            window.app.showSuccess('Transparency scores loaded successfully!');
        } catch (error) {
            window.app.showError('Failed to load transparency scores: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    }
};

