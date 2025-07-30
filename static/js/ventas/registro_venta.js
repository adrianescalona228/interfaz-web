$(function() {
    // Inicializar
    inicializarFechaActual();
    obtenerUltimoNumeroVenta();
    inicializarAutocompletado();
    configurarEventos();
    
    function inicializarFechaActual() {
        var fechaActual = new Date().toISOString().slice(0, 10);
        $('#date').val(fechaActual);
    }
    
    function obtenerUltimoNumeroVenta() {
        fetch('/new_sale/last_sale_number', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())  // Convertir la respuesta a JSON
        .then(data => {
          console.log(data.last_number)
            $('#sale_number').val(data.last_number);  // Usar el valor recibido
        })
        .catch(error => {
            console.log('Error al obtener el último número de venta:', error);
        });
    }    
    
    function inicializarAutocompletado() {
        $('#product').autocomplete({
            source: function(request, response) {
                fetch('/new_sale/autocomplete_products?term=' + encodeURIComponent(request.term))
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
                if (ui.item.quantity !== undefined) {
                    agregarProducto(ui.item.value, 1, ui.item.price, ui.item.quantity);
                } else {
                    console.error("El producto no tiene cantidad definida.");
                }
        
                $('#product').val('');
                return false;
            }
        });
            
        $('#client').autocomplete({
            source: '/new_sale/autocomplete_clients'
        });
    }
    

    function configurarEventos() {
        // Escuchar cambios en cantidad y precio con 'input' para mejor respuesta
        $(document).on('input', '.cantidad, .precio', function() {
            actualizarTotalProducto($(this).closest('tr'));
        });

        // Eliminar producto
        $(document).on('click', '.eliminar-producto', function() {
            $(this).closest('tr').remove();
            calcularTotalVenta();
        });

        // Vaciar carrito (corregido el id del botón)
        $('#empty_cart').click(function() {
            vaciarCarrito();
        });

        // Verificar número de venta en tiempo real
        $('#sale_number').on('keyup', function() {
            verificarNumeroVenta($(this).val());
        });

        // Procesar venta al hacer clic
        $('#process_sale').click(function(event) {
            event.preventDefault();
            procesarVenta();
        });

        // Botón reset
        $('.reset_button_id').click(function() {
            fetch('/nueva_venta/reset', {
                method: 'POST'
            })
            .then(response => response.text())
            .then(data => {
                console.log('Reset completado:', data);
            })
            .catch(error => {
                console.error('Error en el reset:', error);
            });
        });
    }

    
    function vaciarCarrito() {
        $('#sales_table tbody').empty();
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
        $('#sales_table tbody').append(row);
        calcularTotalVenta();
    }
    
    function precio(row) {
        var cantidad = row.find('.cantidad').val();
        var nuevoPrecio = parseFloat(row.find('.precio').val());
        if (!isNaN(nuevoPrecio)) {
            row.find('.total-producto').text('$' + (cantidad * nuevoPrecio).toFixed(2));
            calcularTotalVenta();
        }
    }
    function actualizarTotalProducto(row) {
        var cantidad = parseFloat(row.find('.cantidad').val()) || 0;
        var precio = parseFloat(row.find('.precio').val()) || 0;
        var totalProducto = cantidad * precio;

        row.find('.total-producto').text('$' + totalProducto.toFixed(2));

        calcularTotalVenta();
    }


    function calcularTotalVenta() {
        var totalVenta = 0;
        $('#sales_table tbody tr').each(function() {
            var cantidad = parseFloat($(this).find('.cantidad').val()) || 0;
            var precio = parseFloat($(this).find('.precio').val()) || 0;
            totalVenta += cantidad * precio;
        });
        $('#total_sale_value').text('$' + totalVenta.toFixed(2));
    }


    function verificarNumeroVenta(numero_venta) {
        fetch('/new_sale/verify_sale_number', {
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
                $('#process_sale').prop('disabled', true);
            } else {
                $('#mensaje_error_venta').text('');
                $('#process_sale').prop('disabled', false);
            }
        })
        .catch(error => {
            console.error('Error al verificar el número de venta:', error);
        });
    }    

    function procesarVenta() {
        var cliente = $('#client').val();
        var numero_venta = $('#sale_number').val();
        var fecha = $('#date').val();
        var monto_total = parseFloat($('#total_sale_value').text().replace('$', ''));
        
        if (!cliente || !numero_venta || !fecha) {
            alert('Por favor completa todos los campos obligatorios.');
            return;
        }
    
        if ($('#mensaje_error_venta').text() !== '') {
            return;
        }
    
        var productos = [];
        $('#sales_table tbody tr').each(function() {
            var producto = $(this).find('td:first').text();
            var cantidad = $(this).find('.cantidad').val();
            var precio = $(this).find('.precio').val();
            productos.push({ product: producto, quantity: cantidad, price: precio });
        });
    

      fetch('/new_sale/process_sale', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              client: cliente,
              sale_number: numero_venta,
              date: fecha,
              products: productos,
              total_amount: monto_total
          })
      })
      .then(async response => {
          const data = await response.json();  // Siempre intentamos parsear el JSON

          if (!response.ok) {
              // Mostrar el error que vino del backend
              alert('Error: ' + (data.error || 'Error desconocido'));
              return;
          }

          // Si llega aquí, todo fue bien
          alert(data.message || '¡Venta registrada correctamente!');

          // Limpia el carrito y los campos si lo deseas
          vaciarCarrito();
          $('#client').val('');
          $('#sale_number').val(function(i, val) { return +val + 1; });
      })
      .catch(error => {
          console.error('Error:', error);
          alert('Ocurrió un error al procesar la venta. Por favor, intenta de nuevo.');
      });
    }
});
