// Ensure API is available globally before any page scripts run
(function() {
    // Wait for DOM and all scripts to load
    function ensureAPIReady() {
        console.log('[API Init Check] Checking API availability...');
        console.log('[API Init Check] window.api:', window.api);
        console.log('[API Init Check] typeof window.api:', typeof window.api);
        
        if (typeof window.api === 'undefined') {
            console.error('[API Init Check] window.api is not defined!');
            console.log('[API Init Check] Available globals:', Object.keys(window).filter(k => k.includes('api')));
            
            // Try to find api in different ways
            if (typeof api !== 'undefined') {
                console.log('[API Init Check] Found api variable, assigning to window.api');
                window.api = api;
            } else if (typeof APIClient !== 'undefined') {
                console.log('[API Init Check] Found APIClient, creating new instance');
                window.api = new APIClient();
            } else {
                console.error('[API Init Check] Neither api nor APIClient found!');
                console.error('[API Init Check] Scripts loaded:', document.querySelectorAll('script[src]').length);
            }
        } else {
            console.log('[API Init Check] window.api exists');
            console.log('[API Init Check] window.api.getAvailableModels:', typeof window.api.getAvailableModels);
            
            // Verify it has the expected methods
            if (typeof window.api.getAvailableModels !== 'function') {
                console.error('[API Init Check] window.api.getAvailableModels is not a function!');
                console.error('[API Init Check] window.api keys:', Object.keys(window.api));
                
                // Try to fix it
                if (typeof window.APIClient !== 'undefined') {
                    console.log('[API Init Check] Reinitializing API client...');
                    try {
                        Object.defineProperty(window, 'api', {
                            value: new window.APIClient(),
                            writable: false,
                            configurable: true,
                            enumerable: true
                        });
                    } catch (e) {
                        window.api = new window.APIClient();
                    }
                }
            } else {
                console.log('[API Init Check] ✅ API client is properly initialized');
            }
        }
    }
    
    // Run immediately if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureAPIReady);
    } else {
        ensureAPIReady();
    }
    
    // Also run after a short delay to catch late-loading scripts
    setTimeout(ensureAPIReady, 100);
    setTimeout(ensureAPIReady, 500);
    setTimeout(ensureAPIReady, 1000);
})();

