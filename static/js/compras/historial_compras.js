document.getElementById('buscador').addEventListener('input', function () {
    let filtro = this.value.toLowerCase();
    let filasCompras = document.querySelectorAll('.compras-principal tbody tr:not(.info-productos)'); // Seleccionamos las filas principales de compras

    filasCompras.forEach(function (fila) {
        let numeroCompraCell = fila.querySelector('td:nth-child(1)'); // Nro. de compra
        let nombreProveedorCell = fila.querySelector('td:nth-child(2)'); // Proveedor

        // Comprobaciones para evitar null
        if (numeroCompraCell && nombreProveedorCell) {
            let numeroCompra = numeroCompraCell.textContent.toLowerCase();
            let nombreProveedor = nombreProveedorCell.textContent.toLowerCase();

            // Lógica para mostrar
            let mostrar = numeroCompra.includes(filtro) || nombreProveedor.includes(filtro);

            // Mostrar u ocultar la fila de la compra
            fila.style.display = mostrar ? '' : 'none';
        }
    });
});

document.querySelectorAll('.eliminar-compra').forEach(button => {
    button.addEventListener('click', function() {
        const compraId = this.getAttribute('data-compra-id');
        eliminarCompra(this, compraId);  // Pasar 'this' como referencia
    });
});

function eliminarCompra(button, compraId) {
    // Enviar solicitud al backend para eliminar la compra
    fetch(`/historial_compras/eliminar_compra/${compraId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: '_method=DELETE'
    })
    .then(response => {
        if (response.ok) {
            // Usar la referencia pasada para eliminar la compra del DOM
            button.closest('.contenedor').remove();
            alert('Compra eliminada correctamente.');
        } else {
            alert('Hubo un error al eliminar la compra.');
        }
    });
}


document.querySelectorAll('.eliminar-producto').forEach(button => {
    button.addEventListener('click', function() {
        const compraId = this.getAttribute('data-compra-id');
        const productoId = this.getAttribute('data-producto-id');

        console.log('hola')
        console.log(productoId)

        // Enviar solicitud para eliminar el producto de la compra
        fetch(`/historial_compras/eliminar_producto/${compraId}/${productoId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: '_method=DELETE'
        })
        .then(response => {
            if (response.ok) {
                // Eliminar el producto del DOM
                this.closest('tr').remove();
                alert('Producto eliminado correctamente.');
            } else {
                alert('Hubo un error al eliminar el producto.');
            }
        });
    });
});

$('.proveedor').on('click', function() {
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
