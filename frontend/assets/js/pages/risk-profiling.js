// Risk Profiling Page JavaScript
window.RiskProfilingPage = {
    // Store current evaluation data for chatbot
    currentRiskData: {
        csvData: null,
        results: null,
        fileName: null,
        riskResults: null,
        anomalyResults: null
    },

    // Pagination state
    riskPaginationState: {
        currentPage: 1,
        pageSize: 25,
        filter: 'all',
        allData: []
    },

    async init() {
        const container = document.getElementById('page-risk-profiling');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
        this.checkPreviousCSV();
    },

    checkPreviousCSV() {
        // Check if there's a CSV from Supplier Evaluation page
        if (window.SupplierEvaluationPage && window.SupplierEvaluationPage.currentEvaluationData && 
            window.SupplierEvaluationPage.currentEvaluationData.csvData) {
            const prevData = window.SupplierEvaluationPage.currentEvaluationData;
            this.currentRiskData.csvData = prevData.csvData;
            this.currentRiskData.fileName = prevData.fileName;
            
            // Show option to use previous CSV
            const csvOptionDiv = document.getElementById('csv-option-section');
            if (csvOptionDiv) {
                csvOptionDiv.innerHTML = `
                    <div class="alert alert-info" style="margin-bottom: 1rem;">
                        <strong>Previous CSV Available:</strong> ${prevData.fileName} from Supplier Evaluation page
                        <button id="use-previous-csv-btn" class="btn btn-sm btn-primary ml-2">
                            <i class="fas fa-check"></i> Use This CSV
                        </button>
                    </div>
                `;
                document.getElementById('use-previous-csv-btn').addEventListener('click', () => {
                    this.usePreviousCSV();
                });
            }
        }
    },

    usePreviousCSV() {
        const prevData = window.SupplierEvaluationPage.currentEvaluationData;
        this.currentRiskData.csvData = prevData.csvData;
        this.currentRiskData.fileName = prevData.fileName;
        window.app.showSuccess(`Using CSV: ${prevData.fileName}`);
        document.getElementById('file-name-display-risk').textContent = prevData.fileName;
        document.getElementById('file-info-risk').style.display = 'block';
    },

    getHTML() {
        return `
            <div class="card mb-4" data-aos="fade-up">
                <div class="card-header-custom">
                    <h1><i class="fas fa-shield-alt"></i> Risk Profiling & Comparison</h1>
                </div>
                <div class="card-body">
                    <p class="lead">Analyze supplier risks, detect anomalies, and get AI-powered insights</p>
                </div>
            </div>

            <!-- CSV Upload Section -->
            <div class="card mb-4" data-aos="fade-up" data-aos-delay="100">
                <div class="card-header-custom" style="background: linear-gradient(135deg, var(--corp-primary) 0%, var(--corp-primary-dark) 100%); color: white;">
                    <h3><i class="fas fa-file-upload"></i> Data Source</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div id="csv-option-section"></div>
                    <div class="mb-3">
                        <label class="form-label-custom">
                            <i class="fas fa-file-csv"></i> Upload CSV/Excel File for Risk Analysis
                        </label>
                        <input type="file" id="file-input-risk" class="form-control-custom" accept=".csv,.xlsx,.xls">
                        <small class="form-text text-muted">Upload supplier data for risk profiling and anomaly detection</small>
                    </div>
                    <div id="file-info-risk" style="display: none; margin-top: 1rem;">
                        <div class="alert alert-info">
                            <i class="fas fa-file"></i> Selected file: <span id="file-name-display-risk"></span>
                        </div>
                    </div>
                    <button id="upload-csv-risk-btn" class="btn-primary-custom" disabled>
                        <i class="fas fa-upload"></i> Upload & Analyze Risk
                    </button>
                </div>
            </div>

            <div class="card mb-4" data-aos="fade-up" data-aos-delay="200">
                <div class="card-header-custom">
                    <h3><i class="fas fa-database"></i> Data Sources</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <button id="load-data-sources-btn" class="btn-secondary-custom mb-3">
                        <i class="fas fa-database"></i> View Data Sources
                    </button>
                    <div id="data-sources-table" class="table-container-enhanced"></div>
                </div>
            </div>

            <div class="card mb-4" data-aos="fade-up" data-aos-delay="300">
                <div class="card-header-custom">
                    <h3><i class="fas fa-crystal-ball"></i> Risk Prediction</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <button id="predict-risk-btn" class="btn-primary-custom mb-3">
                        <i class="fas fa-crystal-ball"></i> Predict Supplier Risk
                    </button>
                    <div id="risk-results" style="display: none;">
                        <div id="risk-distribution-chart" class="chart-container-enhanced mb-3"></div>
                        
                        <!-- Filter and Pagination Controls -->
                        <div class="mb-3" style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                            <div>
                                <label class="form-label-custom"><i class="fas fa-filter"></i> Filter by Risk Level:</label>
                                <select id="risk-filter" class="form-control-custom" style="width: 200px;">
                                    <option value="all">All Suppliers</option>
                                    <option value="High">High Risk</option>
                                    <option value="Medium">Medium Risk</option>
                                    <option value="Low">Low Risk</option>
                                </select>
                            </div>
                            <div>
                                <label class="form-label-custom"><i class="fas fa-list"></i> Items per page:</label>
                                <select id="risk-page-size" class="form-control-custom" style="width: 120px;">
                                    <option value="10">10</option>
                                    <option value="25" selected>25</option>
                                    <option value="50">50</option>
                                    <option value="100">100</option>
                                    <option value="all">All</option>
                                </select>
                            </div>
                            <div style="margin-left: auto;">
                                <span id="risk-count-display" style="font-weight: 600; color: var(--corp-primary);"></span>
                            </div>
                        </div>
                        
                        <div id="risk-table" class="table-container-enhanced"></div>
                        
                        <!-- Pagination Controls -->
                        <div id="risk-pagination" class="mt-3" style="display: flex; justify-content: center; gap: 0.5rem;"></div>
                    </div>
                </div>
            </div>

            <div class="card mb-4" data-aos="fade-up" data-aos-delay="400">
                <div class="card-header-custom">
                    <h3><i class="fas fa-exclamation-triangle"></i> Anomaly Detection</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <button id="detect-anomalies-btn" class="btn-secondary-custom mb-3">
                        <i class="fas fa-exclamation-triangle"></i> Detect Anomalies
                    </button>
                    <div id="anomalies-results" style="display: none;">
                        <div id="anomalies-table" class="table-container-enhanced"></div>
                    </div>
                </div>
            </div>

            <!-- AI Chatbot for Risk Analysis -->
            <div class="card mb-4" data-aos="fade-up" data-aos-delay="500">
                <div class="card-header-custom">
                    <h3><i class="fas fa-robot"></i> AI Risk Analysis Assistant</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <p class="mb-3" style="color: var(--corp-gray-600);">
                        Get AI-powered explanations for risk predictions and anomaly detection. The assistant analyzes your uploaded data, 
                        risk results, and anomalies to provide detailed rationale.
                    </p>
                    <div id="chatbot-container-risk" style="border: 1px solid var(--corp-gray-200); border-radius: 8px; background: white; min-height: 400px; max-height: 600px; display: flex; flex-direction: column;">
                        <div id="chatbot-messages-risk" style="flex: 1; padding: 1.5rem; overflow-y: auto; max-height: 450px;">
                            <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                                    <i class="fas fa-robot"></i> AI Assistant
                                </div>
                                <div style="color: var(--corp-gray-700);">
                                    Hello! I'm your AI Risk Analysis Assistant powered by Gemini 2.5 Flash. 
                                    Upload a CSV file, analyze risks and anomalies to see detailed explanations.
                                </div>
                            </div>
                        </div>
                        <div id="chatbot-input-container-risk" style="padding: 1rem; border-top: 1px solid var(--corp-gray-200); display: flex; gap: 0.5rem;">
                            <input type="text" id="chatbot-input-risk" class="form-control-custom" 
                                   placeholder="Ask about risks or anomalies..." 
                                   style="flex: 1;">
                            <button id="chatbot-send-btn-risk" class="btn-primary-custom" style="white-space: nowrap;">
                                <i class="fas fa-paper-plane"></i> Send
                            </button>
                        </div>
                    </div>
                    <div class="mt-3" style="text-align: center;">
                        <button id="get-risk-rationale-btn" class="btn-primary-custom">
                            <i class="fas fa-brain"></i> Get Risk Analysis Rationale
                        </button>
                        <button id="clear-chat-risk-btn" class="btn-secondary-custom ml-2">
                            <i class="fas fa-trash"></i> Clear Chat
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('load-data-sources-btn').addEventListener('click', () => this.loadDataSources());
        document.getElementById('predict-risk-btn').addEventListener('click', () => this.predictRisk());
        document.getElementById('detect-anomalies-btn').addEventListener('click', () => this.detectAnomalies());
        
        // File upload handlers
        const fileInput = document.getElementById('file-input-risk');
        const uploadBtn = document.getElementById('upload-csv-risk-btn');
        const fileInfo = document.getElementById('file-info-risk');
        const fileNameDisplay = document.getElementById('file-name-display-risk');
        
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
        
        uploadBtn.addEventListener('click', () => this.uploadAndAnalyzeRisk());
        
        // Chatbot handlers
        document.getElementById('get-risk-rationale-btn').addEventListener('click', () => this.getRiskRationale());
        document.getElementById('chatbot-send-btn-risk').addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chatbot-input-risk').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
        document.getElementById('clear-chat-risk-btn').addEventListener('click', () => this.clearChat());
    },

    async uploadAndAnalyzeRisk() {
        try {
            const fileInput = document.getElementById('file-input-risk');
            const file = fileInput.files[0];
            
            if (!file) {
                window.app.showError('Please select a file to upload');
                return;
            }
            
            window.app.showLoading();
            
            // Read CSV content for chatbot
            const csvText = await file.text();
            this.currentRiskData.csvData = csvText;
            this.currentRiskData.fileName = file.name;
            
            // Upload file and analyze
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${window.api.baseURL}/risk/upload-and-analyze`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText || 'Upload failed');
            }
            
            const result = await response.json();
            
            // Store results for chatbot
            this.currentRiskData.results = result.results || [];
            this.currentRiskData.riskResults = result.risk_results || [];
            this.currentRiskData.anomalyResults = result.anomaly_results || [];
            
            // Display results
            this.displayRiskResults(result);
            
            window.app.showSuccess(`Successfully analyzed ${result.total_suppliers || 0} suppliers for risk!`);
        } catch (error) {
            console.error('[RiskProfiling] Error uploading and analyzing:', error);
            window.app.showError('Failed to upload and analyze: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    displayRiskResults(result) {
        // Display risk results
        if (result.risk_results && result.risk_results.length > 0) {
            const risks = result.risk_results;
            this.riskPaginationState.allData = risks;
            this.riskPaginationState.currentPage = 1;
            
            document.getElementById('risk-results').style.display = 'block';
            
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
                height: 400,
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent'
            });
            
            // Setup filter and pagination listeners
            this.setupRiskFilterListeners();
            
            // Display paginated table
            this.displayRiskTable();
        }
        
        // Display anomaly results
        if (result.anomaly_results && result.anomaly_results.length > 0) {
            const anomalies = result.anomaly_results.filter(a => a.is_anomaly);
            document.getElementById('anomalies-results').style.display = 'block';
            
            if (anomalies.length > 0) {
                utils.createTable(anomalies, 'anomalies-table', [
                    { key: 'supplier_id', label: 'Supplier ID' },
                    { key: 'anomaly_score', label: 'Anomaly Score', format: (v) => utils.formatNumber(v, 3) },
                    { key: 'anomaly_reason', label: 'Anomaly Reason' },
                    { key: 'severity', label: 'Severity' }
                ]);
            }
        }
    },

    async loadDataSources() {
        try {
            window.app.showLoading();
            const result = await window.api.getDataSources();
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
            const supplierIds = this.currentRiskData.results ? 
                this.currentRiskData.results.map(r => r.supplier_id) : null;
            
            const result = await window.api.predictRisk(supplierIds);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const risks = result.results || [];
            this.currentRiskData.riskResults = risks;
            this.riskPaginationState.allData = risks;
            this.riskPaginationState.currentPage = 1;
            
            document.getElementById('risk-results').style.display = 'block';

            // Display risk distribution chart
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
                height: 400,
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent'
            });

            // Setup filter and pagination listeners
            this.setupRiskFilterListeners();
            
            // Display paginated table
            this.displayRiskTable();

            window.app.showSuccess(`Analyzed ${result.total_suppliers} suppliers!`);
        } catch (error) {
            window.app.showError('Failed to predict risk: ' + error.message);
        } finally {
            window.app.hideLoading();
        }
    },

    setupRiskFilterListeners() {
        const filterSelect = document.getElementById('risk-filter');
        const pageSizeSelect = document.getElementById('risk-page-size');
        
        if (filterSelect && !filterSelect.dataset.listenerAdded) {
            filterSelect.dataset.listenerAdded = 'true';
            filterSelect.addEventListener('change', (e) => {
                this.riskPaginationState.filter = e.target.value;
                this.riskPaginationState.currentPage = 1;
                this.displayRiskTable();
            });
        }
        
        if (pageSizeSelect && !pageSizeSelect.dataset.listenerAdded) {
            pageSizeSelect.dataset.listenerAdded = 'true';
            pageSizeSelect.addEventListener('change', (e) => {
                this.riskPaginationState.pageSize = e.target.value === 'all' ? 'all' : parseInt(e.target.value);
                this.riskPaginationState.currentPage = 1;
                this.displayRiskTable();
            });
        }
    },

    displayRiskTable() {
        const allData = this.riskPaginationState.allData;
        const filter = this.riskPaginationState.filter;
        const pageSize = this.riskPaginationState.pageSize;
        const currentPage = this.riskPaginationState.currentPage;
        
        // Filter data
        let filteredData = allData;
        if (filter !== 'all') {
            filteredData = allData.filter(r => r.risk_level === filter);
        }
        
        // Update count display
        const countDisplay = document.getElementById('risk-count-display');
        if (countDisplay) {
            countDisplay.textContent = `Showing ${filteredData.length} of ${allData.length} suppliers`;
        }
        
        // Paginate data
        let paginatedData = filteredData;
        let totalPages = 1;
        
        if (pageSize !== 'all') {
            totalPages = Math.ceil(filteredData.length / pageSize);
            const startIdx = (currentPage - 1) * pageSize;
            const endIdx = startIdx + pageSize;
            paginatedData = filteredData.slice(startIdx, endIdx);
        }
        
        // Create table with color-coded risk levels
        const tableData = paginatedData.map(r => ({
            ...r,
            risk_level: r.risk_level
        }));
        
        utils.createTable(tableData, 'risk-table', [
            { key: 'supplier_id', label: 'Supplier ID' },
            { key: 'risk_probability', label: 'Risk Probability', format: (v) => utils.formatPercentage(v) },
            { 
                key: 'risk_level', 
                label: 'Risk Level',
                format: (v) => {
                    const colors = {
                        'High': 'background: #ef4444; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 600;',
                        'Medium': 'background: #f59e0b; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 600;',
                        'Low': 'background: #10b981; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 600;'
                    };
                    return `<span style="${colors[v] || ''}">${v}</span>`;
                }
            }
        ]);
        
        // Render pagination controls
        if (pageSize !== 'all' && totalPages > 1) {
            this.renderRiskPagination(totalPages);
        } else {
            document.getElementById('risk-pagination').innerHTML = '';
        }
    },

    renderRiskPagination(totalPages) {
        const paginationContainer = document.getElementById('risk-pagination');
        const currentPage = this.riskPaginationState.currentPage;
        
        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <button class="btn btn-sm ${currentPage === 1 ? 'btn-secondary' : 'btn-primary'}" 
                    onclick="window.RiskProfilingPage.goToRiskPage(${currentPage - 1})" 
                    ${currentPage === 1 ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i> Previous
            </button>
        `;
        
        // Page numbers
        const maxPagesToShow = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
        
        if (endPage - startPage < maxPagesToShow - 1) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }
        
        if (startPage > 1) {
            paginationHTML += `<button class="btn btn-sm btn-outline-primary" onclick="window.RiskProfilingPage.goToRiskPage(1)">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span style="padding: 0 8px;">...</span>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="btn btn-sm ${i === currentPage ? 'btn-primary' : 'btn-outline-primary'}" 
                        onclick="window.RiskProfilingPage.goToRiskPage(${i})">
                    ${i}
                </button>
            `;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span style="padding: 0 8px;">...</span>`;
            }
            paginationHTML += `<button class="btn btn-sm btn-outline-primary" onclick="window.RiskProfilingPage.goToRiskPage(${totalPages})">${totalPages}</button>`;
        }
        
        // Next button
        paginationHTML += `
            <button class="btn btn-sm ${currentPage === totalPages ? 'btn-secondary' : 'btn-primary'}" 
                    onclick="window.RiskProfilingPage.goToRiskPage(${currentPage + 1})" 
                    ${currentPage === totalPages ? 'disabled' : ''}>
                Next <i class="fas fa-chevron-right"></i>
            </button>
        `;
        
        paginationContainer.innerHTML = paginationHTML;
    },

    goToRiskPage(page) {
        const totalPages = Math.ceil(
            (this.riskPaginationState.filter === 'all' 
                ? this.riskPaginationState.allData.length 
                : this.riskPaginationState.allData.filter(r => r.risk_level === this.riskPaginationState.filter).length
            ) / this.riskPaginationState.pageSize
        );
        
        if (page < 1 || page > totalPages) return;
        
        this.riskPaginationState.currentPage = page;
        this.displayRiskTable();
        
        // Scroll to table
        document.getElementById('risk-table').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },

    async detectAnomalies() {
        try {
            window.app.showLoading();
            const supplierIds = this.currentRiskData.results ? 
                this.currentRiskData.results.map(r => r.supplier_id) : null;
            
            const result = await window.api.detectAnomalies(supplierIds);
            if (result.error) {
                window.app.showError(result.error);
                return;
            }

            const anomalies = result.results || [];
            this.currentRiskData.anomalyResults = anomalies;
            const detected = anomalies.filter(a => a.is_anomaly);
            
            document.getElementById('anomalies-results').style.display = 'block';
            
            if (detected.length > 0) {
                window.app.showError(`⚠️ ${detected.length} anomalies detected!`);
                utils.createTable(detected, 'anomalies-table', [
                    { key: 'supplier_id', label: 'Supplier ID' },
                    { key: 'anomaly_score', label: 'Anomaly Score', format: (v) => utils.formatNumber(v, 3) },
                    { key: 'anomaly_reason', label: 'Anomaly Reason' },
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

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages-risk');
        if (!messagesContainer) return null;

        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator-risk';
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
        const typingIndicator = document.getElementById('typing-indicator-risk');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    },

    async getRiskRationale() {
        try {
            if (!this.currentRiskData.csvData || (!this.currentRiskData.riskResults && !this.currentRiskData.anomalyResults)) {
                window.app.showError('Please upload a CSV file and analyze risks/anomalies first.');
                return;
            }

            this.addChatMessage('user', 'Please explain the risk analysis and anomaly detection results.');
            const typingIndicator = this.showTypingIndicator();
            
            const result = await window.api.getRiskAnalysisRationale({
                csv_data: this.currentRiskData.csvData,
                risk_results: this.currentRiskData.riskResults || [],
                anomaly_results: this.currentRiskData.anomalyResults || [],
                file_name: this.currentRiskData.fileName
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
                return;
            }

            this.addChatMessage('bot', result.rationale || result.response || 'Risk analysis rationale generated successfully.');
            window.app.showSuccess('Risk analysis rationale generated!');
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[RiskProfiling] Error getting risk rationale:', error);
            let errorMessage = error.message || 'Failed to get risk rationale';
            
            if (error.status === 429 || errorMessage.includes('quota') || errorMessage.includes('429')) {
                const retryAfter = error.detail?.retry_after || error.detail?.detail?.retry_after || 60;
                errorMessage = `API Quota Exceeded. Please wait ${retryAfter} seconds before trying again.`;
                this.addChatMessage('bot', errorMessage, true);
                window.app.showError(`Quota exceeded. Please wait ${retryAfter} seconds.`);
            } else {
                this.addChatMessage('bot', `Error: ${errorMessage}`, true);
                window.app.showError('Failed to get risk rationale: ' + errorMessage);
            }
        }
    },

    async sendChatMessage() {
        const input = document.getElementById('chatbot-input-risk');
        const message = input.value.trim();
        
        if (!message) return;

        if (!this.currentRiskData.csvData) {
            window.app.showError('Please upload a CSV file first.');
            return;
        }

        this.addChatMessage('user', message);
        input.value = '';
        const typingIndicator = this.showTypingIndicator();

        try {
            const result = await window.api.chatAboutRisks({
                message: message,
                csv_data: this.currentRiskData.csvData,
                risk_results: this.currentRiskData.riskResults || [],
                anomaly_results: this.currentRiskData.anomalyResults || []
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
            } else {
                this.addChatMessage('bot', result.response || result.answer || 'Response generated.');
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[RiskProfiling] Chat error:', error);
            let errorMessage = error.message || 'Failed to get response';
            
            if (error.status === 429 || errorMessage.includes('quota') || errorMessage.includes('429')) {
                const retryAfter = error.detail?.retry_after || error.detail?.detail?.retry_after || 60;
                errorMessage = `API Quota Exceeded. Please wait ${retryAfter} seconds before trying again.`;
                this.addChatMessage('bot', errorMessage, true);
            } else {
                this.addChatMessage('bot', `Error: ${errorMessage}`, true);
            }
        }
    },

    addChatMessage(sender, message, isError = false) {
        const messagesContainer = document.getElementById('chatbot-messages-risk');
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
        const messagesContainer = document.getElementById('chatbot-messages-risk');
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                        <i class="fas fa-robot"></i> AI Assistant
                    </div>
                    <div style="color: var(--corp-gray-700);">
                        Hello! I'm your AI Risk Analysis Assistant powered by Gemini 2.5 Flash. 
                        Upload a CSV file, analyze risks and anomalies to see detailed explanations.
                    </div>
                </div>
            `;
        }
    }
};
