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
                    el.style.flex = '0 0 auto';
                }
            });
            
            // Expandir el elemento clickeado
            this.classList.add('expanded');
            this.classList.remove('contracted');
            this.style.flex = '1 1 auto';
            
            // Ajustar el tamaño del contenedor padre
            const parentContainer = this.closest('.left_container, .right_container');
            if (parentContainer) {
                parentContainer.style.flex = '4';
                parentContainer.style.width = '80%';
                
                // Ajustar el otro contenedor
                const otherContainer = parentContainer.classList.contains('left_container') 
                    ? document.querySelector('.right_container') 
                    : document.querySelector('.left_container');
                if (otherContainer) {
                    otherContainer.style.flex = '0.8';
                    otherContainer.style.width = '20%';
                }
            }
        });
    });
    
    function resetElements() {
        expandableElements.forEach(element => {
            element.classList.remove('expanded', 'contracted');
            element.style.flex = '';
        });
        
        // Resetear los contenedores principales
        const containers = document.querySelectorAll('.left_container, .right_container');
        containers.forEach(container => {
            container.style.flex = '1';
            container.style.width = '';
        });
    }

    // Función para manejar la carga de iframes
    function handleContentLoad(contentElement, skeletonId) {
        if (contentElement.tagName.toLowerCase() === 'embed') {
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

    // Función para manejar errores
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

    // Funciones para cargar papers
    function loadPapers(source) {
        fetch(`/fetch_papers/${source}`)
            .then(response => response.json())
            .then(data => {
                checkPaperStatus(source);
            })
            .catch(error => {
                console.error('Error iniciando la carga:', error);
                showError(source);
            });
    }

    function checkPaperStatus(source) {
        fetch(`/paper_status/${source}`)
            .then(response => response.json())
            .then(data => {
                console.log(`Estado de ${source}:`, data);
                if (data.status === 'completed') {
                    updatePaperSection(source, data.papers);
                } else if (data.status === 'error') {
                    showError(source);
                } else {
                    setTimeout(() => checkPaperStatus(source), 2000);
                }
            })
            .catch(error => {
                console.error('Error verificando estado:', error);
                showError(source);
            });
    }

    function updatePaperSection(source, papers) {
        const section = document.querySelector(`.paper-section[data-source="${source}"]`);
        const container = section.querySelector('.paper-list');
        if (!container) return;

        // Remover la clase loading
        section.classList.remove('loading');

        if (!papers || papers.length === 0) {
            container.innerHTML = '<p class="coming-soon">No hay papers disponibles en este momento</p>';
            return;
        }

        let html = '';
        papers.forEach(paper => {
            html += `
                <div class="paper-item">
                    <h4><a href="${paper.source_url}" target="_blank">${paper.title}</a></h4>
                    <p class="paper-authors">${paper.authors}</p>
                    <p class="paper-abstract">${paper.abstract}</p>
                    <div class="paper-meta">
                        <div class="paper-info">
                            <span class="paper-date">${paper.date}</span>
                            ${paper.citations !== undefined ? `<span class="paper-citations">📚 ${paper.citations} citas</span>` : ''}
                        </div>
                        <div class="paper-links">
                            ${paper.pdf_url ? `<a href="${paper.pdf_url}" target="_blank" class="paper-pdf">PDF</a>` : ''}
                            ${paper.repository_url ? `<a href="${paper.repository_url}" target="_blank" class="paper-code"><i class="fas fa-code"></i> Repository</a>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });

        // Actualizar el contenido
        container.innerHTML = html;
    }

    function showError(source) {
        const container = document.querySelector(`.paper-section[data-source="${source}"] .paper-list`);
        if (container) {
            container.innerHTML = '<p class="error-message">Error cargando papers. Por favor, intenta más tarde.</p>';
            container.closest('.paper-section').classList.remove('loading');
        }
    }

    // Agregar clase loading a todas las secciones de papers
    document.querySelectorAll('.paper-section').forEach(section => {
        section.classList.add('loading');
    });

    // Iniciar la carga de papers
    loadPapers('arxiv');
    loadPapers('papers_with_code');
    loadPapers('google_scholar');
}); 