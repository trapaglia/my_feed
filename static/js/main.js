document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los elementos que pueden expandirse
    const expandableElements = document.querySelectorAll('.left_container > div, .right_container > div');
    
    expandableElements.forEach(element => {
        element.addEventListener('click', function(e) {
            // Prevenir que el click se propague al contenedor padre
            e.stopPropagation();
            
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
            
            // Expandir el contenedor padre
            const parentContainer = this.closest('.left_container, .right_container');
            const otherContainer = parentContainer.classList.contains('left_container') 
                ? document.querySelector('.right_container') 
                : document.querySelector('.left_container');
            
            parentContainer.classList.add('expanded');
            otherContainer.classList.add('contracted');
        });
    });
    
    // Función para resetear todos los elementos a su tamaño original
    function resetElements() {
        expandableElements.forEach(element => {
            element.classList.remove('expanded', 'contracted');
        });
        document.querySelector('.left_container').classList.remove('expanded', 'contracted');
        document.querySelector('.right_container').classList.remove('expanded', 'contracted');
    }
}); 