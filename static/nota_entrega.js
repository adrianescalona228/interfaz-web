// $(document).ready(function() {
//     $('#generar_nota').click(function() {
//         var numero_venta = $('#numero_venta').val();

//         if (!numero_venta) {
//             alert('Por favor completa todos los campos obligatorios.');
//             return;
//         }

//         $.post('/generar_nota_entrega', {
//             numero_venta: numero_venta,
//         }, function(response) {
//             $('#mensaje_nota_generada').text('Nota de entrega generada correctamente.');
//             // Puedes agregar lógica para mostrar o imprimir la nota de entrega aquí.
//         }).fail(function(xhr) {
//             alert('Ocurrió un error al generar la nota de entrega: ' + xhr.responseText);
//             console.log(xhr)
//         });
//     });
// });