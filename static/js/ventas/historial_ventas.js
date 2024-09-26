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
    let contenedoresVentas = document.querySelectorAll('.ventas-principal tbody tr:not(.info-productos)');

    contenedoresVentas.forEach(function (contenedor) {
        let numeroVentaCelda = contenedor.querySelector('tbody td:nth-child(1)');
        let nombreClienteCelda = contenedor.querySelector('tbody td:nth-child(2)');
        let estadoCelda = contenedor.querySelector('tbody td:nth-child(5)');
        
        // Comprobaciones de existencia
        if (numeroVentaCelda && nombreClienteCelda && estadoCelda) {
            let numeroVenta = numeroVentaCelda.textContent.toLowerCase();
            let nombreCliente = nombreClienteCelda.textContent.toLowerCase();
            let estado = estadoCelda.textContent.trim();

            let mostrar = numeroVenta.includes(filtro) || nombreCliente.includes(filtro);

            contenedor.style.display = mostrar ? '' : 'none';
        }
    });
});

// Ejemplo de cómo activar el filtro de vencimiento
document.getElementById('mostrar_facturas_vencidas').addEventListener('click', function () {
    filtroActivo = !filtroActivo; // Alternar el estado del filtro
    this.textContent = filtroActivo ? 'Mostrar Todas las Facturas' : 'Mostrar Facturas Vencidas'; // Cambiar el texto del botón
    document.getElementById('buscador').dispatchEvent(new Event('input')); // Disparar el evento de entrada para actualizar la búsqueda
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