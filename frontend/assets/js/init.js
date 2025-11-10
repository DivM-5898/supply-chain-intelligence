// Fix landing page layout on load
(function() {
    function setupLandingPageLayout() {
        const homePage = document.getElementById('page-home');
        if (homePage && homePage.classList.contains('active')) {
            const navbar = document.getElementById('top-navbar');
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('main-content');
            const contentContainer = document.getElementById('main-content-container');
            
            // Hide navbar and sidebar on landing page
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
                contentContainer.style.maxWidth = '100%';
            }
        }
    }
    
    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(setupLandingPageLayout, 200);
        });
    } else {
        setTimeout(setupLandingPageLayout, 200);
    }
    
    // Also run when page becomes active
    const observer = new MutationObserver(() => {
        setupLandingPageLayout();
    });
    
    setTimeout(() => {
        const homePage = document.getElementById('page-home');
        if (homePage) {
            observer.observe(homePage, { attributes: true, attributeFilter: ['class'] });
        }
    }, 500);
})();

