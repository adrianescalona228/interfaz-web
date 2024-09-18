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

document.addEventListener('DOMContentLoaded', function() {
    const table = document.querySelector('.tabla-inventario');

    table.addEventListener('dblclick', function(event) {
        const target = event.target;

        if (target.classList.contains('editable')) {
            const originalText = target.textContent.trim();
            const input = document.createElement('input');
            input.type = 'text';
            input.value = originalText;
            target.innerHTML = ''; // Limpiar el contenido
            target.appendChild(input);
            input.focus();
            input.select();

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                const newValue = input.value.trim();
                target.innerHTML = newValue;

                const row = target.closest('tr');
                const id = row.dataset.id;
                const column = target.classList[1]; // Obtener la clase para identificar la columna

                // Enviar los datos al backend
                fetch('/ver_inventario/actualizar_producto', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        id: id,
                        column: column,
                        value: newValue
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Actualización exitosa:', data.message);
                    } else {
                        console.error('Error al actualizar:', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }});
            
            // Interceptar el evento blur y reenfocar el input
            input.addEventListener('blur', function(e) {
                e.preventDefault();
                input.focus();  // Reenfocar el input para evitar que pierda la selección
            });
        }
    });
});

