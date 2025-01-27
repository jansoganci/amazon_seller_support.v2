// Return Report JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date range picker
    initializeDateRangePicker();
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Load initial data
    loadReturnData();
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
        loadReturnData();
    });

    // Date range change
    $('#daterange').on('apply.daterangepicker', function() {
        loadReturnData();
    });

    // ASIN selector change
    document.getElementById('asin').addEventListener('change', function() {
        loadReturnData();
    });

    // Return reason selector change
    document.getElementById('returnReason').addEventListener('change', function() {
        loadReturnData();
    });
}

// Load return data from the server
function loadReturnData() {
    const filters = getFilters();
    
    fetch('/returns/data?' + new URLSearchParams(filters))
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
        asin: document.getElementById('asin').value,
        return_reason: document.getElementById('returnReason').value
    };
}

// Update charts with new data
function updateCharts(data) {
    updateReturnRateChart(data.return_rate);
    updateReturnReasonsChart(data.return_reasons);
}

// Update return rate chart
function updateReturnRateChart(data) {
    const ctx = document.getElementById('returnRateChart').getContext('2d');
    
    if (window.returnRateChart) {
        window.returnRateChart.destroy();
    }
    
    window.returnRateChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Return Rate (%)',
                data: data.rates,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
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
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Update return reasons chart
function updateReturnReasonsChart(data) {
    const ctx = document.getElementById('returnReasonsChart').getContext('2d');
    
    if (window.returnReasonsChart) {
        window.returnReasonsChart.destroy();
    }
    
    window.returnReasonsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.reasons,
            datasets: [{
                label: 'Number of Returns',
                data: data.counts,
                backgroundColor: 'rgb(75, 192, 192)',
            }]
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
                    beginAtZero: true
                }
            }
        }
    });
}

// Update metrics with new data
function updateMetrics(data) {
    document.getElementById('totalReturns').textContent = data.total_returns;
    document.getElementById('totalRefund').textContent = formatCurrency(data.total_refund);
    document.getElementById('returnRate').textContent = data.return_rate + '%';
}

// Update table with new data
function updateTable(data) {
    const tbody = document.getElementById('returnTableBody');
    tbody.innerHTML = '';
    
    data.return_items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${formatDate(item.return_date)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.order_id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.asin}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.title}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.quantity}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.return_reason}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${formatCurrency(item.refund_amount)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.status}</td>
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

// Format date
function formatDate(date) {
    return moment(date).format('YYYY-MM-DD');
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