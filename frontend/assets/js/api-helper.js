// Helper function to get API client safely
function getAPIClient() {
    if (typeof window !== 'undefined' && window.api) {
        return window.api;
    }
    if (typeof api !== 'undefined') {
        return api;
    }
    throw new Error('API client not available. Please ensure api.js is loaded before using this function.');
}

// Make it globally available
if (typeof window !== 'undefined') {
    window.getAPIClient = getAPIClient;
}

