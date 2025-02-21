document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los elementos que pueden expandirse
    const expandableElements = document.querySelectorAll('.left_container > div, .right_container > div');
    
    expandableElements.forEach(element => {
        element.addEventListener('click', function() {
            // Si el elemento ya está expandido, lo contraemos
            if (this.classList.contains('expanded')) {
                resetElements();
                return;
            }
            
            // Contraer todos los elementos
            expandableElements.forEach(el => {
                if (el !== this) {
                    el.classList.add('contracted');
                    el.classList.remove('expanded');
                }
            });
            
            // Expandir el elemento clickeado
            this.classList.add('expanded');
            this.classList.remove('contracted');
        });
    });
    
    // Función para resetear todos los elementos a su tamaño original
    function resetElements() {
        expandableElements.forEach(element => {
            element.classList.remove('expanded', 'contracted');
        });
    }
}); 