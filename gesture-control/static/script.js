
const ctx = document.getElementById('protocolChart').getContext('2d');
const protocolChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: [],
        datasets: [{
            label: 'Protocol Distribution',
            data: [],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});

async function fetchData() {
    console.log("Fetching data...");
    const response = await fetch('/data');
    const data = await response.json();
    console.log("Data received:", data);
    protocolChart.data.labels = Object.keys(data);
    protocolChart.data.datasets[0].data = Object.values(data);
    protocolChart.update();
}

setInterval(fetchData, 1000);
