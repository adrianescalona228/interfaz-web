document.getElementById('buscador-inventario').addEventListener('input', function () {
    let filtro = this.value.toLowerCase(); // Obtener el valor de búsqueda y convertirlo a minúsculas
    let filasProductos = document.querySelectorAll('.table-row-body'); // Seleccionar todas las filas de productos

    filasProductos.forEach(function (fila) { // Iterar sobre cada fila
        let productoNombre = fila.querySelector('td.producto').textContent.toLowerCase(); // Obtener el nombre del producto y convertirlo a minúsculas

        // Mostrar u ocultar la fila basada en si el nombre del producto incluye el filtro
        if (productoNombre.includes(filtro)) {
            fila.style.display = ''; // Mostrar la fila
        } else {
            fila.style.display = 'none'; // Ocultar la fila
        }
    });
});
