//registro_venta.js
$(function() {
    // Inicializar
    inicializarFechaActual();
    obtenerUltimoNumeroVenta();
    inicializarAutocompletado();
    configurarEventos();
    
    function inicializarFechaActual() {
        var fechaActual = new Date().toISOString().slice(0, 10);
        $('#fecha').val(fechaActual);
    }
    
    function obtenerUltimoNumeroVenta() {
        $.ajax({
            url: '/obtener_ultimo_numero_venta',
            method: 'GET',
            success: function(data) {
                $('#numero_venta').val(data.ultimo_numero);
            },
            error: function() {
                console.log('Error al obtener el último número de venta.');
            }
        });
    }
    
    function inicializarAutocompletado() {
        $('#producto').autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: "/autocompletar_productos",
                    dataType: "json",
                    data: { term: request.term },
                    success: function(data) {
                        response(data);
                    }
                });
            },
            minLength: 2,
            select: function(event, ui) {
                agregarProducto(ui.item.value, 1, ui.item.precio);
                $('#producto').val('');
                return false;
            }
        });
    }
    
    function configurarEventos() {
        $(document).on('keyup', '.cantidad', function() {
            calcularTotalProducto($(this).closest('tr'));
        });

        $(document).on('input', '.precio', function() {
            actualizarTotalProducto($(this).closest('tr'));
        });

        $(document).on('click', '.eliminar-producto', function() {
            $(this).closest('tr').remove();
            calcularTotalVenta();
        });

        $('#vaciar_carrito').click(function() {
            $('#tabla_venta tbody').empty();
            calcularTotalVenta();
        });

        $('#numero_venta').on('keyup', function() {
            verificarNumeroVenta($(this).val());
        });

        $('#form_venta').submit(function(event) {
            event.preventDefault();
            procesarVenta();
        });
    }
    
    function calcularTotalProducto(row) {
        var cantidad = parseInt(row.find('.cantidad').val());
        var precio = parseFloat(row.find('.precio').val());
        var totalProducto = cantidad * precio;
        row.find('.total-producto').text('$' + totalProducto.toFixed(2));
        calcularTotalVenta();
    }
    
    function agregarProducto(producto, cantidad, precio) {
        var parsedPrecio;

        // Intentar convertir el precio a float
        try {
            parsedPrecio = parseFloat(precio);
            if (isNaN(parsedPrecio)) {
                parsedPrecio = 0; // Establecer precio en 0 si no es un número válido
            }
        } catch (error) {
            console.error('Error al convertir precio:', error);
            parsedPrecio = 0; // Manejar cualquier error de conversión estableciendo precio en 0
        }
    
        var row = `
            <tr>
                <td>${producto}</td>
                <td><input type="number" class="cantidad" value="${cantidad}" min="1"></td>
                <td><input type="number" class="precio" value="${precio.toFixed(2)}" step="0.01"></td>
                <td class="total-producto">$${(cantidad * precio).toFixed(2)}</td>
                <td><span class="eliminar-producto" title="Eliminar Producto" style="color: red; cursor: pointer;">&#x2716;</span></td>
            </tr>
        `;
        $('#tabla_venta tbody').append(row);
        calcularTotalVenta();
    }
    
    function actualizarTotalProducto(row) {
        var cantidad = row.find('.cantidad').val();
        var nuevoPrecio = parseFloat(row.find('.precio').val());
        if (!isNaN(nuevoPrecio)) {
            row.find('.total-producto').text('$' + (cantidad * nuevoPrecio).toFixed(2));
            calcularTotalVenta();
        }
    }

    function calcularTotalVenta() {
        var totalVenta = 0;
        $('#tabla_venta tbody tr').each(function() {
            var cantidad = parseFloat($(this).find('.cantidad').val());
            var precio = parseFloat($(this).find('.precio').val());
            totalVenta += cantidad * precio;
        });
        $('#valor_total_venta').text('$' + totalVenta.toFixed(2));
    }

    function verificarNumeroVenta(numero_venta) {
        $.ajax({
            url: '/verificar_numero_venta',
            method: 'POST',
            data: { numero_venta: numero_venta },
            success: function(data) {
                if (data.existe) {
                    $('#mensaje_error_venta').text('¡Este número de venta ya existe!');
                    $('#registrar_venta').prop('disabled', true);
                } else {
                    $('#mensaje_error_venta').text('');
                    $('#registrar_venta').prop('disabled', false);
                }
            },
            error: function() {
                console.log('Error al verificar el número de venta.');
            }
        });
    }

    function procesarVenta() {
        var cliente = $('#cliente').val();
        var numero_venta = $('#numero_venta').val();
        var fecha = $('#fecha').val();

        if (!cliente || !numero_venta || !fecha) {
            alert('Por favor completa todos los campos obligatorios.');
            return;
        }

        if ($('#mensaje_error_venta').text() !== '') {
            return;
        }

        $('#tabla_venta tbody tr').each(function() {
            var producto = $(this).find('td:first').text();
            var cantidad = $(this).find('.cantidad').val();
            $.post('/procesar_venta', {
                cliente: cliente,
                numero_venta: numero_venta,
                fecha: fecha,
                producto: producto,
                cantidad: cantidad
            }, function(response) {
                console.log(response);
            });
        });

        $('#tabla_venta tbody').empty();
        $('#mensaje_venta_procesada').text('Venta procesada correctamente');
        setTimeout(function() {
            location.reload();
        }, 1000);
    }
});
