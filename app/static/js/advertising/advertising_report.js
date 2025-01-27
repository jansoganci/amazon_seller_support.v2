// Advertising Report JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date range picker
    initializeDateRangePicker();
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Load initial data
    loadAdvertisingData();
});

// Initialize date range picker
function initializeDateRangePicker() {
    $('#daterange').daterangepicker({
        startDate: moment().subtract(7, 'days'),
        endDate: moment(),
        ranges: {
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'Last 90 Days': [moment().subtract(89, 'days'), moment()]
        }
    });
}

// Initialize event listeners
function initializeEventListeners() {
    // Period selector change
    document.getElementById('period').addEventListener('change', function() {
        loadAdvertisingData();
    });

    // Date range change
    $('#daterange').on('apply.daterangepicker', function() {
        loadAdvertisingData();
    });

    // Campaign selector change
    document.getElementById('campaign').addEventListener('change', function() {
        loadAdvertisingData();
    });

    // Ad group selector change
    document.getElementById('adGroup').addEventListener('change', function() {
        loadAdvertisingData();
    });
}

// Load advertising data from the server
function loadAdvertisingData() {
    const filters = getFilters();
    
    fetch('/advertising/data?' + new URLSearchParams(filters))
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
            updateMetrics(data);
            updateTable(data);
        })
        .catch(error => {
            showToast('Error loading data: ' + error.message, 'error');
        });
}

// Get current filter values
function getFilters() {
    const dateRange = $('#daterange').data('daterangepicker');
    return {
        period: document.getElementById('period').value,
        start_date: dateRange.startDate.format('YYYY-MM-DD'),
        end_date: dateRange.endDate.format('YYYY-MM-DD'),
        campaign: document.getElementById('campaign').value,
        ad_group: document.getElementById('adGroup').value
    };
}

// Update charts with new data
function updateCharts(data) {
    updatePerformanceChart(data.performance);
    updateMetricsChart(data.metrics);
}

// Update performance chart
function updatePerformanceChart(data) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    if (window.performanceChart) {
        window.performanceChart.destroy();
    }
    
    window.performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'ACOS (%)',
                    data: data.acos,
                    borderColor: 'rgb(75, 192, 192)',
                    yAxisID: 'y',
                    tension: 0.1
                },
                {
                    label: 'Spend ($)',
                    data: data.spend,
                    borderColor: 'rgb(255, 99, 132)',
                    yAxisID: 'y1',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'ACOS (%)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Spend ($)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// Update metrics chart
function updateMetricsChart(data) {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    
    if (window.metricsChart) {
        window.metricsChart.destroy();
    }
    
    window.metricsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Impressions',
                    data: data.impressions,
                    backgroundColor: 'rgb(75, 192, 192)',
                    yAxisID: 'y'
                },
                {
                    label: 'Clicks',
                    data: data.clicks,
                    backgroundColor: 'rgb(255, 99, 132)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Impressions'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Clicks'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// Update metrics with new data
function updateMetrics(data) {
    document.getElementById('totalSpend').textContent = formatCurrency(data.total_spend);
    document.getElementById('totalSales').textContent = formatCurrency(data.total_sales);
    document.getElementById('acos').textContent = data.acos.toFixed(2) + '%';
    document.getElementById('roas').textContent = data.roas.toFixed(2);
}

// Update table with new data
function updateTable(data) {
    const tbody = document.getElementById('advertisingTableBody');
    tbody.innerHTML = '';
    
    data.campaigns.forEach(campaign => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${campaign.name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${campaign.status}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${campaign.impressions}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${campaign.clicks}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${campaign.ctr}%</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${formatCurrency(campaign.spend)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${formatCurrency(campaign.sales)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${campaign.acos}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Show toast message
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `p-4 mb-4 rounded-lg ${type === 'error' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`;
    toast.textContent = message;
    
    const container = document.getElementById('toastContainer');
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
} 