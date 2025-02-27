from flask import Flask, render_template, send_from_directory, jsonify, request
import random
import json
from datetime import datetime
import os
from paper_fetchers import fetch_arxiv_papers, fetch_papers_with_code, fetch_google_scholar, fetch_twitter_papers
from paper_storage import should_update_papers, get_stored_papers, update_source_papers
from recipe_fetcher import get_daily_recipe
from threading import Thread
import logging
import base64
from werkzeug.utils import secure_filename

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images/questions'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Variable global para almacenar el estado de carga
loading_status = {
    'arxiv': {'status': 'pending', 'papers': []},
    'papers_with_code': {'status': 'pending', 'papers': []},
    'google_scholar': {'status': 'pending', 'papers': []},
    'twitter': {'status': 'pending', 'papers': []}
}

def get_daily_phrase():
    # Ruta al archivo que almacenará la frase del día
    base_dir = '/home/matiasdanmansilla/projects/my_feed/'
    if __name__ == '__main__':
        base_dir = ''
    storage_file = os.path.join(base_dir, 'static/data/daily_phrase.json')

    # Obtener la fecha actual (solo año, mes, día)
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Intentar leer la frase almacenada
        if os.path.exists(storage_file):
            with open(storage_file, 'r') as f:
                stored_data = json.load(f)
                
            # Si la frase es de hoy, usarla
            if stored_data.get('date') == today:
                return stored_data['phrase']
    except:
        pass  # Si hay algún error, simplemente seleccionar una nueva frase
    
    # Si no hay frase almacenada o es de otro día, seleccionar una nueva
    frases = [
        {
            "texto": "Vortelyx do a general body scan",
            "categoria": "Meditación"
        },
        {
            "texto": "Focus your energy on your aura goal",
            "categoria": "Energía"
        },
        {
            "texto": "Today focus on the root, sacral chakra",
            "categoria": "Chakras"
        },
        {
            "texto": "Today focus on the solar plexus chakra",
            "categoria": "Chakras"
        },
        {
            "texto": "Today focus on the heart chakra",
            "categoria": "Chakras"
        },
        {
            "texto": "Today focus on the throat chakra",
            "categoria": "Chakras"
        },
        {
            "texto": "Today focus on the third eye chakra",
            "categoria": "Chakras"
        },
        {
            "texto": "Today focus on the crown chakra",
            "categoria": "Chakras"
        }
    ]
    
    # Seleccionar una nueva frase aleatoria
    frase_del_dia = random.choice(frases)
    
    # Almacenar la nueva frase con la fecha actual
    with open(storage_file, 'w') as f:
        json.dump({
            'date': today,
            'phrase': frase_del_dia
        }, f)
    
    return frase_del_dia

def async_fetch_papers(source):
    """Función para cargar papers de forma asíncrona"""
    global loading_status
    try:
        logger.info(f"Iniciando carga de papers para {source}")
        
        # Verificar si debemos actualizar los papers
        if not should_update_papers():
            logger.info(f"No es necesario actualizar papers para {source}, usando datos almacenados")
            stored_papers = get_stored_papers()
            loading_status[source] = {
                'status': 'completed',
                'papers': stored_papers.get(source, [])
            }
            return

        # Si es necesario actualizar, proceder con la descarga
        logger.info(f"Actualizando papers para {source}")
        papers = []
        if source == 'arxiv':
            papers = fetch_arxiv_papers()
        elif source == 'papers_with_code':
            papers = fetch_papers_with_code()
        elif source == 'google_scholar':
            papers = fetch_google_scholar()
        elif source == 'twitter':
            papers = fetch_twitter_papers()
        
        if papers:
            # Actualizar el almacenamiento solo si obtuvimos papers
            update_source_papers(source, papers)
            loading_status[source] = {
                'status': 'completed',
                'papers': papers
            }
            logger.info(f"Actualización exitosa para {source}: {len(papers)} papers obtenidos")
        else:
            raise Exception(f"No se obtuvieron papers de {source}")
            
    except Exception as e:
        logger.error(f"Error cargando papers de {source}: {str(e)}")
        # Si hay error, intentar cargar los datos almacenados como fallback
        try:
            stored_papers = get_stored_papers()
            stored_source_papers = stored_papers.get(source, [])
            if stored_source_papers:
                loading_status[source] = {
                    'status': 'completed',
                    'papers': stored_source_papers,
                    'warning': 'Usando datos almacenados debido a un error de actualización'
                }
                logger.info(f"Usando datos almacenados como fallback para {source}")
                return
        except Exception as backup_error:
            logger.error(f"Error al intentar cargar datos almacenados para {source}: {str(backup_error)}")
        
        loading_status[source] = {
            'status': 'error',
            'papers': [],
            'error': f"Error cargando papers: {str(e)}. Por favor intenta más tarde."
        }

