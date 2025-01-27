document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    const filterManager = new FilterManager('business');
    const dataLoader = new DataLoader('business');

    // Initialize charts
    dataLoader.initializeCharts();

    // Initialize date range picker and other filters
    filterManager.initializeDateRange(() => {
        dataLoader.loadData(filterManager.getCurrentFilters());
    });

    // Handle apply filters button
    document.getElementById('applyFilters').addEventListener('click', () => {
        dataLoader.loadData(filterManager.getCurrentFilters());
    });

    // Handle clear filters button
    document.getElementById('clearFilters').addEventListener('click', () => {
        const defaultFilters = filterManager.clearFilters();
        dataLoader.loadData(defaultFilters);
    });

    // Load initial data
    if (window.initialData) {
        dataLoader.updateCharts(window.initialData);
        dataLoader.updateMetrics(window.initialData);
    } else {
        dataLoader.loadData(filterManager.getCurrentFilters());
    }
}); 