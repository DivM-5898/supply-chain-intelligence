// Debug script to help identify loading issues
(function() {
    console.log('=== DEBUG: Page Loading Check ===');
    console.log('Document ready state:', document.readyState);
    console.log('HomePage available:', typeof window.HomePage !== 'undefined');
    console.log('DashboardApp available:', typeof DashboardApp !== 'undefined');
    console.log('API available:', typeof api !== 'undefined');
    console.log('Utils available:', typeof window.utils !== 'undefined');
    
    // Check DOM elements
    setTimeout(function() {
        const homePage = document.getElementById('page-home');
        console.log('Home page element:', homePage);
        if (homePage) {
            console.log('Home page classes:', homePage.className);
            console.log('Home page display:', window.getComputedStyle(homePage).display);
            console.log('Home page visibility:', window.getComputedStyle(homePage).visibility);
            console.log('Home page innerHTML length:', homePage.innerHTML.length);
        }
        
        const app = window.app;
        if (app) {
            console.log('App initialized:', app.initialized);
            console.log('Current page:', app.currentPage);
        } else {
            console.warn('window.app is not defined');
        }
    }, 1000);
    
    // Log errors
    window.addEventListener('error', function(e) {
        console.error('JavaScript Error:', e.message, e.filename, e.lineno);
    });
})();

