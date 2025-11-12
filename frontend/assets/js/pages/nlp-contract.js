// NLP Contract Analyzer Page JavaScript
window.NLPContractPage = {
    // Store current contract data for chatbot
    currentContractData: {
        contractText: null,
        analysisResults: null,
        fileName: null,
        inputMethod: null
    },

    async init() {
        const container = document.getElementById('page-nlp-contract');
        container.innerHTML = this.getHTML();
        this.setupEventListeners();
    },

    getHTML() {
        return `
            <div class="card mb-4" data-aos="fade-up">
                <div class="card-header-custom">
                    <h1><i class="fas fa-file-contract"></i> NLP Contract Analyzer</h1>
                </div>
                <div class="card-body">
                    <p class="lead">Analyze supplier contracts using Natural Language Processing and AI-powered insights</p>
                </div>
            </div>

            <div class="card mb-4" data-aos="fade-up" data-aos-delay="100">
                <div class="card-header-custom">
                    <h3><i class="fas fa-upload"></i> Upload or Enter Contract</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <div class="form-group mb-3">
                        <label class="form-label-custom">
                            <i class="fas fa-list"></i> Input Method
                        </label>
                        <select id="input-method" class="form-control-custom">
                            <option value="upload">Upload File</option>
                            <option value="text">Enter Text</option>
                            <option value="library">Select from Library</option>
                        </select>
                    </div>
                    <div id="upload-section">
                        <div class="form-group mb-3">
                            <label class="form-label-custom">
                                <i class="fas fa-file"></i> Upload Contract File
                            </label>
                            <input type="file" id="contract-file" class="form-control-custom" accept=".txt,.pdf,.doc,.docx">
                            <small class="form-text text-muted">Supported formats: TXT, PDF, DOC, DOCX</small>
                        </div>
                    </div>
                    <div id="text-section" style="display: none;">
                        <div class="form-group mb-3">
                            <label class="form-label-custom">
                                <i class="fas fa-keyboard"></i> Enter Contract Text
                            </label>
                            <textarea id="contract-text" class="form-control-custom" rows="10" placeholder="Paste contract text here..."></textarea>
                        </div>
                    </div>
                    <div id="library-section" style="display: none;">
                        <div class="form-group mb-3">
                            <label class="form-label-custom">
                                <i class="fas fa-book"></i> Select Contract
                            </label>
                            <select id="contract-select" class="form-control-custom"></select>
                        </div>
                    </div>
                    <button id="analyze-btn" class="btn-primary-custom">
                        <i class="fas fa-search"></i> Analyze Contract
                    </button>
                </div>
            </div>

            <div id="analysis-results" style="display: none;">
                <div id="analysis-loading" style="display: none; text-align: center; padding: 3rem;">
                    <div style="display: inline-block;">
                        <div style="display: flex; align-items: center; gap: 1rem; color: var(--corp-primary);">
                            <div style="width: 2rem; height: 2rem; border: 3px solid var(--corp-gray-200); border-top-color: var(--corp-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                            <div style="font-size: 1.1rem; font-weight: 500;">
                                Analyzing contract... Please wait
                            </div>
                        </div>
                    </div>
                </div>
                <div id="analysis-content" style="display: none;">
                <div class="card mb-4" data-aos="fade-up" data-aos-delay="200">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-chart-bar"></i> Analysis Summary</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <div class="row">
                            <div class="col-md-3 mb-3">
                                <div class="stat-card">
                                    <div class="stat-icon" style="background: var(--corp-primary);">
                                        <i class="fas fa-tags"></i>
                                    </div>
                                    <div class="stat-value" id="entity-count" style="font-size: 2rem; font-weight: 700;">0</div>
                                    <div class="stat-label">Entities Found</div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="stat-card">
                                    <div class="stat-icon" style="background: var(--corp-success);">
                                        <i class="fas fa-file-alt"></i>
                                    </div>
                                    <div class="stat-value" id="clause-count" style="font-size: 2rem; font-weight: 700;">0</div>
                                    <div class="stat-label">Key Clauses</div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="stat-card">
                                    <div class="stat-icon" style="background: var(--corp-warning);">
                                        <i class="fas fa-smile"></i>
                                    </div>
                                    <div class="stat-value" id="sentiment-value" style="font-size: 2rem; font-weight: 700;">N/A</div>
                                    <div class="stat-label">Sentiment</div>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="stat-card">
                                    <div class="stat-icon" style="background: var(--corp-danger);">
                                        <i class="fas fa-exclamation-triangle"></i>
                                    </div>
                                    <div class="stat-value" id="risk-level-value" style="font-size: 2rem; font-weight: 700;">N/A</div>
                                    <div class="stat-label">Risk Level</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card mb-4" data-aos="fade-up" data-aos-delay="300">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-tags"></i> Named Entities</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <div id="entities-display" class="row"></div>
                    </div>
                </div>

                <div class="card mb-4" data-aos="fade-up" data-aos-delay="400">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-file-alt"></i> Key Clauses</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <div id="clauses-display"></div>
                    </div>
                </div>

                <div class="card mb-4" data-aos="fade-up" data-aos-delay="500">
                    <div class="card-header-custom">
                        <h3><i class="fas fa-exclamation-triangle"></i> Risk Terms</h3>
                    </div>
                    <div class="card-body" style="padding: 2rem;">
                        <div id="risk-terms-display" class="row"></div>
                    </div>
                </div>
            </div>

            <!-- AI Chatbot for Contract Analysis -->
            <div class="card mb-4" data-aos="fade-up" data-aos-delay="600">
                <div class="card-header-custom">
                    <h3><i class="fas fa-robot"></i> AI Contract Analysis Assistant</h3>
                </div>
                <div class="card-body" style="padding: 2rem;">
                    <p class="mb-3" style="color: var(--corp-gray-600);">
                        Get AI-powered explanations for contract analysis results. The assistant analyzes your uploaded/loaded contract, 
                        provides a brief overview of what the document is about, and explains the analysis results in detail.
                    </p>
                    <div id="chatbot-container-contract" style="border: 1px solid var(--corp-gray-200); border-radius: 8px; background: white; min-height: 400px; max-height: 600px; display: flex; flex-direction: column;">
                        <div id="chatbot-messages-contract" style="flex: 1; padding: 1.5rem; overflow-y: auto; max-height: 450px;">
                            <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                                    <i class="fas fa-robot"></i> AI Assistant
                                </div>
                                <div style="color: var(--corp-gray-700);">
                                    Hello! I'm your AI Contract Analysis Assistant powered by Gemini 2.5 Flash. 
                                    Upload or load a contract file, analyze it, and I'll provide detailed explanations about the document and its analysis results.
                                </div>
                            </div>
                        </div>
                        <div id="chatbot-input-container-contract" style="padding: 1rem; border-top: 1px solid var(--corp-gray-200); display: flex; gap: 0.5rem;">
                            <input type="text" id="chatbot-input-contract" class="form-control-custom" 
                                   placeholder="Ask about the contract analysis..." 
                                   style="flex: 1;">
                            <button id="chatbot-send-btn-contract" class="btn-primary-custom" style="white-space: nowrap;">
                                <i class="fas fa-paper-plane"></i> Send
                            </button>
                        </div>
                    </div>
                    <div class="mt-3" style="text-align: center;">
                        <button id="get-contract-rationale-btn" class="btn-primary-custom">
                            <i class="fas fa-brain"></i> Get Contract Analysis & Document Overview
                        </button>
                        <button id="clear-chat-contract-btn" class="btn-secondary-custom ml-2">
                            <i class="fas fa-trash"></i> Clear Chat
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.getElementById('input-method').addEventListener('change', (e) => this.handleInputMethodChange(e.target.value));
        document.getElementById('analyze-btn').addEventListener('click', () => this.analyzeContract());
        
        // Chatbot handlers
        document.getElementById('get-contract-rationale-btn').addEventListener('click', () => this.getContractRationale());
        document.getElementById('chatbot-send-btn-contract').addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chatbot-input-contract').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
        document.getElementById('clear-chat-contract-btn').addEventListener('click', () => this.clearChat());
        
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

    showAnalysisLoading() {
        const analysisResults = document.getElementById('analysis-results');
        const analysisLoading = document.getElementById('analysis-loading');
        const analysisContent = document.getElementById('analysis-content');
        
        if (analysisResults && analysisLoading && analysisContent) {
            analysisResults.style.display = 'block';
            analysisLoading.style.display = 'block';
            analysisContent.style.display = 'none';
        }
    },

    hideAnalysisLoading() {
        const analysisLoading = document.getElementById('analysis-loading');
        const analysisContent = document.getElementById('analysis-content');
        
        if (analysisLoading && analysisContent) {
            analysisLoading.style.display = 'none';
            analysisContent.style.display = 'block';
        }
    },

    async analyzeContract() {
        try {
            this.showAnalysisLoading();
            const method = document.getElementById('input-method').value;
            let result;
            let contractText = '';

            if (method === 'upload') {
                const file = document.getElementById('contract-file').files[0];
                if (!file) {
                    window.app.showError('Please select a file');
                    this.hideAnalysisLoading();
                    return;
                }
                // Read file content
                contractText = await file.text();
                this.currentContractData.fileName = file.name;
                this.currentContractData.inputMethod = 'upload';
                result = await window.api.uploadContract(file);
            } else if (method === 'text') {
                contractText = document.getElementById('contract-text').value;
                if (!contractText.trim()) {
                    window.app.showError('Please enter contract text');
                    this.hideAnalysisLoading();
                    return;
                }
                this.currentContractData.fileName = 'Entered Text';
                this.currentContractData.inputMethod = 'text';
                result = await window.api.analyzeContract(contractText, null);
            } else {
                const contractId = document.getElementById('contract-select').value;
                if (!contractId) {
                    window.app.showError('Please select a contract');
                    this.hideAnalysisLoading();
                    return;
                }
                this.currentContractData.fileName = contractId;
                this.currentContractData.inputMethod = 'library';
                result = await window.api.analyzeContract(null, contractId);
                // Try to get contract text from result if available
                if (result.contract_text) {
                    contractText = result.contract_text;
                } else {
                    // Try to load contract text from library
                    try {
                        const contracts = await window.api.listContracts();
                        const contract = contracts.contracts?.find(c => c.contract_id === contractId);
                        if (contract && contract.content) {
                            contractText = contract.content;
                        }
                    } catch (e) {
                        console.warn('Could not load contract text from library:', e);
                    }
                }
            }

            if (result.error) {
                window.app.showError(result.error);
                this.hideAnalysisLoading();
                return;
            }

            // Store contract data for chatbot - ensure we have the text
            // If contractText is empty, try to get it from the analysis result
            if (!contractText && result.analysis) {
                // Try to extract from analysis if available
                console.warn('[NLPContract] Contract text not available, using analysis data only');
            }
            
            this.currentContractData.contractText = contractText || '';
            this.currentContractData.analysisResults = result.analysis || result;
            
            // Debug: Log stored data
            console.log('[NLPContract] Contract data stored:', {
                hasText: !!this.currentContractData.contractText,
                textLength: this.currentContractData.contractText?.length || 0,
                hasResults: !!this.currentContractData.analysisResults,
                fileName: this.currentContractData.fileName,
                analysisKeys: Object.keys(this.currentContractData.analysisResults || {})
            });

            this.hideAnalysisLoading();
            this.displayAnalysis(result.analysis || result);
            window.app.showSuccess('Contract analyzed successfully!');
        } catch (error) {
            this.hideAnalysisLoading();
            window.app.showError('Failed to analyze contract: ' + error.message);
            console.error('[NLPContract] Analysis error:', error);
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
        
        // Check if risk terms exist
        const hasRiskTerms = riskTerms && Object.keys(riskTerms).length > 0;
        const totalRiskTerms = hasRiskTerms ? 
            (riskTerms.high_risk?.length || 0) + 
            (riskTerms.medium_risk?.length || 0) + 
            (riskTerms.low_risk?.length || 0) : 0;
        
        if (totalRiskTerms === 0) {
            riskDisplay.innerHTML = `
                <div class="col-12">
                    <div class="card" style="padding: 2rem; text-align: center; background: var(--corp-gray-50);">
                        <i class="fas fa-info-circle" style="font-size: 3rem; color: var(--corp-gray-400); margin-bottom: 1rem;"></i>
                        <h5 style="color: var(--corp-gray-600);">No Risk Terms Detected</h5>
                        <p style="color: var(--corp-gray-500);">The contract analysis did not identify any specific risk terms. This may indicate a standard or low-risk contract.</p>
                    </div>
                </div>
            `;
        } else {
            ['high_risk', 'medium_risk', 'low_risk'].forEach(level => {
                const terms = riskTerms[level] || [];
                if (terms.length > 0) {
                    const col = document.createElement('div');
                    col.className = 'col-md-4 mb-3';
                    const colorClass = level === 'high_risk' ? 'danger' : level === 'medium_risk' ? 'warning' : 'success';
                    const bgColor = level === 'high_risk' ? '#fee' : level === 'medium_risk' ? '#fff4e6' : '#e6f7e6';
                    const borderColor = level === 'high_risk' ? '#fcc' : level === 'medium_risk' ? '#ffd699' : '#b3e6b3';
                    
                    col.innerHTML = `
                        <div class="card" style="border-left: 4px solid ${borderColor}; background: ${bgColor};">
                            <div class="card-body">
                                <h5 style="color: var(--corp-${colorClass}); margin-bottom: 1rem;">
                                    <i class="fas fa-${level === 'high_risk' ? 'exclamation-triangle' : level === 'medium_risk' ? 'exclamation-circle' : 'check-circle'}"></i>
                                    ${level.replace(/_/g, ' ').toUpperCase()}
                                </h5>
                                <p style="font-weight: 600; margin-bottom: 0.5rem;">${terms.length} term${terms.length > 1 ? 's' : ''} found</p>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    ${terms.slice(0, 5).map(term => {
                                        const termText = typeof term === 'object' ? (term.term || term.context || JSON.stringify(term)) : term;
                                        return `<li style="margin-bottom: 0.5rem;">${termText}</li>`;
                                    }).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                    riskDisplay.appendChild(col);
                }
            });
        }
    },

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages-contract');
        if (!messagesContainer) return null;

        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator-contract';
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
        const typingIndicator = document.getElementById('typing-indicator-contract');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    },

    async getContractRationale() {
        try {
            // More lenient check - allow if we have analysis results even without full text
            if (!this.currentContractData.analysisResults) {
                window.app.showError('Please analyze a contract first before requesting rationale.');
                return;
            }

            // If no contract text, use a placeholder or extract from analysis
            let contractText = this.currentContractData.contractText;
            if (!contractText && this.currentContractData.analysisResults) {
                // Try to reconstruct a summary from analysis results
                const summary = this.currentContractData.analysisResults.summary || {};
                contractText = `Contract Analysis Summary: ${summary.total_entities || 0} entities, ${summary.key_clauses_found || 0} clauses, ${summary.overall_sentiment || 'N/A'} sentiment, ${summary.risk_level || 'N/A'} risk level.`;
            }

            this.addChatMessage('user', 'Please provide a brief overview of what this document is about and explain the analysis results.');
            const typingIndicator = this.showTypingIndicator();
            
            const result = await window.api.getContractAnalysisRationale({
                contract_text: contractText || 'Contract document analyzed',
                analysis_results: this.currentContractData.analysisResults,
                file_name: this.currentContractData.fileName,
                input_method: this.currentContractData.inputMethod
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
                return;
            }

            this.addChatMessage('bot', result.rationale || result.response || 'Contract analysis rationale generated successfully.');
            window.app.showSuccess('Contract analysis rationale generated!');
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[NLPContract] Error getting contract rationale:', error);
            let errorMessage = error.message || 'Failed to get contract rationale';
            
            if (error.status === 429 || errorMessage.includes('quota') || errorMessage.includes('429')) {
                const retryAfter = error.detail?.retry_after || error.detail?.detail?.retry_after || 60;
                errorMessage = `API Quota Exceeded. Please wait ${retryAfter} seconds before trying again.`;
                this.addChatMessage('bot', errorMessage, true);
                window.app.showError(`Quota exceeded. Please wait ${retryAfter} seconds.`);
            } else {
                this.addChatMessage('bot', `Error: ${errorMessage}`, true);
                window.app.showError('Failed to get contract rationale: ' + errorMessage);
            }
        }
    },

    async sendChatMessage() {
        const input = document.getElementById('chatbot-input-contract');
        const message = input.value.trim();
        
        if (!message) return;

        // Debug: Check contract data
        console.log('[NLPContract] Chat check:', {
            hasText: !!this.currentContractData.contractText,
            textLength: this.currentContractData.contractText?.length || 0,
            hasResults: !!this.currentContractData.analysisResults,
            fileName: this.currentContractData.fileName
        });

        // More lenient check - allow if we have analysis results even without full text
        if (!this.currentContractData.analysisResults) {
            window.app.showError('Please analyze a contract first.');
            return;
        }

        // If no contract text, use a placeholder or extract from analysis
        let contractText = this.currentContractData.contractText;
        if (!contractText && this.currentContractData.analysisResults) {
            // Try to reconstruct a summary from analysis results
            const summary = this.currentContractData.analysisResults.summary || {};
            contractText = `Contract Analysis Summary: ${summary.total_entities || 0} entities, ${summary.key_clauses_found || 0} clauses, ${summary.overall_sentiment || 'N/A'} sentiment, ${summary.risk_level || 'N/A'} risk level.`;
        }

        this.addChatMessage('user', message);
        input.value = '';
        const typingIndicator = this.showTypingIndicator();

        try {
            const result = await window.api.chatAboutContract({
                message: message,
                contract_text: contractText || 'Contract document analyzed',
                analysis_results: this.currentContractData.analysisResults
            });

            this.hideTypingIndicator();

            if (result.error) {
                this.addChatMessage('bot', `Error: ${result.error}`, true);
            } else {
                this.addChatMessage('bot', result.response || result.answer || 'Response generated.');
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('[NLPContract] Chat error:', error);
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
        const messagesContainer = document.getElementById('chatbot-messages-contract');
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
        const messagesContainer = document.getElementById('chatbot-messages-contract');
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="chat-message bot-message" style="background: var(--corp-gray-50); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: var(--corp-primary); margin-bottom: 0.5rem;">
                        <i class="fas fa-robot"></i> AI Assistant
                    </div>
                    <div style="color: var(--corp-gray-700);">
                        Hello! I'm your AI Contract Analysis Assistant powered by Gemini 2.5 Flash. 
                        Upload or load a contract file, analyze it, and I'll provide detailed explanations about the document and its analysis results.
                    </div>
                </div>
            `;
        }
    }
};

