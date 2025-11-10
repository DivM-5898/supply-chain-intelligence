// NLP Contract Analyzer Page JavaScript
window.NLPContractPage = {
    async init() {
        const container = document.getElementById('page-nlp-contract');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
    },

    getHTML() {
        return `
            <div class="card mb-4">
                <h1 class="card-title">📄 NLP Contract Analyzer</h1>
                <p class="lead">What role does natural language processing (NLP) play in analyzing supplier documents and contracts?</p>
            </div>

            <div class="card mb-4">
                <h3 class="card-title">Upload or Enter Contract</h3>
                <div class="form-group">
                    <label class="form-label">Input Method</label>
                    <select id="input-method" class="form-control">
                        <option value="upload">Upload File</option>
                        <option value="text">Enter Text</option>
                        <option value="library">Select from Library</option>
                    </select>
                </div>
                <div id="upload-section">
                    <div class="form-group">
                        <label class="form-label">Upload Contract File</label>
                        <input type="file" id="contract-file" class="form-control" accept=".txt,.pdf">
                    </div>
                </div>
                <div id="text-section" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Enter Contract Text</label>
                        <textarea id="contract-text" class="form-control" rows="10" placeholder="Paste contract text here..."></textarea>
                    </div>
                </div>
                <div id="library-section" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Select Contract</label>
                        <select id="contract-select" class="form-control"></select>
                    </div>
                </div>
                <button id="analyze-btn" class="btn btn-primary">
                    <i class="fas fa-search"></i> Analyze Contract
                </button>
            </div>

            <div id="analysis-results" style="display: none;">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Entities Found</div>
                        <div class="metric-value" id="entity-count">0</div>
                    </div>
                    <div class="metric-card success">
                        <div class="metric-label">Key Clauses</div>
                        <div class="metric-value" id="clause-count">0</div>
                    </div>
                    <div class="metric-card warning">
                        <div class="metric-label">Sentiment</div>
                        <div class="metric-value" id="sentiment-value">N/A</div>
                    </div>
                    <div class="metric-card danger">
                        <div class="metric-label">Risk Level</div>
                        <div class="metric-value" id="risk-level-value">N/A</div>
                    </div>
                </div>

                <div class="card mb-4">
                    <h3 class="card-title">🏷️ Named Entities</h3>
                    <div id="entities-display" class="row"></div>
                </div>

                <div class="card mb-4">
                    <h3 class="card-title">📋 Key Clauses</h3>
                    <div id="clauses-display"></div>
                </div>

                <div class="card mb-4">
                    <h3 class="card-title">⚠️ Risk Terms</h3>
                    <div id="risk-terms-display" class="row"></div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('input-method').addEventListener('change', (e) => this.handleInputMethodChange(e.target.value));
        document.getElementById('analyze-btn').addEventListener('click', () => this.analyzeContract());
        this.loadContractLibrary();
    },

    handleInputMethodChange(method) {
        document.getElementById('upload-section').style.display = method === 'upload' ? 'block' : 'none';
        document.getElementById('text-section').style.display = method === 'text' ? 'block' : 'none';
        document.getElementById('library-section').style.display = method === 'library' ? 'block' : 'none';
    },

    async loadContractLibrary() {
        try {
            const result = await (window.api).listContracts();
            if (result.contracts) {
                const select = document.getElementById('contract-select');
                select.innerHTML = '<option value="">Select a contract...</option>';
                result.contracts.forEach(contract => {
                    const option = document.createElement('option');
                    option.value = contract.contract_id;
                    option.textContent = `${contract.contract_id} - ${contract.contract_type}`;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load contract library:', error);
        }
    },

    async analyzeContract() {
        try {
            window.app.showLoading();
            const method = document.getElementById('input-method').value;
            let result;

            if (method === 'upload') {
                const file = document.getElementById('contract-file').files[0];
                if (!file) {
                    window.app.showError('Please select a file');
                    return;
                }
                result = await (window.api).uploadContract(file);
            } else if (method === 'text') {
                const text = document.getElementById('contract-text').value;
                if (!text.trim()) {
                    window.app.showError('Please enter contract text');
                    return;
                }
                result = await (window.api).analyzeContract(text, null);
            } else {
                const contractId = document.getElementById('contract-select').value;
                if (!contractId) {
                    window.app.showError('Please select a contract');
                    return;
                }
                result = await (window.api).analyzeContract(null, contractId);
            }

            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            this.displayAnalysis(result.analysis);
            window.app.showSuccess('Contract analyzed successfully!');
        } catch (error) {
            window.app.showError('Failed to analyze contract: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    displayAnalysis(analysis) {
        document.getElementById('analysis-results').style.display = 'block';
        const summary = analysis.summary || {};

        // Update metrics
        document.getElementById('entity-count').textContent = summary.total_entities || 0;
        document.getElementById('clause-count').textContent = summary.key_clauses_found || 0;
        document.getElementById('sentiment-value').textContent = summary.overall_sentiment || 'N/A';
        document.getElementById('risk-level-value').textContent = summary.risk_level || 'N/A';

        // Display entities
        const entities = analysis.entities || {};
        const entitiesDisplay = document.getElementById('entities-display');
        entitiesDisplay.innerHTML = '';
        Object.entries(entities).forEach(([type, items]) => {
            if (items && items.length > 0) {
                const col = document.createElement('div');
                col.className = 'col-md-6 mb-3';
                col.innerHTML = `
                    <div class="card">
                        <h5>${type.replace(/_/g, ' ').toUpperCase()}</h5>
                        <ul>
                            ${items.slice(0, 5).map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                `;
                entitiesDisplay.appendChild(col);
            }
        });

        // Display clauses
        const clauses = analysis.clauses || {};
        const clausesDisplay = document.getElementById('clauses-display');
        clausesDisplay.innerHTML = '';
        Object.entries(clauses).forEach(([type, items]) => {
            if (items && items.length > 0) {
                const card = document.createElement('div');
                card.className = 'card mb-3';
                card.innerHTML = `
                    <h5>${type.replace(/_/g, ' ').toUpperCase()} (${items.length} found)</h5>
                    ${items.slice(0, 3).map(item => `<p class="text-secondary">${item.substring(0, 200)}...</p>`).join('')}
                `;
                clausesDisplay.appendChild(card);
            }
        });

        // Display risk terms
        const riskTerms = analysis.risk_terms || {};
        const riskDisplay = document.getElementById('risk-terms-display');
        riskDisplay.innerHTML = '';
        ['high_risk', 'medium_risk', 'low_risk'].forEach(level => {
            const terms = riskTerms[level] || [];
            if (terms.length > 0) {
                const col = document.createElement('div');
                col.className = 'col-md-4 mb-3';
                const colorClass = level === 'high_risk' ? 'danger' : level === 'medium_risk' ? 'warning' : 'success';
                col.innerHTML = `
                    <div class="card alert-${colorClass}">
                        <h5>${level.replace(/_/g, ' ').toUpperCase()}</h5>
                        <p>${terms.length} terms found</p>
                        <ul>
                            ${terms.slice(0, 3).map(term => `<li>${term.term || term}</li>`).join('')}
                        </ul>
                    </div>
                `;
                riskDisplay.appendChild(col);
            }
        });
    }
};

