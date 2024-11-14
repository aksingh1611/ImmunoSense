document.addEventListener('DOMContentLoaded', function() {
    // Get the predictions data from Flask and convert it to an array
    var prediction = JSON.parse('{{ prediction | tojson | safe }}');
    
    // Extract dates and immunity index from predictions
    var dates = prediction.map(prediction => prediction.prediction_date);
    var immunityIndex = prediction.map(prediction => prediction.immunity_index);

    // Create a new Chart.js line chart
    var ctx = document.getElementById('immunityChart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Immunity Index',
                data: immunityIndex,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
