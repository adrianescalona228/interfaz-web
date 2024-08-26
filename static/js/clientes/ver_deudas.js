$(document).ready(function() {
    function calcularTotalDeuda() {
        var totalDeuda = 0;
        $('table tbody tr').each(function() {
            var monto = parseFloat($(this).find('.monto').text());
            if (!isNaN(monto)) {
                totalDeuda += monto;
            }
        });
        $('#valor_total_deuda').text('$' + totalDeuda.toFixed(2));
    }
    
    // Llama a la función para calcular el total de deuda cuando la página carga
    calcularTotalDeuda();
});

document.getElementById('buscador-deuda').addEventListener('input', function () {
    let filtro = this.value.toLowerCase(); // Obtener el valor de búsqueda y convertirlo a minúsculas
    let filasDeudas = document.querySelectorAll('.table-row-body-deudas'); // Seleccionar todas las filas de productos

    filasDeudas.forEach(function (filasDeudas) { // Iterar sobre cada fila
        let nombreCliente = filasDeudas.querySelector('td.nombre-cliente').textContent.toLowerCase(); // Obtener el nombre del producto y convertirlo a minúsculas

        // Mostrar u ocultar la fila basada en si el nombre del producto incluye el filtro
        if (nombreCliente.includes(filtro)) {
            filasDeudas.style.display = ''; // Mostrar la fila
        } else {
            filasDeudas.style.display = 'none'; // Ocultar la fila
        }
    });
});