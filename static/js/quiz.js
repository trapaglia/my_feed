let questions = [];
let currentQuestionIndex = 0;

// Cargar las preguntas al iniciar
fetch('/static/data/questions.json')
    .then(response => response.json())
    .then(data => {
        questions = data.questions;
        shuffleQuestions();
        showQuestion();
    })
    .catch(error => {
        console.error('Error cargando las preguntas:', error);
        document.getElementById('currentQuestion').textContent = 'Error cargando las preguntas';
    });

// Función para mezclar las preguntas
function shuffleQuestions() {
    for (let i = questions.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [questions[i], questions[j]] = [questions[j], questions[i]];
    }
}

// Mostrar la pregunta actual
function showQuestion() {
    const questionElement = document.getElementById('currentQuestion');
    const answerContainer = document.querySelector('.answer-container');
    const answerButtons = document.querySelector('.answer-buttons');
    
    if (currentQuestionIndex >= questions.length) {
        // Si se acabaron las preguntas, volver a empezar
        currentQuestionIndex = 0;
        shuffleQuestions();
    }
    
    const currentQuestion = questions[currentQuestionIndex];
    questionElement.textContent = currentQuestion.question;
    
    // Resetear la interfaz
    answerContainer.style.display = 'none';
    answerButtons.style.display = 'flex';
}

// Manejar la respuesta del usuario
function handleAnswer(remembered, event) {
    // Prevenir el comportamiento por defecto
    event.preventDefault();
    event.stopPropagation();
    
    const currentQuestion = questions[currentQuestionIndex];
    const answerContainer = document.querySelector('.answer-container');
    const answerText = document.querySelector('.answer-text');
    const feedbackText = document.querySelector('.feedback-text');
    const answerButtons = document.querySelector('.answer-buttons');
    
    // Mostrar la respuesta
    answerText.textContent = currentQuestion.answer;
    
    // Mostrar feedback según si el usuario recordó o no
    feedbackText.textContent = remembered ? 
        '¡Excelente! Sigamos practicando.' : 
        'No te preocupes, con práctica lo recordarás mejor.';
    
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