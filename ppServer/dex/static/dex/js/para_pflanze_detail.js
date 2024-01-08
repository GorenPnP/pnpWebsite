const ecology = JSON.parse(document.querySelector("#ecology").innerHTML);
const colors = {
    ph: "#2ac206",
    temperatur: "#f55f5f",
    licht: "#ffd33a",
    wasser: "#3a66ff",
}

for (const [label, data] of Object.entries(ecology)) {

    const selector = `#chart--${label.toLowerCase()}`;
    new Chart(document.querySelector(selector), {
        type: 'line',
        data: {
            labels: data.map(e => e.x),
            datasets: [
                {
                    label,
                    data: data.map(e => e.y),
                    fill: true,
                    borderColor: colors[label.toLowerCase()],
                    tension: .4
                }
            ]
        },
        options: {
            scales: {
                y: {
                    title: {
                        display: true,
                        text: "Wachstum (in %)"
                    },
                    beginAtZero: true,
                    type: "linear"
                },
                x: {
                    type: "linear",
                }
            }
        },
    });
}