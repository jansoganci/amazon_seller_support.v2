class DataLoader {
    constructor(module) {
        this.module = module;
        this.charts = {};
        this.isLoading = false;
        this.metricConfigs = window.metricConfigs || {};
    }

    async loadData(params) {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            showToast('Loading data...', 'info');
            
            const queryParams = new URLSearchParams({
                ...params,
                store_id: window.storeId // Assumed to be set in the template
            });
            
            const response = await fetch(`/${this.module}/api/trends?${queryParams}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.updateCharts(data);
            this.updateMetrics(data);
            showToast('Data updated successfully', 'success');
            
        } catch (error) {
            console.error('Error loading data:', error);
            showToast(error.message || 'An error occurred while loading data', 'error');
        } finally {
            this.isLoading = false;
        }
    }

    initializeCharts() {
        // Initialize charts based on metric configurations
        Object.entries(this.metricConfigs).forEach(([metricId, config]) => {
            if (config.visualization.chartType) {
                const chartElement = document.getElementById(metricId + 'Chart');
                if (chartElement) {
                    this.charts[metricId] = ChartFactory.createChart(
                        config.visualization.chartType,
                        chartElement.getContext('2d'),
                        {
                            label: config.name,
                            color: config.visualization.color || this.getDefaultColor(metricId),
                            bgColor: config.visualization.bgColor || this.getDefaultBgColor(metricId),
                            valueType: config.visualization.type
                        }
                    );
                }
            }
        });
    }

    updateCharts(data) {
        // Update each chart with its corresponding data
        Object.entries(this.charts).forEach(([metricId, chart]) => {
            if (data[metricId] && data.labels) {
                this.updateChart(chart, data.labels, data[metricId], this.metricConfigs[metricId]);
            }
        });
    }

    updateChart(chart, labels, data, config) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;

        // Apply any specific chart options from the metric config
        if (config && config.visualization.options) {
            chart.options = {
                ...chart.options,
                ...config.visualization.options
            };
        }

        chart.update();
    }

    updateMetrics(data) {
        // Update metric cards with formatted values
        Object.entries(this.metricConfigs).forEach(([metricId, config]) => {
            const value = data[metricId];
            const growth = data[metricId + '_growth'];
            
            if (value !== undefined) {
                // Update value
                const formattedValue = this.formatValue(value, config.visualization);
                const valueElement = document.getElementById(metricId);
                if (valueElement) {
                    valueElement.textContent = formattedValue;
                }

                // Update growth indicator if available
                const growthElement = document.getElementById(metricId + 'Growth');
                if (growthElement && growth !== undefined) {
                    const growthClass = growth >= 0 ? 'text-green-500' : 'text-red-500';
                    const growthIcon = growth >= 0 ? '↑' : '↓';
                    growthElement.innerHTML = `<span class="${growthClass}">${growthIcon} ${Math.abs(growth).toFixed(2)}%</span>`;
                }

                // Update thresholds if configured
                if (config.thresholds) {
                    const card = valueElement?.closest('.metric-card');
                    if (card) {
                        this.updateThresholdStatus(card, value, config.thresholds);
                    }
                }
            }
        });
    }

    formatValue(value, visualization) {
        switch (visualization.type) {
            case 'currency':
                return this.formatCurrency(value);
            case 'percentage':
                return this.formatPercentage(value);
            case 'number':
                return this.formatNumber(value);
            default:
                return value;
        }
    }

    updateThresholdStatus(card, value, thresholds) {
        const numericValue = parseFloat(String(value).replace(/[^0-9.-]+/g, ''));
        let status = 'normal';

        if (thresholds.direction === 'desc') {
            if (numericValue <= thresholds.critical) status = 'critical';
            else if (numericValue <= thresholds.warning) status = 'warning';
        } else {
            if (numericValue >= thresholds.critical) status = 'critical';
            else if (numericValue >= thresholds.warning) status = 'warning';
        }

        // Remove existing status classes
        card.classList.remove('border-yellow-400', 'border-red-400');
        
        // Add new status class
        if (status === 'warning') card.classList.add('border-yellow-400');
        else if (status === 'critical') card.classList.add('border-red-400');
    }

    getDefaultColor(metricId) {
        const colors = {
            total_revenue: '#3b82f6',      // blue
            total_orders: '#10b981',       // green
            total_sessions: '#8b5cf6',     // purple
            conversion_rate: '#f59e0b',    // amber
            average_order_value: '#ef4444'  // red
        };
        return colors[metricId] || '#6b7280'; // gray as default
    }

    getDefaultBgColor(metricId) {
        const color = this.getDefaultColor(metricId);
        return color.replace(')', ', 0.1)').replace('rgb', 'rgba');
    }

    formatCurrency(value) {
        return '$' + parseFloat(value).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    formatNumber(value) {
        return parseFloat(value).toLocaleString('en-US');
    }

    formatPercentage(value) {
        return parseFloat(value).toFixed(2) + '%';
    }
}

// Utility functions
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const content = document.createElement('div');
    content.className = 'flex items-center';
    
    const icon = document.createElement('i');
    switch(type) {
        case 'success':
            icon.className = 'fas fa-check-circle mr-2';
            break;
        case 'error':
            icon.className = 'fas fa-exclamation-circle mr-2';
            break;
        case 'warning':
            icon.className = 'fas fa-exclamation-triangle mr-2';
            break;
        case 'info':
            icon.className = 'fas fa-info-circle mr-2';
            break;
    }
    
    content.appendChild(icon);
    
    const text = document.createElement('span');
    text.textContent = message;
    content.appendChild(text);
    
    toast.appendChild(content);
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}