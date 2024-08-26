document.addEventListener('DOMContentLoaded', function() {
    const formInventario = document.querySelector('#producto-form');

    formInventario.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita el envío tradicional del formulario

        // Verifica si el formulario es válido
        if (formInventario.checkValidity()) {
            // Obtén los datos del formulario
            const formData = new FormData(formInventario);
            const data = Object.fromEntries(formData.entries());

            console.log(data)

            // Enviar datos al backend usando fetch
            fetch('/registrar_producto_nuevo/guardar_producto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Opcional: Vaciar el formulario
                    formInventario.reset();
                    console.log(data.message);
                } else {
                    alert('Error al agregar producto: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ocurrió un error al enviar los datos');
            });
        } else {
            // Manejo si el formulario no es válido
            formInventario.reportValidity(); // Muestra los errores de validación
        }
    });
});
