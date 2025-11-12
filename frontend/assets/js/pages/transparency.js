// Transparency & Resilience Page JavaScript
window.TransparencyPage = {
    // Store current transparency data for chatbot
    currentTransparencyData: {
        csvData: null,
        modelType: null,
        results: null,
        fileName: null
    },

    async init() {
        const container = document.getElementById('page-transparency');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
        this.checkPreviousCSV();
    },

    getHTML() {
        return `
            <div class="card mb-4" data-aos="fade-up">
                <div class="card-header-custom">
                    <h1><i class="fas fa-globe"></i> Transparency & Resilience</h1>
                </div>
                <div class="card-body">
                    <p class="lead">Enhance transparency and resilience in global supply chains with AI-powered insights</p>
                </div>
            </div>

            <!-- CSV Upload Section -->
            <div class="card mb-4" data-aos="fade-up" data-aos-delay="100" style="border: 2px solid var(--corp-primary);">
                <div class="card-header-custom" style="background: linear-gradient(135deg, var(--corp-primary) 0%, var(--corp-primary-dark) 100%); color: white;">
                    <h3><i class="fas fa-upload"></i> Upload CSV/EXCEL File for Transparency Analysis</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div id="previous-csv-notice" style="display: none; margin-bottom: 1rem; padding: 1rem; background: var(--corp-gray-50); border-left: 4px solid var(--corp-primary); border-radius: 4px;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <i class="fas fa-info-circle" style="color: var(--corp-primary); font-size: 1.5rem;"></i>
                            <div style="flex: 1;">
                                <strong>Previous CSV Detected</strong>
                                <p style="margin: 0.5rem 0 0 0; color: var(--corp-gray-600);">
                                    A CSV file was previously uploaded in the Supplier Evaluation & Scoring section. 
                                    You can use that file or upload a new one.
                                </p>
                            </div>
                            <button id="use-previous-csv-btn" class="btn-primary-custom" style="white-space: nowrap;">
                                <i class="fas fa-check"></i> Use Previous CSV
                            </button>
                        </div>
                    </div>
                    <div id="upload-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                        <div style="display: inline-block;">
                            <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                                <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                                <div style="font-size: 1rem; font-weight: 500;">
                                    Uploading and analyzing file... Please wait
                                </div>
                            </div>
                        </div>
                    </div>
                    <div id="upload-content">
                    <div class="form-group mb-3">
                        <label class="form-label-custom">
                            <i class="fas fa-file-csv"></i> Upload CSV/Excel File
                        </label>
                        <input type="file" id="transparency-file-input" class="form-control-custom" accept=".csv,.xlsx,.xls">
                        <small class="form-text text-muted">Supported formats: CSV, XLSX, XLS</small>
                    </div>
                    <div class="form-group mb-3">
                        <label class="form-label-custom">
                            <i class="fas fa-brain"></i> Select Model
                        </label>
                        <select id="transparency-model-select" class="form-control-custom">
                            <option value="xgboost">XGBoost</option>
                            <option value="random_forest">Random Forest</option>
                            <option value="gradient_boosting">Gradient Boosting</option>
                            <option value="svr">SVR</option>
                            <option value="mlp">MLP</option>
                            <option value="adaboost">AdaBoost</option>
                        </select>
                    </div>
                    <button id="upload-transparency-btn" class="btn-primary-custom">
                        <i class="fas fa-upload"></i> Upload & Analyze Transparency
                    </button>
                    </div>
                </div>
            </div>

            <div class="card mb-4" data-aos="fade-up" data-aos-delay="200">
                <div class="card-header-custom">
                    <h3><i class="fas fa-project-diagram"></i> Supplier Network Visualization</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div id="network-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                        <div style="display: inline-block;">
                            <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                                <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                                <div style="font-size: 1rem; font-weight: 500;">
                                    Loading supplier network... Please wait
                                </div>
                            </div>
                        </div>
                    </div>
                    <div id="network-content">
                    <button id="load-network-btn" class="btn-primary-custom mb-3">
                        <i class="fas fa-project-diagram"></i> View Supplier Network
                    </button>
                    <div id="network-stats" class="metrics-grid mb-3"></div>
                    <div id="network-chart" class="chart-container"></div>
                    </div>
                </div>
            </div>

            <div class="card mb-4" data-aos="fade-up" data-aos-delay="300">
                <div class="card-header-custom">
                    <h3><i class="fas fa-shield-alt"></i> Resilience Metrics</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div id="resilience-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                        <div style="display: inline-block;">
                            <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                                <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                                <div style="font-size: 1rem; font-weight: 500;">
                                    Calculating resilience metrics... Please wait
                                </div>
                            </div>
                        </div>
                    </div>
                    <div id="resilience-content">
                    <button id="load-resilience-btn" class="btn-primary-custom mb-3">
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
                    </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4" data-aos="fade-up" data-aos-delay="400">
                <div class="card-header-custom">
                    <h3><i class="fas fa-eye"></i> Transparency Scores</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div id="transparency-loading" style="display: none; text-align: center; padding: 2rem; margin-bottom: 1rem;">
                        <div style="display: inline-block;">
                            <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                                <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                                <div style="font-size: 1rem; font-weight: 500;">
                                    Loading transparency scores... Please wait
                                </div>
                            </div>
                        </div>
                    </div>
                    <div id="transparency-content">
                    <button id="load-transparency-btn" class="btn-primary-custom mb-3">
                        <i class="fas fa-eye"></i> View Transparency Scores
                    </button>
                    <div id="transparency-table" class="table-container"></div>
                    </div>
                </div>
            </div>

            <!-- AI Chatbot for Transparency Analysis -->
            <div class="card mb-4" data-aos="fade-up" data-aos-delay="500">
                <div class="card-header-custom">
                    <h3><i class="fas fa-robot"></i> AI Transparency Analysis Assistant</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <p class="mb-3" style="color: var(--corp-gray-600);">
                        Get AI-powered explanations for transparency and resilience analysis results. The assistant analyzes your uploaded CSV, 
                        provides insights about supplier rankings, transparency scores, and resilience metrics.
                    </p>
                    <div id="chatbot-container-transparency" style="border: 1px solid var(--corp-gray-200); border-radius: 8px; background: white; min-height: 400px; max-height: 600px; display: flex; flex-direction: column;">
                        <div id="chatbot-messages-transparency" style="flex: 1; padding: 1.5rem; overflow-y: auto; max-height: 450px;">
                            <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                                    <i class="fas fa-robot"></i> AI Assistant
                                </div>
                                <div style="color: var(--corp-gray-700);">
                                    Hello! I'm your AI Transparency Analysis Assistant powered by Gemini 2.5 Flash. 
                                    Upload a CSV file, analyze transparency and resilience metrics, and I'll provide detailed explanations about the results.
                                </div>
                            </div>
                        </div>
                        <div id="chatbot-input-container-transparency" style="padding: 1rem; border-top: 1px solid var(--corp-gray-200); display: flex; gap: 0.5rem;">
                            <input type="text" id="chatbot-input-transparency" class="form-control-custom" 
                                   placeholder="Ask about the transparency analysis..." 
                                   style="flex: 1;">
                            <button id="chatbot-send-btn-transparency" class="btn-primary-custom" style="white-space: nowrap;">
                                <i class="fas fa-paper-plane"></i> Send
                            </button>
                        </div>
                    </div>
                    <div class="mt-3" style="text-align: center;">
                        <button id="get-transparency-rationale-btn" class="btn-primary-custom">
                            <i class="fas fa-brain"></i> Get Transparency Analysis Rationale
                        </button>
                        <button id="clear-chat-transparency-btn" class="btn-secondary-custom ml-2">
                            <i class="fas fa-trash"></i> Clear Chat
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('load-network-btn').addEventListener('click', () => this.loadSupplierNetwork());
        document.getElementById('load-resilience-btn').addEventListener('click', () => this.loadResilienceMetrics());
        document.getElementById('load-transparency-btn').addEventListener('click', () => this.loadTransparencyScores());
        
        // CSV upload handlers
        document.getElementById('upload-transparency-btn').addEventListener('click', () => this.uploadAndAnalyzeTransparency());
        document.getElementById('transparency-file-input').addEventListener('change', (e) => this.handleFileChange(e));
        
        // Previous CSV handler
        document.getElementById('use-previous-csv-btn').addEventListener('click', () => this.usePreviousCSV());
        
        // Chatbot handlers
        document.getElementById('get-transparency-rationale-btn').addEventListener('click', () => this.getTransparencyRationale());
        document.getElementById('chatbot-send-btn-transparency').addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chatbot-input-transparency').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
        document.getElementById('clear-chat-transparency-btn').addEventListener('click', () => this.clearChat());
    },

    async loadSupplierNetwork() {
        try {
            this.showLoading('network');
            const result = await (window.api).getSupplierNetwork();
            if (result.error) {
                window.app.showError(result.error);
                this.hideLoading('network');
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

            this.hideLoading('network');
            window.app.showSuccess(`Loaded ${nodes.length} suppliers in network!`);
        } catch (error) {
            this.hideLoading('network');
            window.app.showError('Failed to load supplier network: ' + error.message);
        }
    },

    async loadResilienceMetrics() {
        try {
            this.showLoading('resilience');
            const result = await (window.api).getResilienceMetrics();
            if (result.error) {
                window.app.showError(result.error);
                this.hideLoading('resilience');
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

            this.hideLoading('resilience');
            window.app.showSuccess(`Calculated resilience for ${metrics.length} suppliers!`);
        } catch (error) {
            this.hideLoading('resilience');
            window.app.showError('Failed to load resilience metrics: ' + error.message);
        }
    },

    async loadTransparencyScores() {
        try {
            this.showLoading('transparency');
            const result = await (window.api).getTransparencyScores();
            if (result.error) {
                window.app.showError(result.error);
                this.hideLoading('transparency');
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

            this.hideLoading('transparency');
            window.app.showSuccess('Transparency scores loaded successfully!');
        } catch (error) {
            this.hideLoading('transparency');
            window.app.showError('Failed to load transparency scores: ' + error.message);
        }
    },

    showLoading(section) {
        const loadingEl = document.getElementById(`${section}-loading`);
        const contentEl = document.getElementById(`${section}-content`);
        
        if (loadingEl && contentEl) {
            loadingEl.style.display = 'block';
            contentEl.style.display = 'none';
        }
    },

    hideLoading(section) {
        const loadingEl = document.getElementById(`${section}-loading`);
        const contentEl = document.getElementById(`${section}-content`);
        
        if (loadingEl && contentEl) {
            loadingEl.style.display = 'none';
            contentEl.style.display = 'block';
        }
    },

    checkPreviousCSV() {
        // Check if Supplier Evaluation page has uploaded CSV data
        try {
            if (window.SupplierEvaluationPage && window.SupplierEvaluationPage.currentEvaluationData && 
                window.SupplierEvaluationPage.currentEvaluationData.csvData) {
                const notice = document.getElementById('previous-csv-notice');
                if (notice) {
                    notice.style.display = 'block';
                }
            }
        } catch (error) {
            console.warn('[Transparency] Could not check for previous CSV:', error);
        }
    },

    usePreviousCSV() {
        try {
            if (window.SupplierEvaluationPage && window.SupplierEvaluationPage.currentEvaluationData) {
                const data = window.SupplierEvaluationPage.currentEvaluationData;
                this.currentTransparencyData = {
                    csvData: data.csvData,
                    modelType: data.modelType || 'xgboost',
                    results: data.results || [],
                    fileName: data.fileName || 'Previous CSV'
                };
                
                // Update model select
                const modelSelect = document.getElementById('transparency-model-select');
                if (modelSelect && data.modelType) {
                    modelSelect.value = data.modelType;
                }
                
                // Hide notice
                document.getElementById('previous-csv-notice').style.display = 'none';
                
                window.app.showSuccess(`Using previous CSV: ${this.currentTransparencyData.fileName}`);
            } else {
                window.app.showError('No previous CSV data found. Please upload a CSV in Supplier Evaluation section first.');
            }
        } catch (error) {
            console.error('[Transparency] Error using previous CSV:', error);
            window.app.showError('Failed to use previous CSV: ' + error.message);
        }
    },

    handleFileChange(event) {
        const file = event.target.files[0];
        const uploadBtn = document.getElementById('upload-transparency-btn');
        
        if (file) {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = `<i class="fas fa-upload"></i> Upload & Analyze: ${file.name}`;
        } else {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = `<i class="fas fa-upload"></i> Upload & Analyze Transparency`;
        }
    },

    async uploadAndAnalyzeTransparency() {
        try {
            const fileInput = document.getElementById('transparency-file-input');
            const file = fileInput.files[0];
            const modelType = document.getElementById('transparency-model-select').value;
            
            if (!file) {
                window.app.showError('Please select a CSV or Excel file');
                return;
            }

            this.showLoading('upload');
            
            // Read file as text for chatbot
            const csvText = await file.text();
            
            // Upload and evaluate using supplier evaluation endpoint (same logic)
            const result = await window.api.uploadAndEvaluate(file, modelType);
            
            if (result.error) {
                window.app.showError(result.error);
                this.hideLoading('upload');
                return;
            }

            // Store data for chatbot
            this.currentTransparencyData = {
                csvData: csvText,
                modelType: modelType,
                results: result.results || [],
                fileName: file.name
            };
            
            // Hide previous CSV notice
            document.getElementById('previous-csv-notice').style.display = 'none';
            
            this.hideLoading('upload');
            window.app.showSuccess(`Successfully analyzed ${result.total_suppliers || result.results?.length || 0} suppliers from uploaded file!`);
            
        } catch (error) {
            this.hideLoading('upload');
            console.error('[Transparency] Error uploading and analyzing:', error);
            window.app.showError('Failed to upload and analyze file: ' + error.message);
        }
    },

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages-transparency');
        if (!messagesContainer) return null;

        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator-transparency';
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
        const typingIndicator = document.getElementById('typing-indicator-transparency');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    },

    async getTransparencyRationale() {
        try {
            if (!this.currentTransparencyData.results || !this.currentTransparencyData.modelType) {
                window.app.showError('Please upload a CSV file and analyze transparency first before requesting rationale.');
                return;
            }

            this.addChatMessage('user', 'Please explain the transparency and resilience analysis results.');
            const typingIndicator = this.showTypingIndicator();
            
            const result = await window.api.getRankingRationale({
                csv_data: this.currentTransparencyData.csvData,
                model_type: this.currentTransparencyData.modelType,
                results: this.currentTransparencyData.results,
                file_name: this.currentTransparencyData.fileName
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
                return;
            }

            this.addChatMessage('bot', result.rationale || result.response || 'Transparency analysis rationale generated successfully.');
            window.app.showSuccess('Transparency analysis rationale generated!');
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[Transparency] Error getting transparency rationale:', error);
            let errorMessage = error.message || 'Failed to get transparency rationale';
            
            if (error.status === 429 || errorMessage.includes('quota') || errorMessage.includes('429')) {
                const retryAfter = error.detail?.retry_after || error.detail?.detail?.retry_after || 60;
                errorMessage = `API Quota Exceeded. Please wait ${retryAfter} seconds before trying again.`;
                this.addChatMessage('bot', errorMessage, true);
                window.app.showError(`Quota exceeded. Please wait ${retryAfter} seconds.`);
            } else {
                this.addChatMessage('bot', `Error: ${errorMessage}`, true);
                window.app.showError('Failed to get transparency rationale: ' + errorMessage);
            }
        }
    },

    async sendChatMessage() {
        const input = document.getElementById('chatbot-input-transparency');
        const message = input.value.trim();
        
        if (!message) return;

        if (!this.currentTransparencyData.results) {
            window.app.showError('Please upload a CSV file and analyze transparency first.');
            return;
        }

        this.addChatMessage('user', message);
        input.value = '';
        const typingIndicator = this.showTypingIndicator();

        try {
            const result = await window.api.chatAboutRankings({
                message: message,
                csv_data: this.currentTransparencyData.csvData,
                model_type: this.currentTransparencyData.modelType,
                results: this.currentTransparencyData.results
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
            } else {
                this.addChatMessage('bot', result.response || result.answer || 'Response generated.');
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[Transparency] Chat error:', error);
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
        const messagesContainer = document.getElementById('chatbot-messages-transparency');
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
        const messagesContainer = document.getElementById('chatbot-messages-transparency');
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                        <i class="fas fa-robot"></i> AI Assistant
                    </div>
                    <div style="color: var(--corp-gray-700);">
                        Hello! I'm your AI Transparency Analysis Assistant powered by Gemini 2.5 Flash. 
                        Upload a CSV file, analyze transparency and resilience metrics, and I'll provide detailed explanations about the results.
                    </div>
                </div>
            `;
        }
    }
};

