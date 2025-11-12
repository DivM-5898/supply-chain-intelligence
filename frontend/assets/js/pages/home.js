// Landing Page JavaScript
window.HomePage = {
    async init() {
        console.log('HomePage.init() called');
        const container = document.getElementById('page-home');
        if (!container) {
            console.error('Page container not found');
            return;
        }
        
        try {
            // Set loading state
            container.innerHTML = '<div style="text-align: center; padding: 50px;"><i class="fas fa-spinner fa-spin fa-3x"></i><p>Loading landing page...</p></div>';
            
            // Small delay to ensure DOM is ready
            await new Promise(resolve => setTimeout(resolve, 50));
            
            // Get HTML content
            let html;
            try {
                html = this.getHTML();
            } catch (error) {
                console.error('Error in getHTML():', error);
                html = null;
            }
            
            if (!html || html.trim() === '') {
                console.error('getHTML() returned empty content');
                container.innerHTML = '<div class="alert alert-danger">Failed to load landing page content</div>';
                return;
            }
            
            // Render HTML
            container.innerHTML = html;
            console.log('Landing page HTML rendered, length:', html.length);
            
            // Wait for DOM to update
            setTimeout(() => {
                try {
                    if (typeof this.setupAnimations === 'function') {
                        this.setupAnimations();
                    }
                    if (typeof this.loadStats === 'function') {
                        this.loadStats();
                    }
                    if (typeof this.setupWorkflow === 'function') {
                        this.setupWorkflow();
                    }
                    if (typeof this.setupScrollReveal === 'function') {
                        this.setupScrollReveal();
                    }
                    console.log('Landing page initialized successfully');
                    
                    // Hide loading overlay if it exists
                    const loadingOverlay = document.getElementById('loadingOverlay');
                    if (loadingOverlay) {
                        loadingOverlay.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Error setting up landing page features:', error);
                    // Don't fail completely, page content is already rendered
                }
            }, 100);
        } catch (error) {
            console.error('Error initializing landing page:', error);
            container.innerHTML = `<div class="alert alert-danger">Error loading landing page: ${error.message}<br><small>${error.stack}</small></div>`;
        }
    },

    getHTML() {
        return `
            <!-- Hero Section -->
            <section class="landing-hero">
                <div class="hero-content">
                    <h1 class="hero-title">🚀 AI Supplier Selection & Risk Management</h1>
                    <p class="hero-subtitle">Transform Complex Supplier Analytics into Intelligent Decisions</p>
                    <p class="hero-description">
                        A comprehensive AI-driven platform that empowers executives to make smarter supplier decisions 
                        through advanced machine learning, natural language processing, and real-time risk analysis. 
                        Unify all seven analytical capabilities into one intuitive, data-driven decision cockpit.
                    </p>
                    <div class="cta-buttons">
                        <a href="#" class="btn-hero btn-hero-primary" onclick="window.app.navigateToPage('supplier-evaluation'); return false;">
                            <i class="fas fa-rocket"></i> Get Started
                        </a>
                        <a href="#" class="btn-hero" onclick="window.app.navigateToPage('supplier-evaluation'); return false;">
                            <i class="fas fa-play-circle"></i> Watch Demo
                        </a>
                    </div>
                </div>
            </section>

            <!-- Stats Section -->
            <section class="stats-section" data-aos="fade-up" data-aos-duration="800">
                <div class="stats-grid">
                    <div class="stat-card" data-aos="zoom-in" data-aos-delay="100">
                        <div class="stat-value" id="stat-time">95%</div>
                        <div class="stat-label">Time Savings</div>
                    </div>
                    <div class="stat-card" data-aos="zoom-in" data-aos-delay="200">
                        <div class="stat-value" id="stat-risk">30-40%</div>
                        <div class="stat-label">Risk Reduction</div>
                    </div>
                    <div class="stat-card" data-aos="zoom-in" data-aos-delay="300">
                        <div class="stat-value" id="stat-cost">15-20%</div>
                        <div class="stat-label">Cost Optimization</div>
                    </div>
                    <div class="stat-card" data-aos="zoom-in" data-aos-delay="400">
                        <div class="stat-value" id="stat-models">7+</div>
                        <div class="stat-label">ML Models</div>
                    </div>
                </div>
            </section>

            <!-- Interactive Workflow Visualization Section -->
            <section class="workflow-section" data-aos="fade-up">
                <div class="container">
                    <h2 class="text-center mb-2" data-aos="fade-up" style="font-size: 2.5rem; font-weight: 700; color: var(--corp-gray-900);">
                        AI-Powered Supplier Selection Workflow
                    </h2>
                    <p class="text-center mb-5" data-aos="fade-up" data-aos-delay="100" style="font-size: 1.2rem; color: var(--corp-gray-600); max-width: 700px; margin: 0 auto 3rem;">
                        Follow the complete journey from data ingestion to intelligent decision-making
                    </p>
                    
                    <div class="workflow-container" id="workflow-container">
                        <!-- Workflow Steps -->
                        <div class="workflow-step" data-step="1" data-aos="fade-right" data-aos-delay="100">
                            <div class="workflow-step-icon">
                                <i class="fas fa-database"></i>
                                <div class="workflow-pulse"></div>
                                <div class="workflow-step-number">1</div>
                            </div>
                            <div class="workflow-step-content">
                                <h3>Data Collection</h3>
                                <p>Synthetic supplier datasets with comprehensive metrics</p>
                                <div class="workflow-badge">100+ Suppliers</div>
                                <div class="workflow-details" style="display: none;">
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Comprehensive supplier profiles</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Historical performance data</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Real-time metrics tracking</span>
                                    </div>
                                </div>
                                <button class="workflow-learn-more">
                                    <i class="fas fa-info-circle"></i> Learn More
                                </button>
                            </div>
                            <div class="workflow-connector">
                                <div class="workflow-line"></div>
                                <div class="workflow-arrow"><i class="fas fa-arrow-right"></i></div>
                            </div>
                        </div>

                        <div class="workflow-step" data-step="2" data-aos="fade-right" data-aos-delay="200">
                            <div class="workflow-step-icon">
                                <i class="fas fa-brain"></i>
                                <div class="workflow-pulse"></div>
                                <div class="workflow-step-number">2</div>
                            </div>
                            <div class="workflow-step-content">
                                <h3>AI Processing</h3>
                                <p>7 ML models analyze supplier data simultaneously</p>
                                <div class="workflow-badge">XGBoost, RF, GB, SVM, NN, AdaBoost, Ensemble</div>
                                <div class="workflow-details" style="display: none;">
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Ensemble voting for accuracy</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Real-time model comparison</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>92%+ prediction accuracy</span>
                                    </div>
                                </div>
                                <button class="workflow-learn-more">
                                    <i class="fas fa-info-circle"></i> Learn More
                                </button>
                            </div>
                            <div class="workflow-connector">
                                <div class="workflow-line"></div>
                                <div class="workflow-arrow"><i class="fas fa-arrow-right"></i></div>
                            </div>
                        </div>

                        <div class="workflow-step" data-step="3" data-aos="fade-right" data-aos-delay="300">
                            <div class="workflow-step-icon">
                                <i class="fas fa-shield-alt"></i>
                                <div class="workflow-pulse"></div>
                                <div class="workflow-step-number">3</div>
                            </div>
                            <div class="workflow-step-content">
                                <h3>Risk Assessment</h3>
                                <p>Multi-dimensional risk profiling & anomaly detection</p>
                                <div class="workflow-badge">Real-time Analysis</div>
                                <div class="workflow-details" style="display: none;">
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Geographic risk mapping</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Anomaly detection algorithms</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>40% risk reduction achieved</span>
                                    </div>
                                </div>
                                <button class="workflow-learn-more">
                                    <i class="fas fa-info-circle"></i> Learn More
                                </button>
                            </div>
                            <div class="workflow-connector">
                                <div class="workflow-line"></div>
                                <div class="workflow-arrow"><i class="fas fa-arrow-right"></i></div>
                            </div>
                        </div>

                        <div class="workflow-step" data-step="4" data-aos="fade-right" data-aos-delay="400">
                            <div class="workflow-step-icon">
                                <i class="fas fa-file-contract"></i>
                                <div class="workflow-pulse"></div>
                                <div class="workflow-step-number">4</div>
                            </div>
                            <div class="workflow-step-content">
                                <h3>Contract Analysis</h3>
                                <p>NLP-powered contract review with Gemini AI insights</p>
                                <div class="workflow-badge">BERT, spaCy, Gemini</div>
                                <div class="workflow-details" style="display: none;">
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Entity extraction & classification</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Risk clause identification</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>AI-powered recommendations</span>
                                    </div>
                                </div>
                                <button class="workflow-learn-more">
                                    <i class="fas fa-info-circle"></i> Learn More
                                </button>
                            </div>
                            <div class="workflow-connector">
                                <div class="workflow-line"></div>
                                <div class="workflow-arrow"><i class="fas fa-arrow-right"></i></div>
                            </div>
                        </div>

                        <div class="workflow-step" data-step="5" data-aos="fade-right" data-aos-delay="500">
                            <div class="workflow-step-icon">
                                <i class="fas fa-balance-scale"></i>
                                <div class="workflow-pulse"></div>
                                <div class="workflow-step-number">5</div>
                            </div>
                            <div class="workflow-step-content">
                                <h3>Decision Support</h3>
                                <p>TOPSIS & AHP algorithms for optimal selection</p>
                                <div class="workflow-badge">Multi-Criteria Analysis</div>
                                <div class="workflow-details" style="display: none;">
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Customizable weight assignments</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Optimal supplier ranking</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Scenario-based analysis</span>
                                    </div>
                                </div>
                                <button class="workflow-learn-more">
                                    <i class="fas fa-info-circle"></i> Learn More
                                </button>
                            </div>
                            <div class="workflow-connector">
                                <div class="workflow-line"></div>
                                <div class="workflow-arrow"><i class="fas fa-arrow-right"></i></div>
                            </div>
                        </div>

                        <div class="workflow-step" data-step="6" data-aos="fade-right" data-aos-delay="600">
                            <div class="workflow-step-icon">
                                <i class="fas fa-check-circle"></i>
                                <div class="workflow-pulse"></div>
                                <div class="workflow-step-number">6</div>
                            </div>
                            <div class="workflow-step-content">
                                <h3>Ethics & Compliance</h3>
                                <p>Explainable AI with SHAP/LIME & bias detection</p>
                                <div class="workflow-badge">Transparent Decisions</div>
                                <div class="workflow-details" style="display: none;">
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>SHAP value explanations</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Bias detection algorithms</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>ESG compliance scoring</span>
                                    </div>
                                </div>
                                <button class="workflow-learn-more">
                                    <i class="fas fa-info-circle"></i> Learn More
                                </button>
                            </div>
                            <div class="workflow-connector">
                                <div class="workflow-line"></div>
                                <div class="workflow-arrow"><i class="fas fa-arrow-right"></i></div>
                            </div>
                        </div>

                        <div class="workflow-step workflow-step-final" data-step="7" data-aos="fade-right" data-aos-delay="700">
                            <div class="workflow-step-icon">
                                <i class="fas fa-chart-line"></i>
                                <div class="workflow-pulse"></div>
                                <div class="workflow-step-number">7</div>
                            </div>
                            <div class="workflow-step-content">
                                <h3>Visualization & Insights</h3>
                                <p>Interactive dashboards with 3D charts & real-time metrics</p>
                                <div class="workflow-badge">Executive Dashboard</div>
                                <div class="workflow-details" style="display: none;">
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>3D interactive visualizations</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Real-time metric updates</span>
                                    </div>
                                    <div class="workflow-detail-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>Exportable reports & insights</span>
                                    </div>
                                </div>
                                <button class="workflow-learn-more">
                                    <i class="fas fa-info-circle"></i> Learn More
                                </button>
                            </div>
                        </div>

                        <!-- Animated Data Flow -->
                        <div class="workflow-data-flow" id="workflow-data-flow" style="display: none;">
                            <!-- Data particles removed -->
                        </div>
                    </div>

                    <!-- Workflow Stats -->
                    <div class="workflow-stats" data-aos="fade-up" data-aos-delay="800">
                        <div class="workflow-stat-item">
                            <div class="workflow-stat-icon"><i class="fas fa-clock"></i></div>
                            <div class="workflow-stat-value">95%</div>
                            <div class="workflow-stat-label">Time Saved</div>
                        </div>
                        <div class="workflow-stat-item">
                            <div class="workflow-stat-icon"><i class="fas fa-shield-alt"></i></div>
                            <div class="workflow-stat-value">40%</div>
                            <div class="workflow-stat-label">Risk Reduced</div>
                        </div>
                        <div class="workflow-stat-item">
                            <div class="workflow-stat-icon"><i class="fas fa-dollar-sign"></i></div>
                            <div class="workflow-stat-value">20%</div>
                            <div class="workflow-stat-label">Cost Optimized</div>
                        </div>
                        <div class="workflow-stat-item">
                            <div class="workflow-stat-icon"><i class="fas fa-check-double"></i></div>
                            <div class="workflow-stat-value">99%</div>
                            <div class="workflow-stat-label">Accuracy</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Dashboard Access Section -->
            <section class="dashboard-grid" data-aos="fade-up" data-aos-duration="800">
                <div class="container" style="grid-column: 1 / -1; margin-bottom: 3rem; text-align: center;">
                    <h2 class="text-center mb-2" data-aos="fade-up" data-aos-duration="600" style="font-size: 2.5rem; font-weight: 700;">
                        Explore Our Dashboards
                    </h2>
                    <p class="text-center mb-5" data-aos="fade-up" data-aos-delay="100" style="font-size: 1.2rem; color: var(--corp-gray-600);">
                        Access powerful analytics tools designed for executive decision-making
                    </p>
                </div>
                        <div class="dashboard-card" data-aos="zoom-in" data-aos-delay="100" onclick="window.app.navigateToPage('supplier-evaluation')">
                            <div class="dashboard-card-icon"><i class="fas fa-chart-line"></i></div>
                            <h3 class="dashboard-card-title">Supplier Evaluation</h3>
                            <p class="dashboard-card-description">
                                Evaluate and rank suppliers using 7 ML models with interactive visualizations and feature importance analysis.
                            </p>
                            <a href="#" class="dashboard-card-link" onclick="event.stopPropagation(); window.app.navigateToPage('supplier-evaluation'); return false;">
                                Explore <i class="fas fa-arrow-right"></i>
                            </a>
                        </div>
                        <div class="dashboard-card" data-aos="zoom-in" data-aos-delay="200" onclick="window.app.navigateToPage('risk-profiling')">
                            <div class="dashboard-card-icon"><i class="fas fa-shield-alt"></i></div>
                            <h3 class="dashboard-card-title">Risk Profiling</h3>
                            <p class="dashboard-card-description">
                                Predict supplier risks, detect anomalies, and visualize geographic risk distribution with real-time updates.
                            </p>
                            <a href="#" class="dashboard-card-link" onclick="event.stopPropagation(); window.app.navigateToPage('risk-profiling'); return false;">
                                Explore <i class="fas fa-arrow-right"></i>
                            </a>
                        </div>
                        <div class="dashboard-card" data-aos="zoom-in" data-aos-delay="300" onclick="window.app.navigateToPage('fraud-prediction')">
                            <div class="dashboard-card-icon"><i class="fas fa-exclamation-triangle"></i></div>
                            <h3 class="dashboard-card-title">Fraud Prediction</h3>
                            <p class="dashboard-card-description">
                                Detect potential fraud with advanced ML models and compare predictions across multiple algorithms.
                            </p>
                            <a href="#" class="dashboard-card-link" onclick="event.stopPropagation(); window.app.navigateToPage('fraud-prediction'); return false;">
                                Explore <i class="fas fa-arrow-right"></i>
                            </a>
                        </div>
                        <div class="dashboard-card" data-aos="zoom-in" data-aos-delay="400" onclick="window.app.navigateToPage('nlp-contract')">
                            <div class="dashboard-card-icon"><i class="fas fa-file-contract"></i></div>
                            <h3 class="dashboard-card-title">NLP Contract Analyzer</h3>
                            <p class="dashboard-card-description">
                                Analyze contracts with AI-powered NLP, extract entities, identify risks, and get Gemini AI insights.
                            </p>
                            <a href="#" class="dashboard-card-link" onclick="event.stopPropagation(); window.app.navigateToPage('nlp-contract'); return false;">
                                Explore <i class="fas fa-arrow-right"></i>
                            </a>
                        </div>
                        <div class="dashboard-card" data-aos="zoom-in" data-aos-delay="500" onclick="window.app.navigateToPage('decision-support')">
                            <div class="dashboard-card-icon"><i class="fas fa-balance-scale"></i></div>
                            <h3 class="dashboard-card-title">Decision Support</h3>
                            <p class="dashboard-card-description">
                                Multi-criteria decision support with TOPSIS and AHP algorithms for optimal supplier selection.
                            </p>
                            <a href="#" class="dashboard-card-link" onclick="event.stopPropagation(); window.app.navigateToPage('decision-support'); return false;">
                                Explore <i class="fas fa-arrow-right"></i>
                            </a>
                        </div>
                        <div class="dashboard-card" data-aos="zoom-in" data-aos-delay="600" onclick="window.app.navigateToPage('ethics-compliance')">
                            <div class="dashboard-card-icon"><i class="fas fa-check-circle"></i></div>
                            <h3 class="dashboard-card-title">Ethics & Compliance</h3>
                            <p class="dashboard-card-description">
                                Explainable AI with SHAP/LIME, bias detection, and ESG compliance scoring for ethical decisions.
                            </p>
                            <a href="#" class="dashboard-card-link" onclick="event.stopPropagation(); window.app.navigateToPage('ethics-compliance'); return false;">
                                Explore <i class="fas fa-arrow-right"></i>
                            </a>
                        </div>
                        <div class="dashboard-card" data-aos="zoom-in" data-aos-delay="700" onclick="window.app.navigateToPage('transparency')">
                            <div class="dashboard-card-icon"><i class="fas fa-globe"></i></div>
                            <h3 class="dashboard-card-title">Transparency & Resilience</h3>
                            <p class="dashboard-card-description">
                                Global supply chain visualization, resilience metrics, and transparency scores for comprehensive oversight.
                            </p>
                            <a href="#" class="dashboard-card-link" onclick="event.stopPropagation(); window.app.navigateToPage('transparency'); return false;">
                                Explore <i class="fas fa-arrow-right"></i>
                            </a>
                        </div>
            </section>

            <!-- Technology Stack Section -->
            <section style="background: var(--gradient-dark); padding: 6rem 2rem; color: white;" data-aos="fade-up">
                <div class="container" style="max-width: 1200px; margin: 0 auto;">
                    <h2 class="text-center mb-5" style="font-size: 2.5rem; font-weight: 700;" data-aos="fade-up">
                        Technology Stack
                    </h2>
                    <div class="row" style="max-width: 1200px; margin: 0 auto;">
                        <div class="col-md-4 mb-4" data-aos="fade-up" data-aos-delay="100">
                            <h4 style="margin-bottom: 1.5rem;"><i class="fas fa-brain"></i> Machine Learning</h4>
                            <ul style="list-style: none; padding: 0;">
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> XGBoost & Random Forest</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> Gradient Boosting</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> Neural Networks</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> SVM & AdaBoost</li>
                            </ul>
                        </div>
                        <div class="col-md-4 mb-4" data-aos="fade-up" data-aos-delay="200">
                            <h4 style="margin-bottom: 1.5rem;"><i class="fas fa-language"></i> NLP & AI</h4>
                            <ul style="list-style: none; padding: 0;">
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> BERT & spaCy</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> Google Gemini AI</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> SHAP & LIME</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> TOPSIS & AHP</li>
                            </ul>
                        </div>
                        <div class="col-md-4 mb-4" data-aos="fade-up" data-aos-delay="300">
                            <h4 style="margin-bottom: 1.5rem;"><i class="fas fa-code"></i> Infrastructure</h4>
                            <ul style="list-style: none; padding: 0;">
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> FastAPI Backend</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> HTML5/CSS3/JavaScript</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> Plotly.js Visualizations</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem; color: var(--corp-accent);"></i> Render Deployment</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>
        `;
    },

    setupAnimations() {
        // Animate stats on load
        setTimeout(() => {
            this.animateValue('stat-time', 0, 95, 2000, '%');
            this.animateValue('stat-risk', 0, 35, 2000, '%');
            this.animateValue('stat-cost', 0, 17, 2000, '%');
            this.animateValue('stat-models', 0, 7, 2000, '+');
        }, 500);
    },

    animateValue(id, start, end, duration, suffix = '') {
        const element = document.getElementById(id);
        if (!element) return;
        
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current) + suffix;
        }, 16);
    },

    setupScrollReveal() {
        const reveals = document.querySelectorAll('.scroll-reveal');
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, { threshold: 0.1 });

        reveals.forEach(reveal => revealObserver.observe(reveal));
    },

    async loadStats() {
        // Load real stats if available
        try {
            const health = await (window.api).checkGeminiHealth();
            if (health.status === 'healthy') {
                console.log('Gemini AI is ready');
            } else {
                // Gemini API quota exceeded or unavailable - this is OK, app still works
                console.log('Gemini AI unavailable (quota exceeded or service down). Core ML features still available.');
            }
        } catch (e) {
            // Silently handle - Gemini is optional, core features still work
            console.log('Gemini AI check failed. Core ML features still available.');
        }
    },

    setupWorkflow() {
        setTimeout(() => {
            const container = document.getElementById('workflow-container');
            if (!container) {
                console.warn('Workflow container not found');
                return;
            }

            const steps = container.querySelectorAll('.workflow-step');
            const dataFlow = document.getElementById('workflow-data-flow');
            
            if (!steps.length || !dataFlow) return;

            // Animate steps sequentially on load
            steps.forEach((step, index) => {
                setTimeout(() => {
                    step.classList.add('workflow-active', 'workflow-step-highlight');
                    
                    // Animate connector
                    const connector = step.querySelector('.workflow-connector');
                    if (connector) {
                        setTimeout(() => {
                            connector.classList.add('workflow-connector-active');
                        }, 300);
                    }

                    // Remove highlight after animation
                    setTimeout(() => {
                        step.classList.remove('workflow-step-highlight');
                    }, 1000);
                }, index * 400);
            });

            // Data particles animation removed - no longer animating particles
            // The workflow-data-flow container is hidden via CSS (display: none)

            // Click to expand details
            steps.forEach(step => {
                const learnMoreBtn = step.querySelector('.workflow-learn-more');
                const details = step.querySelector('.workflow-details');
                
                if (learnMoreBtn && details) {
                    learnMoreBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const isExpanded = details.style.display !== 'none';
                        if (isExpanded) {
                            details.style.display = 'none';
                            this.innerHTML = '<i class="fas fa-info-circle"></i> Learn More';
                            step.classList.remove('workflow-step-expanded');
                        } else {
                            details.style.display = 'block';
                            this.innerHTML = '<i class="fas fa-times"></i> Close';
                            step.classList.add('workflow-step-expanded');
                            
                            // Close other expanded steps
                            steps.forEach(s => {
                                if (s !== step) {
                                    const d = s.querySelector('.workflow-details');
                                    const b = s.querySelector('.workflow-learn-more');
                                    if (d && b) {
                                        d.style.display = 'none';
                                        b.innerHTML = '<i class="fas fa-info-circle"></i> Learn More';
                                        s.classList.remove('workflow-step-expanded');
                                    }
                                }
                            });
                        }
                    });
                }

                // Enhanced hover interactions
                step.addEventListener('mouseenter', function() {
                    this.classList.add('workflow-step-hover');
                    const icon = this.querySelector('.workflow-step-icon');
                    if (icon) {
                        icon.style.transform = 'scale(1.15) rotate(5deg)';
                    }
                });

                step.addEventListener('mouseleave', function() {
                    this.classList.remove('workflow-step-hover');
                    const icon = this.querySelector('.workflow-step-icon');
                    if (icon) {
                        icon.style.transform = '';
                    }
                });

                // Click to highlight
                step.addEventListener('click', function() {
                    steps.forEach(s => s.classList.remove('workflow-step-clicked'));
                    this.classList.add('workflow-step-clicked');
                    setTimeout(() => {
                        this.classList.remove('workflow-step-clicked');
                    }, 2000);
                });
            });

            // Continuous pulse animation for active step
            let currentStep = 0;
            setInterval(() => {
                steps.forEach(step => step.classList.remove('workflow-step-pulse'));
                if (steps[currentStep]) {
                    steps[currentStep].classList.add('workflow-step-pulse');
                }
                currentStep = (currentStep + 1) % steps.length;
            }, 3000);
        }, 500);
    }
};
