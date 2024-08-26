$(document).ready(function() {
    inicializarFechaActual()
    inicializarAutocompletado()
    configurarEventos()
});

function configurarEventos() {
    $(document).on('keyup', '.cantidad', function() {
        actualizarTotalProducto($(this).closest('tr'));
    });

    $(document).on('input', '.precio', function() {
        actualizarTotalProducto($(this).closest('tr'));
    });

    $(document).on('click', '.eliminar-producto', function() {
        $(this).closest('tr').remove();
        calcularTotalVenta();
    });

    $('#vaciar_carrito').click(function() {
        vaciarCarrito()
    });
    
    $('#procesar_compra').click(function(event) {
        event.preventDefault();
        procesarCompra();

    });
}

function obtenerUltimoNumeroVenta() {
    fetch('/comprar_stock/obtener_ultimo_numero_venta', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())  // Convertir la respuesta a JSON
    .then(data => {
        console.log(data)
        $('#numero_compra').val(data.ultimo_numero);  // Usar el valor recibido
    })
    .catch(error => {
        console.log('Error al obtener el último número de venta:', error);
    });
}   

function vaciarCarrito() {
    $('#tabla_compra tbody').empty();
}

function inicializarFechaActual() {
    var fechaActual = new Date().toISOString().slice(0, 10);
    $('#fecha').val(fechaActual);
};

function inicializarAutocompletado() {
    $('#producto').autocomplete({
        source: function(request, response) {
            fetch('/nueva_venta/autocompletar_productos?term=' + encodeURIComponent(request.term))
                .then(res => res.json())
                .then(data => {
                    response(data);
                })
                .catch(error => {
                    console.error('Error al obtener productos:', error);
                });
        },
        minLength: 2,
        select: function(event, ui) {
            agregarProducto(ui.item.value, 1, ui.item.costo);
            $('#producto').val('');
            return false;
        }
    });
    $('#proveedor').autocomplete({
        source: '/comprar_stock/autocompletar_proveedores'
    });
}

function agregarProducto(producto, cantidad, costo) {
    var parsedCosto;

    try {
        parsedCosto = parseFloat(costo);
        if (isNaN(parsedCosto)) {
            parsedCosto = 0;
        }
    } catch (error) {
        console.error('Error al convertir costo:', error);
        parsedCosto = 0;
    }

    var row = `
        <tr>
            <td>${producto}</td>
            <td><input type="number" class="cantidad" value="${cantidad}" min="1"></td>
            <td><input type="number" class="costo" value="${parsedCosto.toFixed(2)}" step="0.01"></td>
            <td class="total-producto">$${(cantidad * parsedCosto).toFixed(2)}</td>
            <td><span class="eliminar-producto" title="Eliminar Producto" style="color: red; cursor: pointer;">&#x2716;</span></td>
        </tr>
    `;
    $('#tabla_compra tbody').append(row);
}

function actualizarTotalProducto(row) {
    var cantidad = row.find('.cantidad').val();
    var nuevoPrecio = parseFloat(row.find('.costo').val());
    if (!isNaN(nuevoPrecio)) {
        row.find('.total-producto').text('$' + (cantidad * nuevoPrecio).toFixed(2));
    }
}

function procesarCompra() {
    var proveedor = $('#proveedor').val();
    var compra_id = $('#numero_compra').val();
    var fecha = $('#fecha').val();

    if (!proveedor || !compra_id || !fecha) {
        alert('Por favor completa todos los campos obligatorios.');
        return;
    }

    if ($('#mensaje_error_venta').text() !== '') {
        return;
    }

    var productos = [];
    $('#tabla_compra tbody tr').each(function() {
        var producto = $(this).find('td:first').text();
        var cantidad = $(this).find('.cantidad').val();
        var costo = $(this).find('.costo').val();
        productos.push({ producto: producto, cantidad: cantidad, costo: costo });
    });

    var data = {
        proveedor: proveedor,
        compra_id: compra_id,
        fecha: fecha,
        productos: productos
    };
    
    // Enviar los datos con fetch
    fetch('/comprar_stock/procesar_compra', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'  // Establecer el tipo de contenido como JSON
        },
        body: JSON.stringify(data)  // Convertir los datos a JSON
    })
    .then(response => response.json())  // Parsear la respuesta como JSON
    .then(data => {
        vaciarCarrito();
        $('#proveedor').val('');
        $('#numero_compra').val('');
        alert('Success:', data);  // Manejar la respuesta con éxito
        // Aquí puedes agregar lógica adicional, como mostrar un mensaje de éxito o redirigir
    })
    .catch((error) => {
        alert('Error:', error);  // Manejar cualquier error
    });
} 