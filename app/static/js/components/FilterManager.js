class FilterManager {
    constructor(module) {
        this.module = module;
        this.prefix = `${module}_`;
        
        this.defaultFilters = {
            startDate: moment().subtract(30, 'days').format('YYYY-MM-DD'),
            endDate: moment().format('YYYY-MM-DD'),
            groupBy: 'daily',
            category: '',
            asin: ''
        };
    }

    initializeDateRange(callback) {
        const savedFilters = this.loadFilters();
        
        $('#daterange').daterangepicker({
            startDate: moment(savedFilters.startDate),
            endDate: moment(savedFilters.endDate),
            opens: 'left',
            showDropdowns: true,
            autoApply: false,
            ranges: {
                'Today': [moment(), moment()],
                'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                'This Month': [moment().startOf('month'), moment().endOf('month')],
                'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            locale: {
                format: 'YYYY-MM-DD'
            }
        });

        // Restore other saved filters
        $('#groupBy').val(savedFilters.groupBy);
        $('#category').val(savedFilters.category);
        $('#asin').val(savedFilters.asin);

        // Set up event listeners
        $('#daterange').on('apply.daterangepicker', (ev, picker) => {
            this.saveFilter('startDate', picker.startDate.format('YYYY-MM-DD'));
            this.saveFilter('endDate', picker.endDate.format('YYYY-MM-DD'));
            if (callback) callback();
        });

        ['groupBy', 'category', 'asin'].forEach(filter => {
            $(`#${filter}`).on('change', () => {
                this.saveFilter(filter, $(`#${filter}`).val());
                if (callback) callback();
            });
        });
    }

    saveFilter(key, value) {
        localStorage.setItem(this.prefix + key, value);
    }

    loadFilters() {
        return {
            startDate: localStorage.getItem(this.prefix + 'startDate') || this.defaultFilters.startDate,
            endDate: localStorage.getItem(this.prefix + 'endDate') || this.defaultFilters.endDate,
            groupBy: localStorage.getItem(this.prefix + 'groupBy') || this.defaultFilters.groupBy,
            category: localStorage.getItem(this.prefix + 'category') || this.defaultFilters.category,
            asin: localStorage.getItem(this.prefix + 'asin') || this.defaultFilters.asin
        };
    }

    clearFilters() {
        Object.keys(this.defaultFilters).forEach(key => {
            localStorage.removeItem(this.prefix + key);
        });

        // Reset UI
        const daterangePicker = $('#daterange').data('daterangepicker');
        daterangePicker.setStartDate(moment().subtract(30, 'days'));
        daterangePicker.setEndDate(moment());
        
        $('#groupBy').val(this.defaultFilters.groupBy);
        $('#category').val(this.defaultFilters.category);
        $('#asin').val(this.defaultFilters.asin);

        return this.defaultFilters;
    }

    getCurrentFilters() {
        const daterangePicker = $('#daterange').data('daterangepicker');
        
        return {
            startDate: daterangePicker.startDate.format('YYYY-MM-DD'),
            endDate: daterangePicker.endDate.format('YYYY-MM-DD'),
            groupBy: $('#groupBy').val(),
            category: $('#category').val(),
            asin: $('#asin').val()
        };
    }
} 