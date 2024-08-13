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
            url: '/nueva_venta/obtener_ultimo_numero_venta',
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
                agregarProducto(ui.item.value, 1, ui.item.precio);
                $('#producto').val('');
                return false;
            }
            
        });
        $(function() {
            // Autocompletado para cliente
            $('#cliente').autocomplete({
                source: '/nueva_venta/autocompletar_clientes'
            })
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
            vaciarCarrito()
        });

        $('#numero_venta').on('keyup', function() {
            verificarNumeroVenta($(this).val());
        });

        $('#procesar_venta').click(function(event) {
            event.preventDefault();
            procesarVenta();
            vaciarCarrito();
            $('#cliente').val('');
            $('#numero_venta').val(function(i, val) { return +val + 1; });
        });

        $('.reset_button_id').click(function() {
            $.ajax({
                url: '/nueva_venta/reset',
                type: 'POST',
                success: function(response) {
                    console.log('Reset completado:', response);
                },
                error: function(xhr, status, error) {
                    console.error('Error en el reset:', status, error);
                }
            });
        });
    }
    
    function vaciarCarrito() {
        $('#tabla_venta tbody').empty();
        calcularTotalVenta();
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

        try {
            parsedPrecio = parseFloat(precio);
            if (isNaN(parsedPrecio)) {
                parsedPrecio = 0;
            }
        } catch (error) {
            console.error('Error al convertir precio:', error);
            parsedPrecio = 0;
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
            url: '/nueva_venta/verificar_numero_venta',
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
        var monto_total = parseFloat($('#valor_total_venta').text().replace('$', ''));
        // console.log(`este es el monto_total: ${monto_total}`);

        if (!cliente || !numero_venta || !fecha) {
            alert('Por favor completa todos los campos obligatorios.');
            return;
        }

        if ($('#mensaje_error_venta').text() !== '') {
            return;
        }

        var productos = [];
        $('#tabla_venta tbody tr').each(function() {
            var producto = $(this).find('td:first').text();
            var cantidad = $(this).find('.cantidad').val();
            var precio = $(this).find('.precio').val();
            productos.push({ producto: producto, cantidad: cantidad, precio: precio });
        });
        
        // Enviar productos como un array JSON
        $.post('/nueva_venta/procesar_venta', {
            cliente: cliente,
            numero_venta: numero_venta,
            fecha: fecha,
            productos: JSON.stringify(productos)  // Convertir el array a JSON
        }, function(response) {
            console.log(response);
        });
        
        crearFactura(fecha, numero_venta, cliente, monto_total);
        actualizarDeuda(numero_venta);
    }

    function crearFactura(fecha, numero_venta, cliente, monto_total) {
        $.ajax({
            url: '/nueva_venta/crear_factura',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                fecha: fecha,
                numero_venta: numero_venta,
                cliente: cliente,
                monto_total: monto_total
            }),
            success: function(response) {
                console.log('Factura creada:', response);
                // Actualizar deuda después de crear la factura
                actualizarDeuda(numero_venta);
            },
            error: function(xhr, status, error) {
                console.error('Error al crear la factura:', status, error);
            }
        });
    }

    function actualizarDeuda(numero_venta) {
        return $.ajax({
            url: '/nueva_venta/actualizar_deuda',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ numero_venta: numero_venta }),
            success: function(response) {
                console.log('Deuda actualizada:', response);
            },
            error: function(xhr, status, error) {
                console.error('Error al actualizar la deuda:', status, error);
            }
        });
    }
});