@app.route('/fetch_papers/<source>')
def fetch_papers(source):
    """Endpoint para iniciar la carga asíncrona de papers"""
    global loading_status
    
    if source in loading_status and loading_status[source]['status'] == 'pending':
        # Iniciar carga asíncrona
        thread = Thread(target=async_fetch_papers, args=(source,))
        thread.start()
    
    return jsonify(loading_status[source])

@app.route('/paper_status/<source>')
def paper_status(source):
    """Endpoint para verificar el estado de carga de papers"""
    return jsonify(loading_status[source])

@app.route('/')
@app.route('/index')
def index():
    # Reiniciar el estado de carga
    global loading_status
    loading_status = {
        'arxiv': {'status': 'pending', 'papers': []},
        'papers_with_code': {'status': 'pending', 'papers': []},
        'google_scholar': {'status': 'pending', 'papers': []},
        'twitter': {'status': 'pending', 'papers': []}
    }
    
    # Definir receta por defecto
    receta_del_dia = {
        'title': 'Ensalada Mediterránea',
        'summary': 'Una refrescante ensalada con tomates, pepinos, aceitunas y queso feta.',
        'sourceUrl': 'https://www.recetasgratis.net/receta-de-ensalada-mediterranea-59615.html',
        'image': '',
        'readyInMinutes': 15,
        'servings': 4
    }
    
    try:
        logger.info("Obteniendo frase del día...")
        frase_del_dia = get_daily_phrase()
        
        logger.info("Obteniendo receta del día...")
        receta_temp = get_daily_recipe()
        if receta_temp:
            logger.info("Receta obtenida exitosamente")
            receta_del_dia = receta_temp
        else:
            logger.warning("No se pudo obtener la receta, usando receta por defecto")
            
    except Exception as e:
        logger.error(f"Error obteniendo datos diarios: {str(e)}")
        frase_del_dia = {
            "texto": "Focus your energy on your aura goal",
            "categoria": "Energía"
        }
    
    logger.info(f"Renderizando template con receta: {receta_del_dia}")
    return render_template('index.html', 
                         title='Daily Inspiration',
                         frase=frase_del_dia,
                         receta=receta_del_dia,
                         loading_status=loading_status)

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('static/css', filename)

@app.route('/js/<path:filename>')
def js(filename):
    return send_from_directory('static/js', filename)

