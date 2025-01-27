class FilterManager {
    constructor(reportType, onChangeCallback) {
        this.reportType = reportType;
        this.onChangeCallback = onChangeCallback;
        this.filters = {
            dateRange: {
                startDate: moment().subtract(7, 'days').format('YYYY-MM-DD'),
                endDate: moment().format('YYYY-MM-DD')
            },
            category: 'all',
            asin: ''
        };

        this.initializeDateRange();
        this.initializeOtherFilters();
    }

    initializeDateRange() {
        const dateRangePicker = document.getElementById('dateRangePicker');
        if (!dateRangePicker) return;

        const ranges = {
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'Last 90 Days': [moment().subtract(89, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        };

        $(dateRangePicker).daterangepicker({
            startDate: moment(this.filters.dateRange.startDate),
            endDate: moment(this.filters.dateRange.endDate),
            ranges: ranges,
            maxDate: moment(),
            locale: {
                format: 'YYYY-MM-DD'
            }
        }, (start, end) => {
            this.filters.dateRange = {
                startDate: start.format('YYYY-MM-DD'),
                endDate: end.format('YYYY-MM-DD')
            };
            if (this.onChangeCallback) this.onChangeCallback();
        });
    }

    initializeOtherFilters() {
        const categorySelect = document.getElementById('categoryFilter');
        const asinInput = document.getElementById('asinFilter');

        if (categorySelect) {
            categorySelect.addEventListener('change', (e) => {
                this.filters.category = e.target.value;
                if (this.onChangeCallback) this.onChangeCallback();
            });
        }

        if (asinInput) {
            asinInput.addEventListener('input', (e) => {
                this.filters.asin = e.target.value.trim();
                if (this.onChangeCallback) this.onChangeCallback();
            });
        }

        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }
    }

    getCurrentFilters() {
        return {
            reportType: this.reportType,
            ...this.filters
        };
    }

    clearFilters() {
        // Reset date range to last 7 days
        const dateRangePicker = document.getElementById('dateRangePicker');
        if (dateRangePicker) {
            const start = moment().subtract(6, 'days');
            const end = moment();
            $(dateRangePicker).data('daterangepicker').setStartDate(start);
            $(dateRangePicker).data('daterangepicker').setEndDate(end);
            this.filters.dateRange = {
                startDate: start.format('YYYY-MM-DD'),
                endDate: end.format('YYYY-MM-DD')
            };
        }

        // Reset category
        const categorySelect = document.getElementById('categoryFilter');
        if (categorySelect) {
            categorySelect.value = 'all';
            this.filters.category = 'all';
        }

        // Reset ASIN
        const asinInput = document.getElementById('asinFilter');
        if (asinInput) {
            asinInput.value = '';
            this.filters.asin = '';
        }

        if (this.onChangeCallback) this.onChangeCallback();
    }
} 