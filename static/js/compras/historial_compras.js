document.getElementById('search-bar').addEventListener('input', function () {
    let filtro = this.value.toLowerCase();
    let filasCompras = document.querySelectorAll('.purchase-history-table tbody tr:not(.product-details-row)');

    filasCompras.forEach(function (fila) {
        let numeroCompraCell = fila.querySelector('td:nth-child(1)');
        let nombreProveedorCell = fila.querySelector('td:nth-child(2)');

        if (numeroCompraCell && nombreProveedorCell) {
            let numeroCompra = numeroCompraCell.textContent.toLowerCase();
            let nombreProveedor = nombreProveedorCell.textContent.toLowerCase();

            let mostrar = numeroCompra.includes(filtro) || nombreProveedor.includes(filtro);

            fila.style.display = mostrar ? '' : 'none';

            // Solo mostrar la fila de detalles si también está abierta (tiene clase 'abierta')
            let filaDetalles = fila.nextElementSibling;
            if (filaDetalles && filaDetalles.classList.contains('product-details-row')) {
                if (mostrar && filaDetalles.classList.contains('abierta')) {
                    filaDetalles.style.display = '';
                } else {
                    filaDetalles.style.display = 'none';
                }
            }
        }
    });
});



// Eliminar compra
document.querySelectorAll('.delete-purchase').forEach(button => {
    button.addEventListener('click', function () {
        const compraId = this.getAttribute('data-purchase-id');
        eliminarCompra(this, compraId);
    });
});

function eliminarCompra(button, compraId) {
    if (!confirm(`¿Eliminar compra #${compraId}?`)) return;

    fetch(`/purchase_history/delete_purchase/${compraId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: '_method=DELETE'
    })
    .then(response => {
        if (response.ok) {
            const filaCompra = button.closest('tr');
            const filaDetalles = filaCompra.nextElementSibling;

            filaCompra.remove();
            if (filaDetalles && filaDetalles.classList.contains('product-details-row')) {
                filaDetalles.remove();
            }

            alert('Compra eliminada correctamente.');
        } else {
            alert('Hubo un error al eliminar la compra.');
        }
    })
    .catch(error => {
        console.error('Error al eliminar:', error);
        alert('Hubo un error al conectar con el servidor.');
    });
}

// Eliminar producto
document.querySelectorAll('.delete-product').forEach(button => {
    button.addEventListener('click', function () {
        const compraId = this.getAttribute('data-purchase-id');
        const productoId = this.getAttribute('data-product-id');

        if (!confirm(`¿Eliminar producto #${productoId} de la compra #${compraId}?`)) return;

        fetch(`/purchase_history/delete_product/${compraId}/${productoId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: '_method=DELETE'
        })
        .then(response => {
            if (response.ok) {
                this.closest('tr').remove();
                alert('Producto eliminado correctamente.');
            } else {
                alert('Hubo un error al eliminar el producto.');
            }
        })
        .catch(error => {
            console.error('Error al eliminar producto:', error);
            alert('Hubo un error al conectar con el servidor.');
        });
    });
});

document.querySelectorAll('.supplier-name').forEach(cell => {
    cell.addEventListener('click', function () {
        const filaCompra = this.closest('tr');
        const filaDetalles = filaCompra.nextElementSibling;

        if (filaDetalles && filaDetalles.classList.contains('product-details-row')) {
            const estabaAbierta = filaDetalles.classList.contains('abierta');

            // Cierra cualquier otra fila abierta si quieres comportamiento exclusivo
            // document.querySelectorAll('.product-details-row.abierta').forEach(f => {
            //     f.classList.remove('abierta');
            //     f.style.display = 'none';
            // });

            if (estabaAbierta) {
                filaDetalles.classList.remove('abierta');
                filaDetalles.style.display = 'none';
            } else {
                filaDetalles.classList.add('abierta');
                filaDetalles.style.display = '';
            }
        }
    });
});

