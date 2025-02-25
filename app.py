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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variable global para almacenar el estado de carga
loading_status = {
    'arxiv': {'status': 'pending', 'papers': []},
    'papers_with_code': {'status': 'pending', 'papers': []},
    'google_scholar': {'status': 'pending', 'papers': []},
    'twitter': {'status': 'pending', 'papers': []}
}

@app.route('/add_question', methods=['POST'])
def add_question():
    try:
        data = request.get_json()
        
        # Validar los datos recibidos
        if not all(key in data for key in ['question', 'answer', 'category']):
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400
            
        # Definir la ruta correcta al archivo questions.json
        questions_file = os.path.join('static', 'data', 'questions.json')
        logger.info(f"Intentando guardar pregunta en: {questions_file}")
        
        # Cargar las preguntas existentes
        try:
            with open(questions_file, 'r', encoding='utf-8') as file:
                questions_data = json.load(file)
        except FileNotFoundError:
            questions_data = {"questions": []}
            
        # Crear nueva pregunta con ID
        new_id = len(questions_data["questions"]) + 1
        new_question = {
            'id': new_id,
            'question': data['question'],
            'answer': data['answer'],
            'category': data['category']
        }
        
        # Agregar la nueva pregunta
        questions_data["questions"].append(new_question)
        
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(questions_file), exist_ok=True)
        
        # Guardar el archivo actualizado
        with open(questions_file, 'w', encoding='utf-8') as file:
            json.dump(questions_data, file, ensure_ascii=False, indent=4)
            
        logger.info("Pregunta guardada exitosamente")
        return jsonify({'success': True, 'message': 'Pregunta agregada exitosamente'})
        
    except Exception as e:
        logger.error(f"Error al guardar la pregunta: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al guardar la pregunta: {str(e)}'}), 500

@app.route('/update_question_stats', methods=['POST'])
def update_question_stats():
    try:
        question = request.get_json()
        
        # Validar los datos recibidos
        if not question or 'id' not in question or 'stats' not in question:
            return jsonify({'success': False, 'message': 'Datos inválidos'}), 400
            
        # Cargar las preguntas existentes
        questions_file = os.path.join('static', 'data', 'questions.json')
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as file:
                questions_data = json.load(file)
        except FileNotFoundError:
            return jsonify({'success': False, 'message': 'Archivo de preguntas no encontrado'}), 404
            
        # Actualizar la pregunta específica
        for i, q in enumerate(questions_data['questions']):
            if q['id'] == question['id']:
                questions_data['questions'][i]['stats'] = question['stats']
                break
        
        # Guardar los cambios
        with open(questions_file, 'w', encoding='utf-8') as file:
            json.dump(questions_data, file, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error actualizando estadísticas: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

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
    
    frase_del_dia = get_daily_phrase()
    receta_del_dia = get_daily_recipe()
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

@app.route('/fetch_papers/<source>')
def fetch_papers(source):
    """Endpoint para iniciar la carga asíncrona de papers"""
    global loading_status
    
    if source not in loading_status:
        return jsonify({'status': 'error', 'message': 'Fuente no válida'}), 400
        
    try:
        if source == 'arxiv':
            papers = fetch_arxiv_papers()
        elif source == 'papers_with_code':
            papers = fetch_papers_with_code()
        elif source == 'google_scholar':
            papers = fetch_google_scholar()
        elif source == 'twitter':
            papers = fetch_twitter_papers()
            
        if papers:
            loading_status[source] = {
                'status': 'completed',
                'papers': papers
            }
        else:
            # Intentar cargar datos almacenados
            stored_papers = get_stored_papers()
            if source in stored_papers and stored_papers[source]:
                loading_status[source] = {
                    'status': 'completed',
                    'papers': stored_papers[source],
                    'warning': 'Usando datos almacenados'
                }
            else:
                loading_status[source] = {
                    'status': 'error',
                    'papers': [],
                    'error': 'No se pudieron obtener papers'
                }
    except Exception as e:
        logger.error(f"Error cargando papers de {source}: {str(e)}")
        # Intentar cargar datos almacenados como fallback
        try:
            stored_papers = get_stored_papers()
            if source in stored_papers and stored_papers[source]:
                loading_status[source] = {
                    'status': 'completed',
                    'papers': stored_papers[source],
                    'warning': 'Usando datos almacenados debido a un error'
                }
            else:
                loading_status[source] = {
                    'status': 'error',
                    'papers': [],
                    'error': f'Error: {str(e)}'
                }
        except Exception as backup_error:
            loading_status[source] = {
                'status': 'error',
                'papers': [],
                'error': f'Error: {str(e)}'
            }
    
    return jsonify(loading_status[source])

@app.route('/paper_status/<source>')
def paper_status(source):
    """Endpoint para verificar el estado de carga de papers"""
    if source not in loading_status:
        return jsonify({'status': 'error', 'message': 'Fuente no válida'}), 400
    return jsonify(loading_status[source])

if __name__ == '__main__':
    app.run(debug=True) 