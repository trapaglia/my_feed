document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los elementos que pueden expandirse
    const expandableElements = document.querySelectorAll('.left_container > div, .right_container > div');
    
    expandableElements.forEach(element => {
        element.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Si el elemento ya está expandido, lo contraemos
            if (this.classList.contains('expanded')) {
                resetElements();
                return;
            }
            
            // Contraer todos los elementos excepto el clickeado
            expandableElements.forEach(el => {
                if (el !== this) {
                    el.classList.add('contracted');
                    el.classList.remove('expanded');
                }
            });
            
            // Expandir el elemento clickeado
            this.classList.add('expanded');
            this.classList.remove('contracted');
            
            // Ajustar el tamaño del contenedor padre sin contraer el otro contenedor
            const parentContainer = this.closest('.left_container, .right_container');
            parentContainer.classList.add('expanded');
            
            // Eliminar la clase expanded del otro contenedor si la tiene
            const otherContainer = parentContainer.classList.contains('left_container') 
                ? document.querySelector('.right_container') 
                : document.querySelector('.left_container');
            otherContainer.classList.remove('expanded');
        });
    });
    
    function resetElements() {
        expandableElements.forEach(element => {
            element.classList.remove('expanded', 'contracted');
        });
        document.querySelector('.left_container').classList.remove('expanded');
        document.querySelector('.right_container').classList.remove('expanded');
    }
}); 