@app.route('/static/data/<path:filename>')
def data(filename):
    return send_from_directory('static/data', filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_question', methods=['POST'])
def add_question():
    try:
        data = request.get_json()
        logger.info(f"Recibiendo nueva pregunta: {data}")
        
        # Validar los datos recibidos
        if not all(key in data for key in ['question', 'answer', 'category']):
            logger.error("Faltan campos requeridos en la pregunta")
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400
            
        # Procesar la imagen si está presente
        image_path = None
        if 'image' in data and data['image']:
            try:
                # Decodificar la imagen base64
                image_data = base64.b64decode(data['image'].split(',')[1])
                # Crear un nombre único para la imagen
                filename = secure_filename(f"question_{len(get_stored_questions()) + 1}.jpg")
                # Asegurar que el directorio existe
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                # Guardar la imagen
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                # Convertir la ruta a relativa para almacenamiento
                image_path = os.path.join('images/questions', filename)
            except Exception as e:
                logger.error(f"Error procesando la imagen: {str(e)}")
                return jsonify({'success': False, 'message': f'Error procesando la imagen: {str(e)}'}), 500

        # Definir la ruta correcta al archivo questions.json
        questions_file = os.path.join('static', 'data', 'questions.json')
        logger.info(f"Intentando guardar pregunta en: {questions_file}")
        
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(questions_file), exist_ok=True)
        
        # Cargar las preguntas existentes o crear estructura inicial
        try:
            if os.path.exists(questions_file):
                with open(questions_file, 'r', encoding='utf-8') as file:
                    questions_data = json.load(file)
            else:
                questions_data = {"questions": []}
        except Exception as e:
            logger.error(f"Error leyendo el archivo de preguntas: {str(e)}")
            questions_data = {"questions": []}
            
        # Crear nueva pregunta con ID y estadísticas iniciales
        new_id = len(questions_data["questions"]) + 1
        new_question = {
            'id': new_id,
            'question': data['question'],
            'answer': data['answer'],
            'category': data['category'],
            'image': image_path,
            'stats': {
                'correct_count': 0,
                'incorrect_count': 0,
                'last_reviewed': None,
                'next_review': None,
                'interval': 1
            }
        }
        
        # Agregar la nueva pregunta
        questions_data["questions"].append(new_question)
        
        # Guardar el archivo actualizado
        try:
            with open(questions_file, 'w', encoding='utf-8') as file:
                json.dump(questions_data, file, ensure_ascii=False, indent=4)
            logger.info("Pregunta guardada exitosamente")
            return jsonify({'success': True, 'message': 'Pregunta agregada exitosamente'})
        except Exception as e:
            logger.error(f"Error escribiendo en el archivo: {str(e)}")
            return jsonify({'success': False, 'message': f'Error al guardar la pregunta: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error general al guardar la pregunta: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al guardar la pregunta: {str(e)}'}), 500

def get_stored_questions():
    """Función auxiliar para obtener las preguntas almacenadas"""
    questions_file = os.path.join('static', 'data', 'questions.json')
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as file:
            return json.load(file)["questions"]
    return []

@app.route('/update_question_stats', methods=['POST'])
def update_question_stats():
    try:
        question = request.get_json()
        logger.info(f"Actualizando estadísticas para pregunta ID: {question.get('id')}")
        
        # Validar los datos recibidos
        if not question or 'id' not in question or 'stats' not in question:
            logger.error("Datos inválidos en la actualización de estadísticas")
            return jsonify({'success': False, 'message': 'Datos inválidos'}), 400
            
        # Cargar las preguntas existentes
        questions_file = os.path.join('static', 'data', 'questions.json')
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as file:
                questions_data = json.load(file)
        except FileNotFoundError:
            logger.error("Archivo de preguntas no encontrado")
            return jsonify({'success': False, 'message': 'Archivo de preguntas no encontrado'}), 404
            
        # Actualizar la pregunta específica
        updated = False
        for i, q in enumerate(questions_data['questions']):
            if q['id'] == question['id']:
                questions_data['questions'][i]['stats'] = question['stats']
                updated = True
                break
        
        if not updated:
            logger.error(f"No se encontró la pregunta con ID: {question['id']}")
            return jsonify({'success': False, 'message': 'Pregunta no encontrada'}), 404
        
        # Guardar los cambios
        try:
            with open(questions_file, 'w', encoding='utf-8') as file:
                json.dump(questions_data, file, ensure_ascii=False, indent=4)
            logger.info("Estadísticas actualizadas exitosamente")
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error guardando las estadísticas: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500
            
    except Exception as e:
        logger.error(f"Error general actualizando estadísticas: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

# Ideas for improvements:
# Implementar un sistema de filtrado para los papers
# Agregar un sistema de guardado de papers favoritos
# Mejorar la sección del cuestionario
# Implementar la sección de recetas
# Mejorar la integración con el calendario