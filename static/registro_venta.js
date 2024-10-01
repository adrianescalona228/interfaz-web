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
        fetch('/nueva_venta/obtener_ultimo_numero_venta', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())  // Convertir la respuesta a JSON
        .then(data => {
            $('#numero_venta').val(data.ultimo_numero);  // Usar el valor recibido
        })
        .catch(error => {
            console.log('Error al obtener el último número de venta:', error);
        });
    }    
    
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
                // Agregar un console.log para ver qué contiene ui.item
                console.log(ui.item); // Depuración para verificar el objeto
        
                // Verificar si existe la cantidad antes de pasarla
                if (ui.item.cantidad !== undefined) {
                    agregarProducto(ui.item.value, 1, ui.item.precio, ui.item.cantidad);
                } else {
                    console.error("El producto no tiene cantidad definida.");
                }
        
                $('#producto').val('');
                return false;
            }
        });
            
        $('#cliente').autocomplete({
            source: '/nueva_venta/autocompletar_clientes'
        });
    }
    
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

        $('#numero_venta').on('keyup', function() {
            verificarNumeroVenta($(this).val());
        });

        $('#procesar_venta').click(function(event) {
            event.preventDefault();
            procesarVenta();
        });

        $('.reset_button_id').click(function() {
            fetch('/nueva_venta/reset', {
                method: 'POST'
            })
            .then(response => response.text())  // Puedes ajustar esto si el servidor devuelve otro tipo de respuesta
            .then(data => {
                console.log('Reset completado:', data);
            })
            .catch(error => {
                console.error('Error en el reset:', error);
            });
        });        
    }
    
    function vaciarCarrito() {
        $('#tabla_venta tbody').empty();
        calcularTotalVenta();
    }
    
    function agregarProducto(producto, cantidad, precio, cantidadInventario) {
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
                <td class="inventario">(${cantidadInventario})</td>
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
        fetch('/nueva_venta/verificar_numero_venta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ numero_venta: numero_venta })
        })
        .then(response => response.json())  // Convierte la respuesta a JSON
        .then(data => {
            if (data.existe) {
                $('#mensaje_error_venta').text('¡Este número de venta ya existe!');
                $('#procesar_venta').prop('disabled', true);
            } else {
                $('#mensaje_error_venta').text('');
                $('#procesar_venta  ').prop('disabled', false);
            }
        })
        .catch(error => {
            console.error('Error al verificar el número de venta:', error);
        });
    }    

    function procesarVenta() {
        var cliente = $('#cliente').val();
        var numero_venta = $('#numero_venta').val();
        var fecha = $('#fecha').val();
        var monto_total = parseFloat($('#valor_total_venta').text().replace('$', ''));
    
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
    
        // Enviar datos con fetch
        fetch('/nueva_venta/procesar_venta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // Establece el tipo de contenido como JSON
            },
            body: JSON.stringify({
                cliente: cliente,
                numero_venta: numero_venta,
                fecha: fecha,
                productos: productos,  // Envía productos como un array JSON
                monto_total: monto_total
            })
        })
        .then(response => response.text())  // Puedes ajustar la respuesta según lo que devuelva el backend
        .then(data => {
            console.log('Success:', data);
            
            // Mostrar alerta de éxito si la venta se registró correctamente
            if (data.includes('Venta procesada correctamente')) {
                alert('¡Venta registrada correctamente!');
                
                // Limpia el carrito y los campos de entrada
                vaciarCarrito();
                $('#cliente').val('');
                $('#numero_venta').val(function(i, val) { return +val + 1; });
            } else {
                // Si el backend devuelve algo inesperado, mostrarlo también como alerta de error
                alert('Ocurrió un error: ' + data);
            }
        
            // Aquí puedes agregar lógica adicional, como mostrar un mensaje de éxito
        })
        .catch(error => {
            console.error('Error:', error);
            // Mostrar alerta de error en caso de que haya un problema con la solicitud
            alert('Ocurrió un error al procesar la venta. Por favor, intenta de nuevo.');
        });        

    }
});
