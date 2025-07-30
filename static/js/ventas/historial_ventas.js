// historial_ventas.js
// Esto va a estar comentado por ahora, luego se volvera a integrar
//document.addEventListener('DOMContentLoaded', () => {
//    // Seleccionar todos los botones de crear nota de entrega
//    document.querySelectorAll('.crear-nota-entrega').forEach(button => {
//        button.addEventListener('click', () => {
//            const numeroVenta = button.getAttribute('data-venta-id');
//
//            // Envío del número de venta al servidor con fetch
//            fetch('/historial_ventas/generar_nota_entrega', {
//                method: 'POST',
//                headers: {
//                    'Content-Type': 'application/json'
//                },
//                body: JSON.stringify({ numero_venta: numeroVenta })
//            })
//            .then(response => {
//                if (response.ok) {
//                    console.log('Nota de entrega creada correctamente')
//                    // Aquí podrías redirigir a una página de confirmación o mostrar más información
//                } else {
//                }
//            })
//            .catch(error => {
//                console.error('Error:', error);
//                alert('Error al crear la nota de entrega.');
//            });
//        });
//    });
//});

let filtroActivo = false; // Estado del filtro

document.getElementById('search-input').addEventListener('input', function () {
    let filtro = this.value.toLowerCase();
    let contenedoresVentas = document.querySelectorAll('.main-sales-table tbody tr:not(.products-info)');

    contenedoresVentas.forEach(function (contenedor) {
        let numeroVentaCell = contenedor.querySelector('td:nth-child(1)');
        let nombreClienteCell = contenedor.querySelector('td:nth-child(2)');
        let estadoCell = contenedor.querySelector('td:nth-child(5)');
        let fechaVencimientoCell = contenedor.querySelector('td:nth-child(6)'); // due date oculto
        let fechaVencimiento = fechaVencimientoCell ? fechaVencimientoCell.textContent.trim() : null;

        if (numeroVentaCell && nombreClienteCell && estadoCell) {
            let numeroVenta = numeroVentaCell.textContent.toLowerCase();
            let nombreCliente = nombreClienteCell.textContent.toLowerCase();
            let estado = estadoCell.textContent.trim().toUpperCase();

            let hoy = new Date().toISOString().split('T')[0];

            let mostrar = numeroVenta.includes(filtro) || nombreCliente.includes(filtro);

            if (filtroActivo) {
                mostrar = mostrar && estado === 'PENDIENTE' && fechaVencimiento && fechaVencimiento < hoy;
            }

            contenedor.style.display = mostrar ? '' : 'none';
        } else {
            contenedor.style.display = 'none';
        }
    });
});

document.getElementById('show-overdue-invoices').addEventListener('click', function () {
    filtroActivo = !filtroActivo;
    this.textContent = filtroActivo ? 'Show All Invoices' : 'Show Overdue Invoices';
    document.getElementById('search-input').dispatchEvent(new Event('input'));
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
    fetch(`/sales_history/delete_sale/${ventaId}`, {
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
        fetch(`/sales_history/remove_product/${ventaId}/${productoId}`, {
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

$(document).on('click', '.client-name', function() {
    console.log("click detectado en client-name");
    var $infoProductos = $(this).closest('tr').next('.products-info');

    if ($infoProductos.is(':visible')) {
        $infoProductos.hide();
    } else {
        $infoProductos.show();
        $infoProductos.find('*').css('display', '');
    }
});

$(document).ready(function() {
    $('.monto-pagado-container').on('dblclick', function() {
        const $container = $(this);
        const $texto = $container.find('.monto-pagado-texto');
        const montoPagado = parseFloat($texto.text());
        const totalVenta = parseFloat($container.text().split('/')[1]);

        const $input = $('<input type="number" class="monto-pagado-input">');
        $input.val(montoPagado);
        $texto.replaceWith($input);
        $input.focus();

        // Evento para detectar la tecla "Enter"
        $input.on('keypress', function(event) {
            if (event.which === 13) { // 13 es el código de la tecla "Enter"
                $input.blur(); // Simula un "blur" para finalizar la edición
            }
        });

        $input.on('blur', function() {
            let nuevoMontoPagado = parseFloat($input.val());

            if (isNaN(nuevoMontoPagado) || nuevoMontoPagado < 0) {
                alert('Por favor, ingrese un número válido.');
                nuevoMontoPagado = montoPagado;
            } else if (nuevoMontoPagado > totalVenta) {
                alert('El monto pagado no puede ser mayor que el total de la venta.');
                nuevoMontoPagado = montoPagado;
            }

            // Enviar al servidor con fetch
            $.ajax({
                url: '/sales_history/update_paid_amount',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    numero_venta: $(this).closest('tr').find('td:first-child').text(),
                    monto_pagado: nuevoMontoPagado
                }),
                success: function(response) {
                    console.log('Monto pagado actualizado correctamente:', response);
                    $input.replaceWith(`<span class="monto-pagado-texto">${nuevoMontoPagado}</span>`);
                },
                error: function(error) {
                    console.error('Error al actualizar el monto pagado:', error);
                    alert('Error al actualizar el monto pagado.');
                    $input.replaceWith(`<span class="monto-pagado-texto">${montoPagado}</span>`);
                }
            });
        });
    });
});
