document.getElementById('buscador').addEventListener('input', function () {
    let filtro = this.value.toLowerCase();
    let contenedoresCompras = document.querySelectorAll('.contenedor');

    contenedoresCompras.forEach(function (contenedor) {
        let numeroVenta = contenedor.querySelector('tbody td:nth-child(1)').textContent.toLowerCase();
        let nombreProveedor = contenedor.querySelector('tbody td:nth-child(2)').textContent.toLowerCase();

        if (numeroVenta.includes(filtro) || nombreProveedor.includes(filtro)) {
            contenedor.style.display = '';
        } else {
            contenedor.style.display = 'none';
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
