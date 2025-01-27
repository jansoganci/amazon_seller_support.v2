const ChartFactory = {
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)'
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                    color: document.documentElement.classList.contains('dark') ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)'
                }
            }
        }
    },

    createChart(type, context, config) {
        const options = {
            ...this.defaultOptions,
            scales: {
                ...this.defaultOptions.scales,
                y: {
                    ...this.defaultOptions.scales.y,
                    ticks: {
                        ...this.defaultOptions.scales.y.ticks,
                        callback: function(value) {
                            switch(config.valueType) {
                                case 'currency':
                                    return '$' + value.toLocaleString('en-US', {
                                        minimumFractionDigits: 0,
                                        maximumFractionDigits: 0
                                    });
                                case 'percentage':
                                    return value.toFixed(2) + '%';
                                default:
                                    return value.toLocaleString('en-US');
                            }
                        }
                    }
                }
            }
        };

        return new Chart(context, {
            type: type || 'line',
            data: {
                labels: [],
                datasets: [{
                    label: config.label,
                    data: [],
                    borderColor: config.color,
                    backgroundColor: config.bgColor,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: options
        });
    }
}; 