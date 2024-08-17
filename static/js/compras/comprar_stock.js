$(document).ready(function() {
    inicializarFechaActual()
    autocompletarProductos()
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
        procesarVenta();
        vaciarCarrito();
    });
}

function vaciarCarrito() {
    $('#tabla_venta tbody').empty();
}

function inicializarFechaActual() {
    var fechaActual = new Date().toISOString().slice(0, 10);
    $('#fecha').val(fechaActual);
};

function autocompletarProductos() {
    $('#producto').autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "/nueva_venta/autocompletar_productos",
                dataType: "json",
                data: { term: request.term },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            agregarProducto(ui.item.value, 1, ui.item.costo);
            $('#producto').val('');
            return false;
        }
    }
)}

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
    var nuevoPrecio = parseFloat(row.find('.precio').val());
    if (!isNaN(nuevoPrecio)) {
        row.find('.total-producto').text('$' + (cantidad * nuevoPrecio).toFixed(2));
    }
}

function procesarCompra() {
    var proveedor = $('#proveedor').val();
    var numero_compra = $('#numero_compra').val();
    var fecha = $('#fecha').val();

    if (!proveedor || !numero_compra || !fecha) {
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
        var precio = $(this).find('.precio').val();
        productos.push({ producto: producto, cantidad: cantidad, precio: precio });
    });

    var data = {
        proveedor: proveedor,
        numero_compra: numero_compra,
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
        console.log('Success:', data);  // Manejar la respuesta con éxito
        // Aquí puedes agregar lógica adicional, como mostrar un mensaje de éxito o redirigir
    })
    .catch((error) => {
        console.error('Error:', error);  // Manejar cualquier error
    });
} 