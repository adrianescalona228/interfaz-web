document.getElementById('buscador-cliente').addEventListener('input', function () {
    let filtro = this.value.toLowerCase(); // Obtener el valor de búsqueda y convertirlo a minúsculas
    let filasProductos = document.querySelectorAll('.table-row-body'); // Seleccionar todas las filas de productos

    filasProductos.forEach(function (fila) { // Iterar sobre cada fila
        let productoNombre = fila.querySelector('td.nombre').textContent.toLowerCase(); // Obtener el nombre del producto y convertirlo a minúsculas
        let direccion = fila.querySelector('td.direccion').textContent.toLowerCase(); // Obtener la dirección y convertirla a minúsculas

        // Mostrar u ocultar la fila basada en si el nombre del producto o la dirección incluye el filtro
        if (productoNombre.includes(filtro) || direccion.includes(filtro)) {
            fila.style.display = ''; // Mostrar la fila
        } else {
            fila.style.display = 'none'; // Ocultar la fila
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const table = document.querySelector('table'); // Seleccionamos la tabla de clientes

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

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    const newValue = input.value.trim();
                    target.innerHTML = newValue;

                    const row = target.closest('tr');
                    const id = row.dataset.id;  // Asegúrate de tener el ID en un atributo `data-id` en la fila
                    const column = target.classList[1]; // Obtener la clase para identificar la columna

                    // Enviar los datos al backend
                    fetch('/clients_list/update_client', {
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
                }
            });
            
            // Interceptar el evento blur y reenfocar el input
            input.addEventListener('blur', function(e) {
                e.preventDefault();
                input.focus();  // Reenfocar el input para evitar que pierda la selección
            });
        }
    });
});
