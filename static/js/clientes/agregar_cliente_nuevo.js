document.addEventListener('DOMContentLoaded', function() {
    const formCliente = document.querySelector('#cliente-form');

    formCliente.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita el envío tradicional del formulario

        // Verifica si el formulario es válido
        if (formCliente.checkValidity()) {
            // Obtén los datos del formulario
            const formData = new FormData(formCliente);
            const data = Object.fromEntries(formData.entries());

            // Enviar datos al backend usando fetch
            fetch('/agregar_clientes_nuevos/guardar_cliente', {
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
                    alert(data.message);
                    formCliente.reset();
                } else {
                    alert('Error al agregar cliente: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ocurrió un error al enviar los datos');
            });
        } else {
            // Manejo si el formulario no es válido
            formCliente.reportValidity(); // Muestra los errores de validación
        }
    });
});