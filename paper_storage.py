import json
import os
from datetime import datetime, timedelta

STORAGE_FILE = 'static/data/papers_database.json'
if not os.path.exists(STORAGE_FILE):
    STORAGE_FILE = '/home/matiasdanmansilla/my_feed/static/data/papers_database.json'

def should_update_papers():
    """
    Verifica si es necesario actualizar los papers basado en:
    1. Si es lunes
    2. Si han pasado más de 7 días desde la última actualización
    3. Si no hay datos almacenados
    """
    data = load_papers()
    
    # Si no hay última actualización, debemos actualizar
    if not data['last_update']:
        return True
    
    # Convertir la última actualización a datetime
    last_update = datetime.fromisoformat(data['last_update'])
    now = datetime.now()
    
    # Si es lunes y la última actualización fue hace más de 7 días
    is_monday = now.weekday() == 0
    days_since_update = (now - last_update).days
    
    return is_monday and days_since_update >= 7

def load_papers():
    """Carga los papers del archivo de almacenamiento"""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'last_update': None, 'papers': {'arxiv': [], 'papers_with_code': [], 'google_scholar': [], 'twitter': []}}
    return {'last_update': None, 'papers': {'arxiv': [], 'papers_with_code': [], 'google_scholar': [], 'twitter': []}}

def save_papers(papers_data):
    papers_data['last_update'] = datetime.now().isoformat()
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(papers_data, f, ensure_ascii=False, indent=2)

def update_source_papers(source, papers):
    """Actualiza los papers de una fuente específica y la fecha de última actualización"""
    data = load_papers()
    data['papers'][source] = papers
    data['last_update'] = datetime.now().isoformat()
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_stored_papers():
    """Obtiene los papers almacenados sin realizar nuevas descargas"""
    return load_papers()['papers'] 