$(document).ready(function() {
    inicializarFechaActual();
    inicializarAutocompletado();
});

function inicializarFechaActual() {
    var fechaActual = new Date().toISOString().slice(0, 10);
    $('#fecha').val(fechaActual);
}

function inicializarAutocompletado() {
    $('#cliente').autocomplete({
        source: '/new_sale/autocomplete_clients'
    });
}

document.getElementById('form_abono').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita el envío del formulario de manera tradicional
    
    const cliente = document.getElementById('cliente').value;
    const monto = parseFloat(document.getElementById('monto').value);
    const fecha = document.getElementById('fecha').value;

    console.log(cliente, monto, fecha)

    fetch( '/payments/add_payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cliente: cliente,
            monto: monto,
            fecha: fecha
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Abono registrado correctamente');
            // Vaciar el formulario
            document.getElementById('form_abono').reset();
            inicializarFechaActual();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

