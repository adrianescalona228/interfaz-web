document.addEventListener('DOMContentLoaded', function() {
    console.log("JS cargado y ejecutándose");
    const formCliente = document.querySelector('#client-form');

    if (!formCliente) {
        console.error("No se encontró el formulario con id client-form");
        return;
    }

    formCliente.addEventListener('submit', function(event) {
        event.preventDefault();

        if (formCliente.checkValidity()) {
            const formData = new FormData(formCliente);
            const data = Object.fromEntries(formData.entries());
            console.log(data);

            fetch('/new_clients/save_client', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Cliente guardado exitosamente con ID ' + data.client_id);
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
            formCliente.reportValidity();
        }
    });
});
