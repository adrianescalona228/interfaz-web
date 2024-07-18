document.addEventListener("DOMContentLoaded", function() {
    function toggleMenu() {
        console.log('fino rey');
        var menu = document.querySelector(".menu-izquierdo");
        var content = document.querySelector(".contenido-principal");
        
        if (menu && content) {
            if (menu.style.left === "0%") {
                menu.style.left = "-20%";
                content.style.marginLeft = "0";
            } else {
                menu.style.left = "0%";
                content.style.marginLeft = "15%";
            }
        } else {
            console.error('No se encontró el elemento "menu" o "contenido-principal".');
        }
    }

    var toggleButton = document.getElementById("toggle-button");
    if (toggleButton) {
        toggleButton.addEventListener("click", toggleMenu);
    } else {
        console.error('No se encontró el botón con el ID "toggle-button".');
    }
});