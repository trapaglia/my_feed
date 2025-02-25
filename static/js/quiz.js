let questions = [];
let currentQuestionIndex = 0;

// Función para cargar las preguntas
function loadQuestions() {
    fetch('/static/data/questions.json')
        .then(response => response.json())
        .then(data => {
            questions = data.questions;
            prioritizeQuestions();
            showQuestion();
        })
        .catch(error => {
            console.error('Error cargando las preguntas:', error);
            document.getElementById('currentQuestion').textContent = 'Error cargando las preguntas';
        });
}

// Cargar las preguntas al iniciar
loadQuestions();

// Función para calcular la prioridad de una pregunta
function calculatePriority(question) {
    const stats = question.stats;
    const now = new Date().getTime();
    
    // Si nunca se ha revisado, darle alta prioridad
    if (!stats.last_reviewed) {
        return Number.MAX_SAFE_INTEGER;
    }
    
    // Si está pendiente de revisión
    if (stats.next_review && new Date(stats.next_review).getTime() <= now) {
        // Mayor prioridad a las preguntas con más errores
        const errorRatio = stats.incorrect_count / (stats.correct_count + stats.incorrect_count + 1);
        return errorRatio * 1000 + (now - new Date(stats.next_review).getTime());
    }
    
    return -1; // No necesita revisión aún
}

// Función para priorizar las preguntas
function prioritizeQuestions() {
    questions.sort((a, b) => calculatePriority(b) - calculatePriority(a));
    // Filtrar preguntas que no necesitan revisión
    questions = questions.filter(q => calculatePriority(q) >= 0);
    
    // Si no hay preguntas para revisar, cargar todas
    if (questions.length === 0) {
        fetch('/static/data/questions.json')
            .then(response => response.json())
            .then(data => {
                questions = data.questions;
                shuffleArray(questions);
            });
    }
}

// Función para mezclar un array (Fisher-Yates shuffle)
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// Función para calcular el próximo intervalo
function calculateNextInterval(question, remembered) {
    const stats = question.stats;
    let interval = stats.interval || 1;
    
    if (remembered) {
        // Si recordó, aumentar el intervalo (sistema exponencial)
        interval *= 2;
    } else {
        // Si falló, reducir el intervalo
        interval = Math.max(1, Math.floor(interval / 2));
    }
    
    return interval;
}

