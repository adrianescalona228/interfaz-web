let miGraficaBarras;  // Variable para guardar la instancia de la gráfica de barras
let miGraficaLineas;  // Variable para guardar la instancia de la gráfica de líneas

document.addEventListener("DOMContentLoaded", function () {
    obtenerDatos();  // Llamar al cargar la página
});

function obtenerDatos() {
    let rango = document.getElementById('rango').value;
    let categoria = document.getElementById('categoria').value;

    let url = `/graficas?rango=${rango}`;
    if (categoria) {
        url += `&categoria=${categoria}`;
    }

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error en la respuesta del servidor");
            }
            return response.json();
        })
        .then(data => {
            console.log(data);

            // Obtener los datos para las gráficas
            let productos = data.total_vendidos.map(item => item.PRODUCTO);
            let totalesVendidos = data.total_vendidos.map(item => item.total_vendido);
            let fechas = data.ventas_tiempo.map(item => item.fecha);
            let ventasTotales = data.ventas_tiempo.map(item => item.total_ventas);

            // Generar la gráfica de barras para los productos vendidos
            generarGraficaBarras(productos, totalesVendidos);

            // Generar la gráfica de líneas para las ventas a lo largo del tiempo
            generarGraficaLineas(fechas, ventasTotales);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function generarGraficaBarras(productos, totalesVendidos) {
    const filteredData = productos.reduce((acc, producto, index) => {
        if (totalesVendidos[index] > 0) {
            acc.productos.push(producto);
            acc.totalesVendidos.push(totalesVendidos[index]);
        }
        return acc;
    }, { productos: [], totalesVendidos: [] });

    if (filteredData.productos.length === 0) {
        alert('No hay datos para mostrar en la gráfica de barras.');
        return;
    }

    var ctx = document.getElementById('graficaVentasBarras').getContext('2d');

    if (miGraficaBarras) {
        miGraficaBarras.destroy();
    }

    miGraficaBarras = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filteredData.productos,
            datasets: [{
                label: 'Total Vendido',
                data: filteredData.totalesVendidos,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 0.5
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function generarGraficaLineas(fechas, ventasTotales) {
    if (ventasTotales.length === 0) {
        alert('No hay datos para mostrar en la gráfica de líneas.');
        return;
    }

    var ctx = document.getElementById('graficaVentasLineas').getContext('2d');

    if (miGraficaLineas) {
        miGraficaLineas.destroy();
    }

    miGraficaLineas = new Chart(ctx, {
        type: 'line',
        data: {
            labels: fechas,
            datasets: [{
                label: 'Ventas Totales',
                data: ventasTotales,
                fill: false,
                borderColor: 'rgba(153, 102, 255, 1)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
