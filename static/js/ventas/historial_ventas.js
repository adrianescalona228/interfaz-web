// historial_ventas.js
document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar todos los botones de crear nota de entrega
    document.querySelectorAll('.crear-nota-entrega').forEach(button => {
        button.addEventListener('click', () => {
            const numeroVenta = button.getAttribute('data-venta-id');

            // Envío del número de venta al servidor con fetch
            fetch('/historial_ventas/generar_nota_entrega', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ numero_venta: numeroVenta })
            })
            .then(response => {
                if (response.ok) {
                    console.log('Nota de entrega creada correctamente')
                    // Aquí podrías redirigir a una página de confirmación o mostrar más información
                } else {
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al crear la nota de entrega.');
            });
        });
    });
});
    
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
        const nombreCliente = this.closest('section').querySelector('tbody td:nth-child(2)').textContent.trim();
        eliminarVenta(ventaId, nombreCliente);
    });
});

function eliminarVenta(ventaId, nombreCliente) {
    // Aquí puedes implementar la lógica para enviar la solicitud al backend
    fetch(`/historial_ventas/eliminar_venta/${ventaId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            '_method': 'DELETE',
            'cliente': nombreCliente
        })
    })
    .then(response => {
        if (response.ok) {
            // Mostrar alerta con el número de venta eliminado
            alert(`Venta #${ventaId} eliminada correctamente.`);
            // Aquí puedes quitar la venta del DOM o hacer un reload
            location.reload();
        } else {
            // Manejo de errores
            console.error('Error al eliminar la venta');
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

$(document).ready(function() {
    $('.cliente').on('click', function() {
        // Selecciona la fila siguiente (que contiene la tabla de productos)
        $(this).closest('tr').next('.info-productos').toggle();
    });
});