$(function() {
    $("#producto").autocomplete({
        source: "/autocomplete",
        minLength: 2,
    });
});

$(function() {
    // Autocompletado para cliente
    $('#cliente').autocomplete({
        source: '/autocompletar_clientes'
    });

    // Autocompletado para producto
    $('#producto').autocomplete({
        source: '/autocompletar_productos'
    });
});