// Función para actualizar las estadísticas de una pregunta
async function updateQuestionStats(question, remembered) {
    const stats = question.stats;
    const now = new Date();
    
    // Actualizar contadores
    if (remembered) {
        stats.correct_count++;
    } else {
        stats.incorrect_count++;
    }
    
    // Actualizar fechas y intervalos
    stats.last_reviewed = now.toISOString();
    stats.interval = calculateNextInterval(question, remembered);
    
    // Calcular próxima fecha de revisión
    const nextReview = new Date(now);
    nextReview.setDate(nextReview.getDate() + stats.interval);
    stats.next_review = nextReview.toISOString();
    
    try {
        const response = await fetch('/update_question_stats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(question)
        });
        
        if (!response.ok) {
            console.error('Error actualizando estadísticas');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Mostrar la pregunta actual
function showQuestion() {
    const questionElement = document.getElementById('currentQuestion');
    const answerContainer = document.querySelector('.answer-container');
    const answerButtons = document.querySelector('.answer-buttons');
    
    if (currentQuestionIndex >= questions.length) {
        // Si se acabaron las preguntas, volver a cargar
        currentQuestionIndex = 0;
        prioritizeQuestions();
        
        if (questions.length === 0) {
            questionElement.textContent = '¡Has completado todas las preguntas por ahora! Vuelve más tarde para repasar.';
            answerButtons.style.display = 'none';
            return;
        }
    }
    
    const currentQuestion = questions[currentQuestionIndex];
    questionElement.textContent = currentQuestion.question;
    
    // Mostrar estadísticas si existen
    if (currentQuestion.stats) {
        const totalAttempts = currentQuestion.stats.correct_count + currentQuestion.stats.incorrect_count;
        if (totalAttempts > 0) {
            const successRate = Math.round((currentQuestion.stats.correct_count / totalAttempts) * 100);
            questionElement.textContent += `\n\nTasa de éxito: ${successRate}%`;
        }
    }
    
    // Resetear la interfaz
    answerContainer.style.display = 'none';
    answerButtons.style.display = 'flex';
}

// Manejar la respuesta del usuario
async function handleAnswer(remembered, event) {
    event.preventDefault();
    event.stopPropagation();
    
    const currentQuestion = questions[currentQuestionIndex];
    const answerContainer = document.querySelector('.answer-container');
    const answerText = document.querySelector('.answer-text');
    const feedbackText = document.querySelector('.feedback-text');
    const answerButtons = document.querySelector('.answer-buttons');
    
    // Actualizar estadísticas
    await updateQuestionStats(currentQuestion, remembered);
    
    // Mostrar la respuesta
    answerText.textContent = currentQuestion.answer;
    
    // Mostrar feedback según si el usuario recordó o no
    feedbackText.textContent = remembered ? 
        '¡Excelente! La próxima revisión será en ' + currentQuestion.stats.interval + ' días.' : 
        'No te preocupes, repasaremos esta pregunta más frecuentemente.';
    
    // Actualizar la interfaz
    answerContainer.style.display = 'block';
    answerButtons.style.display = 'none';
    
    // Mantener el contenedor expandido
    const quizContainer = document.querySelector('.cuestionario');
    quizContainer.classList.add('expanded');
    quizContainer.classList.remove('contracted');
}

// Pasar a la siguiente pregunta
function nextQuestion(event) {
    // Prevenir el comportamiento por defecto
    event.preventDefault();
    event.stopPropagation();
    
    currentQuestionIndex++;
    showQuestion();
    
    // Mantener el contenedor expandido
    const quizContainer = document.querySelector('.cuestionario');
    quizContainer.classList.add('expanded');
    quizContainer.classList.remove('contracted');
}

// Funciones para el modal de agregar preguntas
function openAddQuestionModal(event) {
    // Prevenir que el evento se propague al contenedor padre
    event.preventDefault();
    event.stopPropagation();
    
    const modal = document.getElementById('addQuestionModal');
    modal.style.display = 'flex';
    
    // Mantener el contenedor expandido
    const quizContainer = document.querySelector('.cuestionario');
    quizContainer.classList.add('expanded');
    quizContainer.classList.remove('contracted');
}

function closeAddQuestionModal(event) {
    // Prevenir que el evento se propague al contenedor padre
    event.preventDefault();
    event.stopPropagation();
    
    const modal = document.getElementById('addQuestionModal');
    modal.style.display = 'none';
    
    // Limpiar los campos del formulario
    document.getElementById('newQuestion').value = '';
    document.getElementById('newAnswer').value = '';
    document.getElementById('newCategory').value = '';
    
    // Mantener el contenedor expandido
    const quizContainer = document.querySelector('.cuestionario');
    quizContainer.classList.add('expanded');
    quizContainer.classList.remove('contracted');
}

async function saveNewQuestion(event) {
    // Prevenir que el evento se propague al contenedor padre
    event.preventDefault();
    event.stopPropagation();
    
    const question = document.getElementById('newQuestion').value.trim();
    const answer = document.getElementById('newAnswer').value.trim();
    const category = document.getElementById('newCategory').value.trim();

    if (!question || !answer || !category) {
        alert('Por favor completa todos los campos');
        return;
    }

    try {
        const response = await fetch('/add_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                answer: answer,
                category: category
            })
        });

        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                alert('Pregunta agregada exitosamente');
                closeAddQuestionModal(event);
                // Recargar las preguntas
                loadQuestions();
            } else {
                alert('Error al guardar la pregunta: ' + result.message);
            }
        } else {
            alert('Error al guardar la pregunta');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al guardar la pregunta');
    }
    
    // Mantener el contenedor expandido
    const quizContainer = document.querySelector('.cuestionario');
    quizContainer.classList.add('expanded');
    quizContainer.classList.remove('contracted');
}

// Prevenir que los clics dentro del modal se propaguen al contenedor padre
document.addEventListener('DOMContentLoaded', function() {
    const modalContent = document.querySelector('.modal-content');
    if (modalContent) {
        modalContent.addEventListener('click', function(event) {
            // Solo detener la propagación si el clic no fue en un input o textarea
            if (!event.target.matches('input, textarea')) {
                event.stopPropagation();
            }
        });
    }
    
    // Prevenir que los inputs pierdan el foco del contenedor
    const formInputs = document.querySelectorAll('.form-group input, .form-group textarea');
    formInputs.forEach(input => {
        input.addEventListener('click', function(event) {
            // No detener la propagación para permitir el foco
            const quizContainer = document.querySelector('.cuestionario');
            quizContainer.classList.add('expanded');
            quizContainer.classList.remove('contracted');
        });
        
        // Agregar listener para el foco
        input.addEventListener('focus', function(event) {
            const quizContainer = document.querySelector('.cuestionario');
            quizContainer.classList.add('expanded');
            quizContainer.classList.remove('contracted');
        });
    });
    
    // Prevenir que el modal se cierre al hacer clic en él
    const modal = document.getElementById('addQuestionModal');
    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                event.preventDefault();
                event.stopPropagation();
                closeAddQuestionModal(event);
            }
        });
    }
}); 