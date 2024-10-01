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
        let numeroVentaCell = contenedor.querySelector('td:nth-child(1)');
        let nombreClienteCell = contenedor.querySelector('td:nth-child(2)');
        let estadoCell = contenedor.querySelector('td:nth-child(5)');

        // Aquí accedemos a la fecha de vencimiento de una forma diferente
        let fechaVencimientoCell = contenedor.querySelector('td:nth-child(6)'); // sigue existiendo
        let fechaVencimiento = fechaVencimientoCell ? fechaVencimientoCell.textContent.trim() : null;

        // Comprobaciones para evitar null
        if (numeroVentaCell && nombreClienteCell && estadoCell && fechaVencimiento) {
            let numeroVenta = numeroVentaCell.textContent.toLowerCase();
            let nombreCliente = nombreClienteCell.textContent.toLowerCase();
            let estado = estadoCell.textContent.trim().toUpperCase(); // Estado

            let hoy = new Date().toISOString().split('T')[0]; // Fecha actual

            // Lógica para mostrar
            let mostrar = numeroVenta.includes(filtro) || nombreCliente.includes(filtro);

            if (filtroActivo) {
                // Si el filtro de vencimiento está activo, verificamos también la fecha y el estado
                mostrar = mostrar && (estado === 'PENDIENTE') && (fechaVencimiento && fechaVencimiento < hoy);
            }

            // Mostrar u ocultar la fila de la venta
            contenedor.style.display = mostrar ? '' : 'none';
        } else {
            // Si alguno de los elementos es null, ocultar la fila
            contenedor.style.display = 'none';
        }

    });
});

// document.getElementById('buscador').addEventListener('input', function () {
//     let filtro = this.value.toLowerCase();
//     let contenedoresVentas = document.querySelectorAll('.ventas-principal tbody tr:not(.info-productos)');

//     contenedoresVentas.forEach(function (contenedor) {
//         let numeroVentaCelda = contenedor.querySelector('tbody td:nth-child(1)');
//         let nombreClienteCelda = contenedor.querySelector('tbody td:nth-child(2)');
//         let estadoCelda = contenedor.querySelector('tbody td:nth-child(5)');
        
//         // Comprobaciones de existencia
//         if (numeroVentaCelda && nombreClienteCelda && estadoCelda) {
//             let numeroVenta = numeroVentaCelda.textContent.toLowerCase();
//             let nombreCliente = nombreClienteCelda.textContent.toLowerCase();
//             let estado = estadoCelda.textContent.trim();

//             let mostrar = numeroVenta.includes(filtro) || nombreCliente.includes(filtro);

//             contenedor.style.display = mostrar ? '' : 'none';
//         }
//     });
// });

// Ejemplo de cómo activar el filtro de vencimiento
document.getElementById('mostrar_facturas_vencidas').addEventListener('click', function () {
    filtroActivo = !filtroActivo; // Alternar el estado del filtro
    this.textContent = filtroActivo ? 'Mostrar Todas las Facturas' : 'Mostrar Facturas Vencidas'; // Cambiar el texto del botón
    document.getElementById('buscador').dispatchEvent(new Event('input')); // Disparar el evento de entrada para actualizar la búsqueda
});

document.querySelectorAll('.eliminar-venta').forEach(button => {
    button.addEventListener('click', function() {
        console.log('hola');

        const ventaId = this.getAttribute('data-venta-id');
        const fila = this.closest('tr');  // Obtener la fila <tr> más cercana
        console.log('Fila encontrada:', fila);

        if (fila) {
            const nombreClienteElement = fila.querySelector('td:nth-child(2)');  // Buscar el segundo <td> dentro de la fila
            console.log('Elemento del nombre del cliente:', nombreClienteElement);

            if (nombreClienteElement) {
                const nombreCliente = nombreClienteElement.textContent.trim();  // Obtener el texto del cliente
                eliminarVenta(ventaId, nombreCliente);
            } else {
                console.error('No se encontró el <td> con el nombre del cliente');
            }
        } else {
            console.error('No se encontró la fila <tr> más cercana');
        }
    });
});


function eliminarVenta(ventaId, nombreCliente) {
    // console.log('hola')
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

$('.cliente').on('click', function() {
    // Selecciona la fila siguiente (que contiene la tabla de productos)
    var $infoProductos = $(this).closest('tr').next('.info-productos');

    // Comprobar si la fila de productos está visible
    if ($infoProductos.is(':visible')) {
        // Si está visible, ocultamos todos los hijos
        $infoProductos.hide(); // Oculta la fila de productos
    } else {
        // Si está oculta, mostramos la fila
        $infoProductos.show(); // Muestra la fila de productos
        
        // Opcional: Mostrar todos los elementos hijos dentro de la fila
        $infoProductos.find('*').each(function() {
            $(this).css('display', ''); // Restablece el display a su valor predeterminado
        });
    }
});
