$(function() {  

    // Petición AJAX para obtener el último número de venta
    $.ajax({
        url: '/obtener_ultimo_numero_venta',  // Ruta en tu servidor para obtener el número
        method: 'GET',
        success: function(data) {
            // Actualizar el valor del input con el último número de venta
            $('#numero_venta').val(data.ultimo_numero);
        },
        error: function() {
            console.log('Error al obtener el último número de venta.');
        }
    });

    // Función para inicializar la fecha actual en el campo de fecha
    function inicializarFechaActual() {
        var fechaActual = new Date().toISOString().slice(0, 10);
        document.getElementById('fecha').value = fechaActual;
    }

    // Llama a la función para inicializar la fecha al cargar la página
    inicializarFechaActual();

    // Inicialización del autocompletado para productos
    $('#producto').autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "/autocompletar_productos",
                dataType: "json",
                data: {
                    term: request.term
                },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            // Obtener datos del producto seleccionado desde el autocompletado
            var nombreProducto = ui.item.value; // Nombre del producto seleccionado
            var cantidad = 1; // Cantidad inicial, puedes ajustarlo según tus necesidades
            var precio = ui.item.precio; // Obtener precio del producto si está disponible en ui.item

            // Llamar a la función para agregar el producto al carrito
            agregarProducto(nombreProducto, cantidad, precio);

            // Limpiar campo de producto después de agregarlo
            $('#producto').val('');

            return false; // Evitar que el valor seleccionado se establezca en el campo de entrada
        }
    });

    // Evento keyup para calcular total del producto al cambiar la cantidad manualmente
    $(document).on('keyup', '.cantidad', function() {
        calcularTotalProducto($(this).closest('tr'));
    });

    // Función para calcular el total del producto (cantidad * precio) y actualizar la tabla
    function calcularTotalProducto(row) {
        var cantidad = parseInt(row.find('.cantidad').val());
        var precio = parseFloat(row.find('td:nth-child(3)').text().replace('$', ''));
        var totalProducto = cantidad * precio;
        row.find('.total-producto').text('$' + totalProducto.toFixed(2));

        calcularTotalVenta(); // Llamar a la función para recalcular el total de la venta
    }

    //Agregar productos al carrito
    function agregarProducto(producto, cantidad, precio) {
        var parsedPrecio;
        try {
            parsedPrecio = parseFloat(precio); // Intentar convertir el precio a float
            if (isNaN(parsedPrecio)) { // Verificar si no es un número válido
                parsedPrecio = 0; // Establecer precio en 0 si no es un número válido
            }
        } catch (error) {
            console.error('Error al convertir precio:', error);
            parsedPrecio = 0; // Manejar cualquier error de conversión estableciendo precio en 0
        }
        
        var totalProducto = cantidad * parsedPrecio; // Calcular total por producto con el precio parseado
        var row = '<tr>' +
                    '<td>' + producto + '</td>' +
                    '<td><input type="number" class="cantidad" value="' + cantidad + '" min="1"></td>' +
                    '<td><input type="number" class="precio" value="' + parsedPrecio.toFixed(2) + '" step="0.01"></td>' + // Campo editable para precio
                    '<td class="total-producto">$' + totalProducto.toFixed(2) + '</td>' + // Mostrar total por producto
                    '<td><span class="eliminar-producto" title="Eliminar Producto" style="color: red; cursor: pointer;">&#x2716;</span></td>' + // "X" roja para eliminar
                '</tr>';
        $('#tabla_venta tbody').append(row);
    
        // Capturar evento de cambio en el campo de precio para actualizar total por producto
        $('.precio').on('input', function() {
            var cantidad = $(this).closest('tr').find('.cantidad').val(); // Obtener cantidad del producto
            var nuevoPrecio = parseFloat($(this).val()); // Obtener nuevo precio ingresado
            if (!isNaN(nuevoPrecio)) { // Verificar si el nuevo precio es un número válido
                $(this).closest('tr').find('.total-producto').text('$' + (cantidad * nuevoPrecio).toFixed(2)); // Actualizar total por producto
                calcularTotalVenta(); // Recalcular el total de la venta
            }
        });
    
        calcularTotalVenta(); // Calcular el total de la venta inicialmente
    }

    function calcularTotalVenta() {
        var totalVenta = 0;

        // Recorrer cada fila de la tabla
        $('#tabla_venta tbody tr').each(function() {
            var cantidad = parseFloat($(this).find('.cantidad').val()); // Obtener cantidad
            var precio = parseFloat($(this).find('.precio').val()); // Obtener precio del input
            var totalProducto = cantidad * precio; // Calcular total por producto

            // Mostrar el total por producto en la tabla
            $(this).find('.total-producto').text('$' + totalProducto.toFixed(2));
    
            totalVenta += totalProducto; // Sumar al total de la venta
        });
    
        // Mostrar el total de la venta en el elemento correspondiente
        console.log('Total Venta:', totalVenta); // Añadir console.log aquí
        console.log($('#valor_total_venta'));
        $('#valor_total_venta').text('$' + totalVenta.toFixed(2));
    }

    // Función para vaciar el carrito
    $('#vaciar_carrito').click(function() {
        $('#tabla_venta tbody').empty(); // Vaciar el contenido del cuerpo de la tabla
        calcularTotalVenta(); // Recalcular el total de la venta
    });
    
    $(document).ready(function() {
        // Evento keyup para verificar dinámicamente el número de venta
        $('#numero_venta').on('keyup', function() {
            var numero_venta = $(this).val();
    
            // Realizar la petición AJAX para verificar el número de venta
            verificarNumeroVenta(numero_venta);
        });
    });

    function verificarNumeroVenta(numero_venta) {
        $.ajax({
            url: '/verificar_numero_venta',
            method: 'POST',
            data: { numero_venta: numero_venta },
            success: function(data) {
                if (data.existe) {
                    console.log('El número de venta ' + numero_venta + ' ya existe en la base de datos.');
                    // Mostrar mensaje de error si el número de venta existe
                    $('#mensaje_error_venta').text('¡Este número de venta ya existe!');
                    $('#registrar_venta').prop('disabled', true); // Deshabilitar botón de registro
                } else {
                    console.log('El número de venta ' + numero_venta + ' no existe en la base de datos.');
                    // Limpiar mensaje de error si el número de venta no existe
                    $('#mensaje_error_venta').text('');
                    $('#registrar_venta').prop('disabled', false); // Habilitar botón de registro
                }
            },
            error: function() {
                console.log('Error al verificar el número de venta.');
            }
        });
    }

    //Eliminar un producto con la x
    $(document).on('click', '.eliminar-producto', function() {
        $(this).closest('tr').remove(); // Elimina la fila del producto
        calcularTotalVenta(); // Recalcula el total de la venta
    });

    // Evento keyup para verificar dinámicamente el número de venta
    $('#numero_venta').on('keyup', function() {
        var numero_venta = $(this).val();
        verificarNumeroVenta(numero_venta);
    });

    // Procesar venta al hacer submit
    $('#form_venta').submit(function(event) {
        event.preventDefault(); // Evitar envío por defecto del formulario

        // Obtener datos del formulario de encabezado
        var cliente = $('#cliente').val();
        var numero_venta = $('#numero_venta').val();
        var fecha = $('#fecha').val();

        // Validar campos importantes
        if (!cliente && !numero_venta && !fecha) {
            alert('Por favor completa todos los campos obligatorios.');
            return;
        }

        // Verificar nuevamente si el número de venta ya existe antes de proceder
        verificarNumeroVenta(numero_venta);

        // Si el número de venta ya existe, detener el proceso de registro
        if ($('#error_numero_venta').text() !== '') {
            return;
        }

        // Recorrer las filas de la tabla y enviar datos al servidor para guardar en la base de datos
        $('#tabla_venta tbody tr').each(function(index, row) {
            var producto = $(row).find('td:first').text();
            var cantidad = $(row).find('.cantidad').text();

            // Aquí se enviarían los datos al servidor por AJAX para guardar en la base de datos
            $.post('/procesar_venta', {
                cliente: cliente,
                numero_venta: numero_venta,
                fecha: fecha,
                producto: producto,
                cantidad: cantidad
            }, function(response) {
                console.log(response); // Manejar respuesta del servidor si es necesario
            });
        });
        
        // Limpiar tabla de carrito después de procesar la venta
        $('#tabla_venta tbody').empty();

        // Mostrar mensaje de venta procesada correctamente
        $('#mensaje_venta_procesada').text('Venta procesada correctamente');

        // Refrescar la página después de 1 segundo
        setTimeout(function() {
            location.reload();
        }, 1000); // 1000 milisegundos = 1 segundo

    });
});
