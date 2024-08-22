$(document).ready(function() {
    function calcularTotalDeuda() {
        var totalDeuda = 0;
        $('table tbody tr').each(function() {
            var monto = parseFloat($(this).find('.monto').text());
            if (!isNaN(monto)) {
                totalDeuda += monto;
            }
        });
        $('#valor_total_deuda').text('$' + totalDeuda.toFixed(2));
    }
    
    // Llama a la función para calcular el total de deuda cuando la página carga
    calcularTotalDeuda();
});