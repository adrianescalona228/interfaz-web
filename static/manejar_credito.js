$(document).ready(function() {
    inicializarFechaActual();
    
    function inicializarFechaActual() {
        var fechaActual = new Date().toISOString().slice(0, 10);
        $('#fecha').val(fechaActual);
    }

    
});