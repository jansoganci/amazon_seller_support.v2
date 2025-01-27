// Inventory Report JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date range picker
    initializeDateRangePicker();
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Load initial data
    loadInventoryData();
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
        loadInventoryData();
    });

    // Date range change
    $('#daterange').on('apply.daterangepicker', function() {
        loadInventoryData();
    });

    // ASIN selector change
    document.getElementById('asin').addEventListener('change', function() {
        loadInventoryData();
    });

    // Warehouse selector change
    document.getElementById('warehouse').addEventListener('change', function() {
        loadInventoryData();
    });
}

// Load inventory data from the server
function loadInventoryData() {
    const filters = getFilters();
    
    fetch('/inventory/data?' + new URLSearchParams(filters))
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
        warehouse: document.getElementById('warehouse').value
    };
}

// Update charts with new data
function updateCharts(data) {
    updateStockLevelsChart(data.stock_levels);
    updateStockDistributionChart(data.stock_distribution);
}

// Update stock levels chart
function updateStockLevelsChart(data) {
    const ctx = document.getElementById('stockLevelsChart').getContext('2d');
    
    if (window.stockLevelsChart) {
        window.stockLevelsChart.destroy();
    }
    
    window.stockLevelsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Sellable',
                    data: data.sellable,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                },
                {
                    label: 'Reserved',
                    data: data.reserved,
                    borderColor: 'rgb(255, 159, 64)',
                    tension: 0.1
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
                    beginAtZero: true
                }
            }
        }
    });
}

// Update stock distribution chart
function updateStockDistributionChart(data) {
    const ctx = document.getElementById('stockDistributionChart').getContext('2d');
    
    if (window.stockDistributionChart) {
        window.stockDistributionChart.destroy();
    }
    
    window.stockDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Sellable', 'Unsellable', 'Reserved'],
            datasets: [{
                data: [data.sellable, data.unsellable, data.reserved],
                backgroundColor: [
                    'rgb(75, 192, 192)',
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

// Update metrics with new data
function updateMetrics(data) {
    document.getElementById('totalStock').textContent = data.total_stock;
    document.getElementById('reservedStock').textContent = data.reserved_stock;
    document.getElementById('lowStockItems').textContent = data.low_stock_items;
}

// Update table with new data
function updateTable(data) {
    const tbody = document.getElementById('inventoryTableBody');
    tbody.innerHTML = '';
    
    data.inventory_items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.asin}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.sku}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.product_name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.sellable}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.unsellable}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.reserved}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">${item.warehouse}</td>
        `;
        tbody.appendChild(row);
    });
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