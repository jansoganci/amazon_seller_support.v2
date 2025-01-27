class ChartFactory {
    constructor() {
        this.charts = {};
        this.chartConfigs = {
            revenueTrend: {
                type: 'line',
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return `$${context.parsed.y.toFixed(2)}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value;
                                }
                            }
                        }
                    }
                }
            },
            conversionRate: {
                type: 'line',
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return `${(context.parsed.y * 100).toFixed(2)}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return (value * 100).toFixed(1) + '%';
                                }
                            }
                        }
                    }
                }
            },
            unitsOrdered: {
                type: 'bar',
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            },
            sessions: {
                type: 'line',
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            }
        };
    }

    createChart(chartId, data) {
        const canvas = document.getElementById(chartId + 'Chart');
        if (!canvas) {
            console.error(`Canvas element not found for chart: ${chartId}`);
            return;
        }

        const config = this.chartConfigs[chartId];
        if (!config) {
            console.error(`Chart configuration not found for: ${chartId}`);
            return;
        }

        const chartData = {
            labels: data.labels,
            datasets: [{
                data: data.values,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                tension: 0.1
            }]
        };

        this.charts[chartId] = new Chart(canvas, {
            type: config.type,
            data: chartData,
            options: config.options
        });
    }

    updateChart(chartId, data) {
        const chart = this.charts[chartId];
        if (!chart) {
            this.createChart(chartId, data);
            return;
        }

        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.values;
        chart.update();
    }

    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }
} 