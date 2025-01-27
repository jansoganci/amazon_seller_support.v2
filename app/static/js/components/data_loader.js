class DataLoader {
    constructor(reportType) {
        this.reportType = reportType;
        this.chartFactory = new ChartFactory();
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.toast = document.getElementById('toast');
        this.toastMessage = document.getElementById('toastMessage');
    }

    showLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('hidden');
        }
    }

    hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('hidden');
        }
    }

    showToast(message, isError = false) {
        if (!this.toast || !this.toastMessage) return;

        this.toastMessage.textContent = message;
        this.toast.classList.remove('hidden', 'bg-green-500', 'bg-red-500');
        this.toast.classList.add(isError ? 'bg-red-500' : 'bg-green-500');

        setTimeout(() => {
            this.toast.classList.add('hidden');
        }, 3000);
    }

    initializeCharts() {
        this.chartFactory.createChart('revenueTrend', { labels: [], values: [] });
        this.chartFactory.createChart('conversionRate', { labels: [], values: [] });
        this.chartFactory.createChart('unitsOrdered', { labels: [], values: [] });
        this.chartFactory.createChart('sessions', { labels: [], values: [] });
    }

    async loadData(filters) {
        this.showLoading();

        try {
            const response = await fetch('/api/report/data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(filters)
            });

            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }

            const results = await response.json();
            
            this.updateCharts(results);
            this.updateMetrics(results);
            
            this.showToast('Data updated successfully');
        } catch (error) {
            console.error('Error loading data:', error);
            this.showToast('Failed to load data', true);
        } finally {
            this.hideLoading();
        }
    }

    updateCharts(results) {
        if (results.revenueTrend) {
            this.chartFactory.updateChart('revenueTrend', {
                labels: results.revenueTrend.dates,
                values: results.revenueTrend.values
            });
        }

        if (results.conversionRate) {
            this.chartFactory.updateChart('conversionRate', {
                labels: results.conversionRate.dates,
                values: results.conversionRate.values
            });
        }

        if (results.unitsOrdered) {
            this.chartFactory.updateChart('unitsOrdered', {
                labels: results.unitsOrdered.dates,
                values: results.unitsOrdered.values
            });
        }

        if (results.sessions) {
            this.chartFactory.updateChart('sessions', {
                labels: results.sessions.dates,
                values: results.sessions.values
            });
        }
    }

    updateMetrics(results) {
        const metrics = results.metrics || {};
        
        // Update Total Revenue
        const totalRevenueElement = document.getElementById('totalRevenue');
        if (totalRevenueElement && metrics.totalRevenue !== undefined) {
            totalRevenueElement.textContent = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(metrics.totalRevenue);
        }

        // Update Total Orders
        const totalOrdersElement = document.getElementById('totalOrders');
        if (totalOrdersElement && metrics.totalOrders !== undefined) {
            totalOrdersElement.textContent = metrics.totalOrders.toLocaleString();
        }

        // Update Total Sessions
        const totalSessionsElement = document.getElementById('totalSessions');
        if (totalSessionsElement && metrics.totalSessions !== undefined) {
            totalSessionsElement.textContent = metrics.totalSessions.toLocaleString();
        }

        // Update Average Order Value
        const avgOrderValueElement = document.getElementById('avgOrderValue');
        if (avgOrderValueElement && metrics.avgOrderValue !== undefined) {
            avgOrderValueElement.textContent = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(metrics.avgOrderValue);
        }
    }
} 