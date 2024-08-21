// $(document).ready(function () {
//     autocompletar_clientes();
// });

// function autocompletar_clientes() {
//     $('#buscador').autocomplete({
//         source: '/nueva_venta/autocompletar_clientes',
//         minLength: 1 // El autocompletado comenzará después de escribir 2 caracteres
//     });
// }

document.getElementById('buscador').addEventListener('input', function () {
    let filtro = this.value.toLowerCase();
    let contenedoresVentas = document.querySelectorAll('.contenedor');

    contenedoresVentas.forEach(function (contenedor) {
        let numeroVenta = contenedor.querySelector('tbody td:nth-child(1)').textContent.toLowerCase();
        let nombreCliente = contenedor.querySelector('tbody td:nth-child(2)').textContent.toLowerCase();

        if (numeroVenta.includes(filtro) || nombreCliente.includes(filtro)) {
            contenedor.style.display = '';
        } else {
            contenedor.style.display = 'none';
        }
    });
});

document.getElementById('mostrar_facturas_vencidas').addEventListener('click', function() {
    let today = new Date().toISOString().split('T')[0];
    let contenedoresVentas = document.querySelectorAll('.contenedor');

    contenedoresVentas.forEach(function(contenedor) {
        let fechaVencimiento = contenedor.querySelector('tbody td:nth-child(4)').textContent.trim();

        // Comparar las fechas
        if (fechaVencimiento && fechaVencimiento < today) {
            contenedor.style.display = ''; // Mostrar si está vencida
        } else {
            contenedor.style.display = 'none'; // Ocultar si no está vencida
        }
    });
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
