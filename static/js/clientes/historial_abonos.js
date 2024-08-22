document.getElementById('buscador-abonos').addEventListener('input', function () {
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

document.querySelectorAll('.eliminar-abono').forEach(button => {
    button.addEventListener('click', function() {
        const abonoId = this.getAttribute('data-abono-id');
        eliminarAbono(this, abonoId);  // Pasar 'this' como referencia
    });
});

function eliminarAbono(button, abonoId) {
    // Enviar solicitud al backend para eliminar el abono
    fetch(`/historial_abonos/eliminar_abono/${abonoId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: '_method=DELETE'
    })
    .then(response => {
        if (response.ok) {
            // Usar la referencia pasada para eliminar el abono del DOM
            button.closest('.table-row-body-deudas').remove();
            alert('Abono eliminado correctamente.');
        } else {
            alert('Hubo un error al eliminar el abono.');
        }
    });
}
