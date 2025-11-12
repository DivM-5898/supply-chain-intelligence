// Decision Support Page JavaScript
window.DecisionSupportPage = {
    async init() {
        const container = document.getElementById('page-decision-support');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
    },

    getHTML() {
        return `
            <div class="card mb-4">
                <h1 class="card-title">⚖️ Multi-Criteria Decision Support</h1>
                <p class="lead">How can AI support multi-criteria decision-making in procurement?</p>
            </div>

            <div class="card mb-4">
                <div class="form-group">
                    <label class="form-label">Select Method</label>
                    <select id="decision-method" class="form-control">
                        <option value="topsis">TOPSIS</option>
                        <option value="ahp">AHP</option>
                    </select>
                </div>
            </div>

            <div id="topsis-section">
                <div class="card mb-4">
                    <h3 class="card-title">📊 TOPSIS Ranking</h3>
                    <p>Define criteria weights (will be normalized automatically)</p>
                    <div id="topsis-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                        <div style="display: inline-block;">
                            <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                                <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                                <div style="font-size: 1rem; font-weight: 500;">
                                    Running TOPSIS analysis... Please wait
                                </div>
                            </div>
                        </div>
                    </div>
                    <div id="topsis-content">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label class="form-label">Cost Weight</label>
                                <input type="range" id="weight-cost" class="form-control" min="0" max="1" step="0.1" value="0.3">
                                <span id="weight-cost-value">0.3</span>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Quality Weight</label>
                                <input type="range" id="weight-quality" class="form-control" min="0" max="1" step="0.1" value="0.25">
                                <span id="weight-quality-value">0.25</span>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Delivery Weight</label>
                                <input type="range" id="weight-delivery" class="form-control" min="0" max="1" step="0.1" value="0.2">
                                <span id="weight-delivery-value">0.2</span>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label class="form-label">Risk Weight</label>
                                <input type="range" id="weight-risk" class="form-control" min="0" max="1" step="0.1" value="0.15">
                                <span id="weight-risk-value">0.15</span>
                            </div>
                            <div class="form-group">
                                <label class="form-label">ESG Weight</label>
                                <input type="range" id="weight-esg" class="form-control" min="0" max="1" step="0.1" value="0.1">
                                <span id="weight-esg-value">0.1</span>
                            </div>
                        </div>
                    </div>
                    <button id="run-topsis-btn" class="btn btn-primary">
                        <i class="fas fa-calculator"></i> Run TOPSIS Analysis
                    </button>
                    </div>
                </div>
            </div>

            <div id="ahp-section" style="display: none;">
                <div class="card mb-4">
                    <h3 class="card-title">📊 AHP Ranking</h3>
                    <p>Pairwise Comparisons (1-9 scale: 1 = equally important, 9 = extremely more important)</p>
                    <div id="ahp-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                        <div style="display: inline-block;">
                            <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                                <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                                <div style="font-size: 1rem; font-weight: 500;">
                                    Running AHP analysis... Please wait
                                </div>
                            </div>
                        </div>
                    </div>
                    <div id="ahp-content">
                    <div id="ahp-comparisons"></div>
                    <button id="run-ahp-btn" class="btn btn-primary">
                        <i class="fas fa-calculator"></i> Run AHP Analysis
                    </button>
                    </div>
                </div>
            </div>

            <div id="decision-results" style="display: none;">
                <div class="card mb-4">
                    <h3 class="card-title">📈 Rankings</h3>
                    <div id="decision-chart" class="chart-container"></div>
                    <div id="decision-table" class="table-container mt-3"></div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('decision-method').addEventListener('change', (e) => {
            document.getElementById('topsis-section').style.display = e.target.value === 'topsis' ? 'block' : 'none';
            document.getElementById('ahp-section').style.display = e.target.value === 'ahp' ? 'block' : 'none';
            if (e.target.value === 'ahp') {
                this.setupAHPComparisons();
            }
        });

        // Update weight displays
        ['cost', 'quality', 'delivery', 'risk', 'esg'].forEach(weight => {
            const slider = document.getElementById(`weight-${weight}`);
            const display = document.getElementById(`weight-${weight}-value`);
            slider.addEventListener('input', (e) => {
                display.textContent = e.target.value;
            });
        });

        document.getElementById('run-topsis-btn').addEventListener('click', () => this.runTOPSIS());
        document.getElementById('run-ahp-btn').addEventListener('click', () => this.runAHP());
    },

    setupAHPComparisons() {
        const criteria = ['Cost', 'Quality', 'Delivery', 'Risk', 'ESG'];
        const container = document.getElementById('ahp-comparisons');
        container.innerHTML = '';

        criteria.forEach((c1, i) => {
            criteria.slice(i + 1).forEach(c2 => {
                const div = document.createElement('div');
                div.className = 'form-group row';
                div.innerHTML = `
                    <div class="col-md-4">
                        <label>${c1} vs ${c2}</label>
                    </div>
                    <div class="col-md-8">
                        <input type="range" class="form-control" min="1" max="9" step="1" value="1" 
                               data-c1="${c1.toLowerCase()}" data-c2="${c2.toLowerCase()}" id="ahp-${c1}-${c2}">
                        <span id="ahp-${c1}-${c2}-value">1</span>
                    </div>
                `;
                container.appendChild(div);

                const slider = div.querySelector('input[type="range"]');
                const display = div.querySelector('span');
                slider.addEventListener('input', (e) => {
                    display.textContent = e.target.value;
                });
            });
        });
    },

    async runTOPSIS() {
        try {
            this.showLoading('topsis');
            const weights = {
                unit_cost: parseFloat(document.getElementById('weight-cost').value),
                quality_score: parseFloat(document.getElementById('weight-quality').value),
                on_time_delivery_rate: parseFloat(document.getElementById('weight-delivery').value),
                geopolitical_risk_score: parseFloat(document.getElementById('weight-risk').value),
                esg_score: parseFloat(document.getElementById('weight-esg').value)
            };

            const result = await (window.api).topsisRanking(weights);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            this.displayResults(result.results, 'TOPSIS');
            window.app.showSuccess('TOPSIS analysis complete!');
        } catch (error) {
            window.app.showError('Failed to run TOPSIS: ' + error.message);
        } finally {
            this.hideLoading('topsis');
        }
    },

    async runAHP() {
        try {
            this.showLoading('ahp');
            const criteria = ['unit_cost', 'quality_score', 'on_time_delivery_rate', 'geopolitical_risk_score', 'esg_score'];
            const comparisons = {};

            // Collect pairwise comparisons
            document.querySelectorAll('#ahp-comparisons input[type="range"]').forEach(input => {
                const c1 = input.getAttribute('data-c1');
                const c2 = input.getAttribute('data-c2');
                const value = parseFloat(input.value);

                if (!comparisons[c1]) comparisons[c1] = {};
                if (!comparisons[c2]) comparisons[c2] = {};
                comparisons[c1][c2] = value;
                comparisons[c2][c1] = 1 / value;
            });

            const result = await (window.api).ahpRanking(criteria, comparisons);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            if (result.consistency_ratio < 0.1) {
                window.app.showSuccess(`AHP analysis complete! Consistency Ratio: ${result.consistency_ratio.toFixed(3)} (Acceptable)`);
            } else {
                window.app.showError(`⚠️ Consistency Ratio: ${result.consistency_ratio.toFixed(3)} (May need review)`);
            }

            this.displayResults(result.results, 'AHP');
        } catch (error) {
            window.app.showError('Failed to run AHP: ' + error.message);
        } finally {
            this.hideLoading('ahp');
        }
    },

    displayResults(results, method) {
        document.getElementById('decision-results').style.display = 'block';
        const top10 = results.slice(0, 10);

        const scoreKey = method === 'TOPSIS' ? 'topsis_score' : 'ahp_score';
        const chartData = [{
            x: top10.map(r => r.alternative),
            y: top10.map(r => r[scoreKey]),
            type: 'bar',
            marker: { color: top10.map(r => r[scoreKey]), colorscale: 'Viridis' }
        }];
        Plotly.newPlot('decision-chart', chartData, {
            title: `${method} Rankings`,
            xaxis: { title: 'Supplier ID' },
            yaxis: { title: `${method} Score` },
            height: 400
        });

        utils.createTable(results.slice(0, 20), 'decision-table', [
            { key: 'rank', label: 'Rank' },
            { key: 'alternative', label: 'Supplier ID' },
            { key: scoreKey, label: 'Score', format: (v) => utils.formatNumber(v, 3) }
        ]);
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

