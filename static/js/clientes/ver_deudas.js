$(document).ready(function() {
    function calcularTotalDeuda() {
        var totalDeuda = 0;
        $('table tbody tr').each(function() {
            var monto = parseFloat($(this).find('.monto').text().replace('$', '').trim());
            if (!isNaN(monto)) {
                totalDeuda += monto;
            }
        });
        $('#valor_total_deuda').text('$' + totalDeuda.toFixed(2));
    }

    // Llama a la función para calcular el total de deuda cuando la página carga
    calcularTotalDeuda();

    document.getElementById('buscador-deuda').addEventListener('input', function () {
        let filtro = this.value.toLowerCase(); // Obtener el valor de búsqueda y convertirlo a minúsculas
        let filasDeudas = document.querySelectorAll('.table-row-body-deudas'); // Seleccionar todas las filas de productos

        filasDeudas.forEach(function (fila) { // Iterar sobre cada fila
            let nombreCliente = fila.querySelector('td.cliente').textContent.toLowerCase(); // Obtener el nombre del producto y convertirlo a minúsculas

            // Mostrar u ocultar la fila basada en si el nombre del producto incluye el filtro
            if (nombreCliente.includes(filtro)) {
                fila.style.display = ''; // Mostrar la fila
            } else {
                fila.style.display = 'none'; // Ocultar la fila
            }
        });

        // Volver a calcular el total después de filtrar
        calcularTotalDeuda();
    });

    let originalText = '';  // Variable para almacenar el valor original
    let previousText = '';  // Variable para almacenar el valor previo al cambio
    let targetElement = null;  // Elemento objetivo que se está editando

    function handleUndo(event) {
        if (event.key === 'z' && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
    
            fetch('/ver_deudas/rollback_deuda', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Rollback exitoso:', data.message);
    
                    // Sobrescribir el valor en el elemento objetivo con el valor previo
                    if (targetElement) {
                        targetElement.innerHTML = previousText;
                        // Actualizar el total de deuda después del rollback
                        calcularTotalDeuda();
                    }
                } else {
                    console.error('Error al realizar el rollback:', data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
            calcularTotalDeuda(); // Recalcular el total después de la actualización
        }
    };

    function simulateTabKey() {
        const event = new KeyboardEvent('keydown', { key: 'Tab', keyCode: 9, code: 'Tab', which: 9 });
        document.dispatchEvent(event);
    }

    document.addEventListener('keydown', handleUndo);  // Escuchar `Ctrl + Z` a nivel de documento

    const table = document.querySelector('.tabla-deudas');

    table.addEventListener('dblclick', function(event) {
        const target = event.target;

        if (target.classList.contains('editable')) {
            originalText = target.textContent.trim();  // Almacenar el valor original
            previousText = originalText;  // También se almacena como previo para posible deshacer
            targetElement = target;  // Almacenar el elemento actual para referencia en "deshacer"

            const input = document.createElement('input');
            input.type = 'text';
            input.value = originalText;
            target.innerHTML = ''; // Limpiar el contenido
            target.appendChild(input);
            input.focus();
            input.select();

            // Evento para manejar la tecla Enter
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const newValue = input.value.trim();

                    if (newValue !== originalText) {
                        previousText = originalText;  // Actualiza el valor previo
                        originalText = newValue;  // Nuevo valor se convierte en el original
                    }

                    target.innerHTML = newValue;

                    const row = target.closest('tr');
                    const nombre = row.dataset.nombre;

                    // Enviar los datos al backend
                    fetch('/ver_deudas/actualizar_deuda', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            nombre: nombre,
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

                targetElement = target; // Mantén referencia para posible deshacer
                // Forzar el enfoque en el documento
                // Simular la tecla Tab después de un pequeño retraso
                setTimeout(simulateTabKey, 50);
                // Recalcular el total después de la actualización
                calcularTotalDeuda();
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
