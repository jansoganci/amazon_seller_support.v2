function dateRangePicker(id) {
    return {
        id,
        isOpen: false,
        startDate: null,
        endDate: null,
        
        init() {
            // Set default dates (last 30 days)
            const end = new Date();
            const start = new Date();
            start.setDate(start.getDate() - 30);
            
            this.startDate = this.formatDate(start);
            this.endDate = this.formatDate(end);
            
            // Dispatch initial event
            this.dispatchDateChange();
        },
        
        get formatDateRange() {
            if (!this.startDate && !this.endDate) return 'Select date range';
            if (!this.endDate) return `From ${this.formatDateForDisplay(this.startDate)}`;
            return `${this.formatDateForDisplay(this.startDate)} - ${this.formatDateForDisplay(this.endDate)}`;
        },
        
        get startCalendarDays() {
            return this.generateCalendarDays(this.startDate || new Date());
        },
        
        get endCalendarDays() {
            return this.generateCalendarDays(this.endDate || new Date());
        },
        
        generateCalendarDays(baseDate) {
            const date = new Date(baseDate);
            const month = date.getMonth();
            const year = date.getFullYear();
            
            // Get first day of month
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            
            const days = [];
            const today = new Date();
            
            // Add previous month's days
            for (let i = 0; i < firstDay.getDay(); i++) {
                const prevDate = new Date(year, month, -i);
                days.unshift({
                    date: this.formatDate(prevDate),
                    dayOfMonth: prevDate.getDate(),
                    disabled: true
                });
            }
            
            // Add current month's days
            for (let i = 1; i <= lastDay.getDate(); i++) {
                const currentDate = new Date(year, month, i);
                days.push({
                    date: this.formatDate(currentDate),
                    dayOfMonth: i,
                    disabled: false,
                    isToday: this.formatDate(currentDate) === this.formatDate(today)
                });
            }
            
            // Add next month's days
            const remainingDays = 42 - days.length; // 6 rows * 7 days
            for (let i = 1; i <= remainingDays; i++) {
                const nextDate = new Date(year, month + 1, i);
                days.push({
                    date: this.formatDate(nextDate),
                    dayOfMonth: nextDate.getDate(),
                    disabled: true
                });
            }
            
            return days;
        },
        
        selectDate(type, day) {
            if (day.disabled) return;
            
            if (type === 'start') {
                this.startDate = day.date;
                if (this.endDate && new Date(this.startDate) > new Date(this.endDate)) {
                    this.endDate = null;
                }
            } else {
                if (!this.startDate || new Date(day.date) < new Date(this.startDate)) {
                    this.startDate = day.date;
                    this.endDate = null;
                } else {
                    this.endDate = day.date;
                }
            }
            
            this.dispatchDateChange();
        },
        
        selectPreset(preset) {
            const end = new Date();
            const start = new Date();
            
            switch (preset) {
                case 'last7':
                    start.setDate(start.getDate() - 7);
                    break;
                case 'last30':
                    start.setDate(start.getDate() - 30);
                    break;
                case 'thisMonth':
                    start.setDate(1);
                    break;
            }
            
            this.startDate = this.formatDate(start);
            this.endDate = this.formatDate(end);
            this.isOpen = false;
            
            this.dispatchDateChange();
        },
        
        isSelectedStart(day) {
            return day.date === this.startDate;
        },
        
        isSelectedEnd(day) {
            return day.date === this.endDate;
        },
        
        formatDate(date) {
            return date.toISOString().split('T')[0];
        },
        
        formatDateForDisplay(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('tr-TR', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },
        
        dispatchDateChange() {
            const event = new CustomEvent('datechange', {
                detail: {
                    startDate: this.startDate,
                    endDate: this.endDate
                }
            });
            window.dispatchEvent(event);
        }
    };
}
