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

    // Función modificada para manejar la carga de iframes
    function handleContentLoad(contentElement, skeletonId) {
        if (contentElement.tagName.toLowerCase() === 'embed') {
            // Para PDFs, usar un timeout corto para simular la carga
            setTimeout(() => {
                const skeleton = document.getElementById(skeletonId);
                if (skeleton) {
                    skeleton.style.display = 'none';
                    contentElement.style.display = 'block';
                }
            }, 1000);
        } else {
            contentElement.addEventListener('load', function() {
                const skeleton = document.getElementById(skeletonId);
                if (skeleton) {
                    skeleton.style.display = 'none';
                    contentElement.style.display = 'block';
                }
            });
        }
    }

    // Manejar la carga de cada elemento
    const pdfEmbed = document.querySelector('.pagina_libro embed');
    const japaneseIframe = document.querySelector('.idioma1 iframe');
    const chineseIframe = document.querySelector('.idioma2 iframe');
    const calendarIframe = document.querySelector('#calendar iframe');

    handleContentLoad(pdfEmbed, 'pdf-skeleton');
    handleContentLoad(japaneseIframe, 'japanese-skeleton');
    handleContentLoad(chineseIframe, 'chinese-skeleton');
    handleContentLoad(calendarIframe, 'calendar-skeleton');

    // Función modificada para manejar errores
    function handleLoadError(element, skeletonId) {
        element.addEventListener('error', function() {
            const skeleton = document.getElementById(skeletonId);
            if (skeleton) {
                skeleton.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        Error al cargar el contenido
                    </div>
                `;
            }
        });
    }

    // Aplicar manejo de errores a todos los elementos
    [pdfEmbed, japaneseIframe, chineseIframe, calendarIframe].forEach((element, index) => {
        handleLoadError(element, ['pdf-skeleton', 'japanese-skeleton', 'chinese-skeleton', 'calendar-skeleton'][index]);
    });
}); 