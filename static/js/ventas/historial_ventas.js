// $(document).ready(function () {
//     autocompletar_clientes();
// });

// function autocompletar_clientes() {
//     $('#buscador').autocomplete({
//         source: '/nueva_venta/autocompletar_clientes',
//         minLength: 1 // El autocompletado comenzará después de escribir 2 caracteres
//     });
// }
let filtroActivo = false; // Variable para llevar el seguimiento del estado del filtro de vencimiento

document.getElementById('buscador').addEventListener('input', function () {
    let filtro = this.value.toLowerCase();
    let contenedoresVentas = document.querySelectorAll('.contenedor');

    contenedoresVentas.forEach(function (contenedor) {
        let numeroVenta = contenedor.querySelector('tbody td:nth-child(1)').textContent.toLowerCase();
        let nombreCliente = contenedor.querySelector('tbody td:nth-child(2)').textContent.toLowerCase();
        let fechaVencimiento = contenedor.querySelector('tbody td:nth-child(5)').textContent.trim();
        let estado = contenedor.querySelector('tbody td:nth-child(4)').textContent.trim(); // Ajusta según la columna de estado

        let mostrar = numeroVenta.includes(filtro) || nombreCliente.includes(filtro);

        if (filtroActivo) {
            // Si el filtro de vencimiento está activo, verificamos también la fecha y el estado
            mostrar = mostrar && fechaVencimiento && fechaVencimiento < new Date().toISOString().split('T')[0] && estado.toUpperCase() === 'PENDIENTE';
        }

        contenedor.style.display = mostrar ? '' : 'none';
    });
});

document.getElementById('mostrar_facturas_vencidas').addEventListener('click', function() {
    filtroActivo = !filtroActivo; // Alternar el estado del filtro de vencimiento

    let today = new Date().toISOString().split('T')[0];
    let contenedoresVentas = document.querySelectorAll('.contenedor');

    contenedoresVentas.forEach(function(contenedor) {
        let fechaVencimiento = contenedor.querySelector('tbody td:nth-child(5)').textContent.trim();
        let estado = contenedor.querySelector('tbody td:nth-child(4)').textContent.trim(); // Ajusta según la columna de estado

        let mostrar = true;

        if (filtroActivo) {
            // Si el filtro de vencimiento está activo, mostramos solo las facturas vencidas y pendientes
            mostrar = fechaVencimiento && fechaVencimiento < today && estado.toUpperCase() === 'PENDIENTE';
        }

        // Aplicar el filtro de búsqueda también
        let filtro = document.getElementById('buscador').value.toLowerCase();
        let numeroVenta = contenedor.querySelector('tbody td:nth-child(1)').textContent.toLowerCase();
        let nombreCliente = contenedor.querySelector('tbody td:nth-child(2)').textContent.toLowerCase();
        
        mostrar = mostrar && (numeroVenta.includes(filtro) || nombreCliente.includes(filtro));

        contenedor.style.display = mostrar ? '' : 'none';
    });

    this.textContent = filtroActivo ? 'Mostrar Todas las Facturas' : 'Mostrar Facturas Vencidas';
});

document.querySelectorAll('.eliminar-venta').forEach(button => {
    button.addEventListener('click', function() {
        const ventaId = this.getAttribute('data-venta-id');
        eliminarVenta(ventaId);
    });
});

function eliminarVenta(ventaId) {
    // Aquí puedes implementar la lógica para enviar la solicitud al backend
    fetch(`/historial_ventas/eliminar_venta/${ventaId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: '_method=DELETE'
    })
    .then(response => {
        if (response.ok) {
            // Opcional: puedes actualizar la página o eliminar el elemento de la lista

            // Aquí puedes quitar la venta del DOM o hacer un reload
            location.reload();
        } else {

        }
    });
}

document.querySelectorAll('.eliminar-producto').forEach(button => {
    button.addEventListener('click', function() {
        const ventaId = this.getAttribute('data-venta-id');
        const productoId = this.getAttribute('data-producto-id');

        // Enviar solicitud para eliminar producto
        fetch(`/historial_ventas/eliminar_producto/${ventaId}/${productoId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: '_method=DELETE'
        })
        .then(response => {
            if (response.ok) {
                // Opcional: Eliminar el producto del DOM
                this.closest('tr').remove();
                alert('Producto eliminado correctamente.');
            } else {
                alert('Hubo un error al eliminar el producto.');
            }
        });
    });
});
