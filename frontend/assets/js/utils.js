// Utility Functions
window.utils = {
    formatNumber(value, decimals = 2) {
        if (value === null || value === undefined) return '-';
        return parseFloat(value).toFixed(decimals);
    },

    formatPercentage(value) {
        if (value === null || value === undefined) return '-';
        return (parseFloat(value) * 100).toFixed(1) + '%';
    },

    createTable(data, containerId, columns = null) {
        const container = typeof containerId === 'string' 
            ? document.getElementById(containerId) || document.querySelector(containerId)
            : containerId;
        
        if (!container) {
            console.error('Container not found:', containerId);
            return;
        }

        if (!data || data.length === 0) {
            container.innerHTML = '<p class="text-center text-secondary">No data available</p>';
            return;
        }

        // If columns not specified, use all keys from first object
        if (!columns) {
            columns = Object.keys(data[0]).map(key => ({
                key: key,
                label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            }));
        }

        let html = '<table class="table table-hover"><thead><tr>';
        columns.forEach(col => {
            html += `<th>${col.label}</th>`;
        });
        html += '</tr></thead><tbody>';

        data.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                let value = row[col.key];
                if (col.format && typeof col.format === 'function') {
                    value = col.format(value, row);
                } else if (typeof value === 'number') {
                    value = this.formatNumber(value);
                }
                html += `<td>${value || '-'}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    },

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
};

