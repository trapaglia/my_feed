let currentQuestion = null;
let questions = [];

// Función para cargar las preguntas desde el archivo JSON
async function loadQuestions() {
    try {
        const response = await fetch('/static/data/questions.json');
        const data = await response.json();
        questions = data.questions;
        if (questions.length > 0) {
            showRandomQuestion();
        }
    } catch (error) {
        console.error('Error cargando las preguntas:', error);
    }
}

// Función para mostrar una pregunta aleatoria
function showRandomQuestion() {
    if (questions.length === 0) return;
    
    const index = Math.floor(Math.random() * questions.length);
    currentQuestion = questions[index];
    
    document.getElementById('currentQuestion').textContent = currentQuestion.question;
    
    // Manejar la imagen de la pregunta
    const imageContainer = document.getElementById('questionImageContainer');
    const questionImage = document.getElementById('questionImage');
    
    if (currentQuestion.image) {
        questionImage.src = `/static/${currentQuestion.image}`;
        imageContainer.style.display = 'block';
    } else {
        imageContainer.style.display = 'none';
    }
    
    // Resetear la interfaz
    document.querySelector('.answer-container').style.display = 'none';
    document.querySelector('.evaluation-buttons').style.display = 'none';
    document.querySelector('.answer-buttons').style.display = 'flex';
}

// Función para mostrar la respuesta
function showAnswer(event) {
    event.preventDefault();
    if (!currentQuestion) return;
    
    document.querySelector('.answer-container').style.display = 'block';
    document.querySelector('.answer-text').textContent = currentQuestion.answer;
    document.querySelector('.evaluation-buttons').style.display = 'flex';
    document.querySelector('.answer-buttons').style.display = 'none';
}

// Función para manejar la respuesta del usuario
async function handleAnswer(remembered, event) {
    event.preventDefault();
    if (!currentQuestion) return;
    
    const feedbackText = document.querySelector('.feedback-text');
    feedbackText.textContent = remembered ? '¡Bien hecho!' : 'Sigue practicando';
    feedbackText.style.color = remembered ? '#2ecc71' : '#e74c3c';
    
    // Actualizar estadísticas
    const stats = currentQuestion.stats;
    if (remembered) {
        stats.correct_count++;
    } else {
        stats.incorrect_count++;
    }
    
    stats.last_reviewed = new Date().toISOString();
    
    // Calcular próxima revisión usando el algoritmo SM-2
    if (remembered) {
        stats.interval = stats.interval * 2;
    } else {
        stats.interval = 1;
    }
    
    const nextReview = new Date();
    nextReview.setDate(nextReview.getDate() + stats.interval);
    stats.next_review = nextReview.toISOString();
    
    try {
        const response = await fetch('/update_question_stats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: currentQuestion.id,
                stats: stats
            }),
        });
        
        if (!response.ok) {
            throw new Error('Error actualizando estadísticas');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Función para pasar a la siguiente pregunta
function nextQuestion(event) {
    event.preventDefault();
    showRandomQuestion();
}

// Función para abrir el modal de nueva pregunta
function openAddQuestionModal(event) {
    event.preventDefault();
    document.getElementById('addQuestionModal').style.display = 'flex';
    // Limpiar el formulario
    document.getElementById('newQuestion').value = '';
    document.getElementById('newAnswer').value = '';
    document.getElementById('newCategory').value = '';
    document.getElementById('newImage').value = '';
    document.getElementById('imagePreview').style.display = 'none';
}

// Función para cerrar el modal
function closeAddQuestionModal(event) {
    event.preventDefault();
    document.getElementById('addQuestionModal').style.display = 'none';
}

// Función para previsualizar la imagen
function handleImagePreview(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Función para guardar una nueva pregunta
async function saveNewQuestion(event) {
    event.preventDefault();
    
    const question = document.getElementById('newQuestion').value.trim();
    const answer = document.getElementById('newAnswer').value.trim();
    const category = document.getElementById('newCategory').value.trim();
    const imageFile = document.getElementById('newImage').files[0];
    
    if (!question || !answer || !category) {
        alert('Por favor completa todos los campos requeridos');
        return;
    }
    
    const formData = {
        question: question,
        answer: answer,
        category: category
    };
    
    // Si hay una imagen, convertirla a base64
    if (imageFile) {
        const reader = new FileReader();
        reader.onload = async function(e) {
            formData.image = e.target.result;
            await submitQuestion(formData);
        };
        reader.readAsDataURL(imageFile);
    } else {
        await submitQuestion(formData);
    }
}

// Función auxiliar para enviar la pregunta al servidor
async function submitQuestion(formData) {
    try {
        const response = await fetch('/add_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            closeAddQuestionModal(new Event('click'));
            await loadQuestions();
        } else {
            alert(result.message || 'Error al guardar la pregunta');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al guardar la pregunta');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadQuestions();
    document.getElementById('newImage').addEventListener('change', handleImagePreview);
}); 