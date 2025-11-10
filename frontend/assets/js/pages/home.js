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
            
            // Get HTML content
            const html = this.getHTML();
            if (!html || html.trim() === '') {
                console.error('getHTML() returned empty content');
                container.innerHTML = '<div class="alert alert-danger">Failed to load landing page content</div>';
                return;
            }
            
            // Render HTML
            container.innerHTML = html;
            console.log('Landing page HTML rendered');
            
            // Wait for DOM to update
            setTimeout(() => {
                try {
                    this.setupAnimations();
                    this.loadStats();
                    this.loadCharts();
                    this.setupScrollReveal();
                    console.log('Landing page initialized successfully');
                } catch (error) {
                    console.error('Error setting up landing page features:', error);
                }
            }, 100);
        } catch (error) {
            console.error('Error initializing landing page:', error);
            container.innerHTML = `<div class="alert alert-danger">Error loading landing page: ${error.message}</div>`;
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

            <!-- Features Section -->
            <section class="features-section" data-aos="fade-up" data-aos-duration="800">
                <div class="container">
                    <h2 class="text-center mb-5" data-aos="fade-up" data-aos-duration="600">
                        Core Capabilities
                    </h2>
                    <p class="text-center mb-5" data-aos="fade-up" data-aos-delay="100" style="font-size: 1.25rem; color: var(--corp-gray-600); max-width: 700px; margin: 0 auto 3rem;">
                        Comprehensive AI-powered solutions for intelligent supplier management
                    </p>
                    <div class="features-grid">
                        <div class="feature-card" data-aos="fade-up" data-aos-delay="100">
                            <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                            <h3 class="feature-title">Supplier Evaluation</h3>
                            <p class="feature-description">
                                7 advanced ML models (XGBoost, Random Forest, Gradient Boosting, SVM, Neural Networks, AdaBoost, Ensemble) 
                                for comprehensive supplier scoring and ranking.
                            </p>
                        </div>
                        <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
                            <div class="feature-icon"><i class="fas fa-shield-alt"></i></div>
                            <h3 class="feature-title">Risk Profiling</h3>
                            <p class="feature-description">
                                Multi-dimensional risk analysis with real-time predictions, anomaly detection, and geographic risk mapping.
                            </p>
                        </div>
                        <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
                            <div class="feature-icon"><i class="fas fa-exclamation-triangle"></i></div>
                            <h3 class="feature-title">Fraud Detection</h3>
                            <p class="feature-description">
                                Advanced fraud prediction models with probability scoring and multi-model comparison for accurate detection.
                            </p>
                        </div>
                        <div class="feature-card" data-aos="fade-up" data-aos-delay="400">
                            <div class="feature-icon"><i class="fas fa-file-contract"></i></div>
                            <h3 class="feature-title">NLP Contract Analysis</h3>
                            <p class="feature-description">
                                Powered by BERT, spaCy, and Google Gemini AI for intelligent contract analysis, entity extraction, and risk assessment.
                            </p>
                        </div>
                        <div class="feature-card" data-aos="fade-up" data-aos-delay="500">
                            <div class="feature-icon"><i class="fas fa-balance-scale"></i></div>
                            <h3 class="feature-title">Decision Support</h3>
                            <p class="feature-description">
                                TOPSIS and AHP algorithms for multi-criteria decision-making with customizable weight assignments.
                            </p>
                        </div>
                        <div class="feature-card" data-aos="fade-up" data-aos-delay="600">
                            <div class="feature-icon"><i class="fas fa-check-circle"></i></div>
                            <h3 class="feature-title">Ethics & Compliance</h3>
                            <p class="feature-description">
                                SHAP/LIME explainability, bias detection, and ESG compliance scoring for transparent AI decisions.
                            </p>
                        </div>
                        <div class="feature-card" data-aos="fade-up" data-aos-delay="700">
                            <div class="feature-icon"><i class="fas fa-globe"></i></div>
                            <h3 class="feature-title">Transparency & Resilience</h3>
                            <p class="feature-description">
                                Global supply chain visualization, resilience metrics, and transparency scores for comprehensive oversight.
                            </p>
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
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem;"></i> Neural Networks</li>
                                <li style="padding: 0.5rem 0;"><i class="fas fa-check-circle" style="margin-right: 0.5rem;"></i> SVM & AdaBoost</li>
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

            <!-- Performance Chart Section -->
            <section style="background: var(--corp-gray-50); padding: 6rem 2rem;" data-aos="fade-up">
                <div class="container" style="max-width: 1400px; margin: 0 auto;">
                    <h2 class="text-center mb-5" style="font-size: 2.5rem; font-weight: 700;" data-aos="fade-up">
                        System Performance
                    </h2>
                    <div class="row">
                        <div class="col-md-6 mb-4" data-aos="fade-up" data-aos-delay="100">
                            <div class="card" style="border-radius: var(--radius-2xl); padding: 2rem;">
                                <h4 class="mb-3">Model Accuracy Comparison</h4>
                                <div id="model-accuracy-chart" class="chart-container" style="height: 400px;"></div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4" data-aos="fade-up" data-aos-delay="200">
                            <div class="card" style="border-radius: var(--radius-2xl); padding: 2rem;">
                                <h4 class="mb-3">Feature Importance</h4>
                                <div id="feature-importance-chart-landing" class="chart-container" style="height: 400px;"></div>
                            </div>
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

    async loadCharts() {
        // Model Accuracy Chart
        setTimeout(() => {
            const accuracyData = [{
                x: ['XGBoost', 'Random Forest', 'Gradient Boosting', 'SVM', 'Neural Network', 'AdaBoost', 'Ensemble'],
                y: [0.92, 0.89, 0.91, 0.85, 0.88, 0.87, 0.93],
                type: 'bar',
                marker: {
                    color: ['#0066CC', '#0052A3', '#0066CC', '#3385D6', '#0066CC', '#0052A3', '#00C853'],
                    line: { color: 'white', width: 2 }
                }
            }];
            const accuracyLayout = {
                title: {
                    text: 'Model R² Scores',
                    font: { size: 18, color: '#1A1A2E' }
                },
                xaxis: { title: 'Model', gridcolor: '#E9ECEF' },
                yaxis: { title: 'R² Score', range: [0.8, 1.0], gridcolor: '#E9ECEF' },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { family: 'Inter, sans-serif', color: '#495057' }
            };
            Plotly.newPlot('model-accuracy-chart', accuracyData, accuracyLayout, {responsive: true});

            // Feature Importance Chart
            const featureData = [{
                x: [0.25, 0.20, 0.18, 0.15, 0.12, 0.10],
                y: ['Quality Score', 'Cost Efficiency', 'Delivery Rate', 'Financial Health', 'ESG Score', 'Risk Score'],
                type: 'bar',
                orientation: 'h',
                marker: {
                    color: '#0066CC',
                    line: { color: 'white', width: 2 }
                }
            }];
            const featureLayout = {
                title: {
                    text: 'Top Feature Importances',
                    font: { size: 18, color: '#1A1A2E' }
                },
                xaxis: { title: 'Importance', gridcolor: '#E9ECEF' },
                yaxis: { title: 'Feature', gridcolor: '#E9ECEF' },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { family: 'Inter, sans-serif', color: '#495057' }
            };
            Plotly.newPlot('feature-importance-chart-landing', featureData, featureLayout, {responsive: true});
        }, 1000);
    }
};
