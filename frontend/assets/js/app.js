// Main Application JavaScript
class DashboardApp {
    constructor() {
        this.currentPage = 'home';
        this.api = typeof api !== 'undefined' ? api : null;
        this.initialized = false;
    }

    init() {
        if (this.initialized) {
            console.warn('DashboardApp already initialized');
            return;
        }
        this.initialized = true;
        this.setupNavigation();
        this.setupSidebarToggle();
        // Initialize landing page layout
        this.navigateToPage('home');
    }

    setupNavigation() {
        document.querySelectorAll('.sidebar-menu a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.navigateToPage(page);
            });
        });
    }

    setupSidebarToggle() {
        const toggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('main-content');

        if (toggle) {
            toggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
                mainContent.classList.toggle('sidebar-collapsed');
            });
        }
    }

    navigateToPage(pageName) {
        const isFromLanding = this.currentPage === 'home' && pageName !== 'home';
        
        // Show creative loading animation when navigating from landing page
        if (isFromLanding) {
            this.showNavigationLoading();
        }
        
        // Update active menu item
        document.querySelectorAll('.sidebar-menu a').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === pageName) {
                link.classList.add('active');
            }
        });

        // Hide all pages with fade out animation
        document.querySelectorAll('.page-content').forEach(page => {
            if (page.classList.contains('active')) {
                page.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
                page.style.opacity = '0';
                page.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    page.classList.remove('active');
                    page.style.display = 'none';
                    page.style.visibility = 'hidden';
                }, 200);
            }
        });

        // Update active menu item
        document.querySelectorAll('.sidebar-menu a').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === pageName) {
                link.classList.add('active');
            }
        });

        // Show/hide navbar and sidebar based on page
        const navbar = document.getElementById('top-navbar');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('main-content');
        const contentContainer = document.getElementById('main-content-container');
        
        if (pageName === 'home') {
            // Landing page - full width, hide sidebar and navbar
            if (navbar) navbar.style.display = 'none';
            if (sidebar) {
                sidebar.style.display = 'none';
                sidebar.style.visibility = 'hidden';
                sidebar.classList.add('hidden-on-landing');
            }
            if (mainContent) {
                mainContent.style.marginLeft = '0';
                mainContent.style.width = '100%';
            }
            if (contentContainer) {
                contentContainer.style.padding = '0';
                contentContainer.style.margin = '0';
                contentContainer.style.width = '100%';
            }
        } else {
            // Dashboard pages - normal layout, show sidebar and navbar
            if (navbar) navbar.style.display = 'flex';
            if (sidebar) {
                sidebar.style.display = 'block';
                sidebar.style.visibility = 'visible';
                sidebar.classList.remove('hidden-on-landing');
            }
            if (mainContent) {
                mainContent.style.marginLeft = '260px';
                mainContent.style.width = 'calc(100% - 260px)';
            }
            if (contentContainer) {
                contentContainer.style.padding = '2rem';
                contentContainer.style.margin = '0';
                contentContainer.style.width = 'auto';
            }
        }

        // Show selected page with fade in animation
        setTimeout(() => {
            const targetPage = document.getElementById(`page-${pageName}`);
            if (targetPage) {
                targetPage.style.display = 'block';
                targetPage.style.visibility = 'visible';
                targetPage.style.opacity = '0';
                targetPage.style.transform = 'translateX(20px)';
                targetPage.classList.add('active');
                this.currentPage = pageName;
                this.updatePageTitle(pageName);
                
                // Load page content asynchronously
                this.loadPageContent(pageName).then(() => {
                    // Hide navigation loading after content loads
                    if (isFromLanding) {
                        setTimeout(() => {
                            this.hideNavigationLoading();
                        }, 300);
                    }
                }).catch(() => {
                    if (isFromLanding) {
                        this.hideNavigationLoading();
                    }
                });
                
                // Fade in animation
                setTimeout(() => {
                    targetPage.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    targetPage.style.opacity = '1';
                    targetPage.style.transform = 'translateX(0)';
                    
                    // Refresh AOS animations for new page
                    if (typeof AOS !== 'undefined') {
                        setTimeout(() => AOS.refresh(), 100);
                    }
                }, 50);
            } else {
                console.error(`Page element not found: page-${pageName}`);
                if (isFromLanding) {
                    this.hideNavigationLoading();
                }
            }
        }, 200);
    }

    updatePageTitle(pageName) {
        const titles = {
            'home': 'Dashboard Home',
            'supplier-evaluation': 'Supplier Evaluation & Scoring',
            'risk-profiling': 'Risk Profiling & Comparison',
            'fraud-prediction': 'Fraud & Disruption Prediction',
            'nlp-contract': 'NLP Contract Analyzer',
            'decision-support': 'Multi-Criteria Decision Support',
            'ethics-compliance': 'Ethics & Compliance',
            'transparency': 'Transparency & Resilience'
        };
        document.querySelector('.page-title').textContent = titles[pageName] || 'Dashboard';
    }

    async loadPage(pageName) {
        this.showLoading();
        try {
            await this.loadPageContent(pageName);
        } catch (error) {
            console.error('Error loading page:', error);
            this.showError('Failed to load page content');
        } finally {
            this.hideLoading();
        }
    }

    async loadPageContent(pageName) {
        // Load page-specific content
        const pageModules = {
            'home': async () => {
                console.log('Loading home page...');
                if (window.HomePage && typeof window.HomePage.init === 'function') {
                    console.log('HomePage found, calling init()');
                    await window.HomePage.init();
                } else {
                    console.error('HomePage not found. Available:', Object.keys(window).filter(k => k.includes('Page')));
                    // Fallback: render basic content
                    const container = document.getElementById('page-home');
                    if (container) {
                        container.innerHTML = '<div class="alert alert-warning">Loading landing page...</div>';
                    }
                }
            },
            'supplier-evaluation': async () => {
                if (window.SupplierEvaluationPage && typeof window.SupplierEvaluationPage.init === 'function') {
                    await window.SupplierEvaluationPage.init();
                }
            },
            'risk-profiling': async () => {
                if (window.RiskProfilingPage && typeof window.RiskProfilingPage.init === 'function') {
                    await window.RiskProfilingPage.init();
                }
            },
            'fraud-prediction': async () => {
                if (window.FraudPredictionPage && typeof window.FraudPredictionPage.init === 'function') {
                    await window.FraudPredictionPage.init();
                }
            },
            'nlp-contract': async () => {
                if (window.NLPContractPage && typeof window.NLPContractPage.init === 'function') {
                    await window.NLPContractPage.init();
                }
            },
            'decision-support': async () => {
                if (window.DecisionSupportPage && typeof window.DecisionSupportPage.init === 'function') {
                    await window.DecisionSupportPage.init();
                }
            },
            'ethics-compliance': async () => {
                if (window.EthicsCompliancePage && typeof window.EthicsCompliancePage.init === 'function') {
                    await window.EthicsCompliancePage.init();
                }
            },
            'transparency': async () => {
                if (window.TransparencyPage && typeof window.TransparencyPage.init === 'function') {
                    await window.TransparencyPage.init();
                }
            }
        };

        const loader = pageModules[pageName];
        if (loader) {
            try {
                await loader();
            } catch (error) {
                console.error(`Error loading page ${pageName}:`, error);
                this.showError(`Failed to load ${pageName} page: ${error.message}`);
            }
        } else {
            console.warn(`No loader found for page: ${pageName}`);
        }
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.style.display = 'flex';
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.style.display = 'none';
    }

    showNavigationLoading() {
        // Create or show creative navigation loading overlay
        let navLoader = document.getElementById('navigation-loader');
        if (!navLoader) {
            navLoader = document.createElement('div');
            navLoader.id = 'navigation-loader';
            navLoader.innerHTML = `
                <div class="nav-loader-backdrop"></div>
                <div class="nav-loader-content">
                    <div class="nav-loader-animation">
                        <div class="nav-loader-circle nav-loader-circle-1"></div>
                        <div class="nav-loader-circle nav-loader-circle-2"></div>
                        <div class="nav-loader-circle nav-loader-circle-3"></div>
                        <div class="nav-loader-circle nav-loader-circle-4"></div>
                        <div class="nav-loader-circle nav-loader-circle-5"></div>
                    </div>
                    <div class="nav-loader-text">
                        <div class="nav-loader-title">Loading Dashboard</div>
                        <div class="nav-loader-subtitle">Preparing your analytics workspace...</div>
                    </div>
                    <div class="nav-loader-progress">
                        <div class="nav-loader-progress-bar"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(navLoader);
        }
        navLoader.style.display = 'flex';
        navLoader.style.opacity = '0';
        setTimeout(() => {
            navLoader.style.transition = 'opacity 0.3s ease';
            navLoader.style.opacity = '1';
        }, 10);
    }

    hideNavigationLoading() {
        const navLoader = document.getElementById('navigation-loader');
        if (navLoader) {
            navLoader.style.transition = 'opacity 0.3s ease';
            navLoader.style.opacity = '0';
            setTimeout(() => {
                navLoader.style.display = 'none';
            }, 300);
        }
    }

    showError(message) {
        if (window.utils && window.utils.showNotification) {
            window.utils.showNotification(message, 'error');
        } else {
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger';
            alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            document.querySelector('.content-container').prepend(alert);
            setTimeout(() => alert.remove(), 5000);
        }
    }

    showSuccess(message) {
        if (window.utils && window.utils.showNotification) {
            window.utils.showNotification(message, 'success');
        } else {
            const alert = document.createElement('div');
            alert.className = 'alert alert-success';
            alert.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
            document.querySelector('.content-container').prepend(alert);
            setTimeout(() => alert.remove(), 5000);
        }
    }

    showInfo(message) {
        if (window.utils && window.utils.showNotification) {
            window.utils.showNotification(message, 'info');
        }
    }
}

// Initialize app when DOM is ready
(function() {
    function initializeApp() {
        // Prevent double initialization
        if (window.app && window.app.initialized) {
            console.log('App already initialized');
            return;
        }
        
        // Wait for all dependencies
        if (typeof DashboardApp === 'undefined') {
            console.error('DashboardApp not defined');
            return;
        }
        
        try {
            window.app = new DashboardApp();
            window.app.init();
            console.log('DashboardApp initialized successfully');
        } catch (error) {
            console.error('Error initializing DashboardApp:', error);
        }
    }
    
    // Try to initialize immediately if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeApp);
    } else {
        // DOM is already ready
        setTimeout(initializeApp, 100);
    }
})();

