import requests
import random
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
dotenv_path = "/home/matiasdanmansilla/my_feed/.env"
if not os.path.exists(dotenv_path):
    load_dotenv()
else:
    load_dotenv(dotenv_path)

STORAGE_FILE = 'static/data/daily_recipe.json'
if not os.path.exists(STORAGE_FILE):
    STORAGE_FILE = '/home/matiasdanmansilla/my_feed/static/data/daily_recipe.json'

def fetch_vegetarian_recipe():
    """Obtiene una receta vegetariana aleatoria de la API de Spoonacular"""
    api_key = os.getenv('SPOONACULAR_API_KEY')
    
    if not api_key:
        print("Error: No se encontró la API key de Spoonacular en el archivo .env")
        return None
    
    try:
        response = requests.get(
            'https://api.spoonacular.com/recipes/random',
            params={
                'apiKey': api_key,
                'tags': 'vegetarian',
                'number': 1
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'recipes' in data and len(data['recipes']) > 0:
                recipe = data['recipes'][0]
                return {
                    'title': recipe['title'],
                    'summary': recipe['summary'],
                    'sourceUrl': recipe['sourceUrl'],
                    'image': recipe.get('image', ''),
                    'readyInMinutes': recipe.get('readyInMinutes', 0),
                    'servings': recipe.get('servings', 0)
                }
        else:
            print(f"Error en la API de Spoonacular: {response.status_code}")
            print(f"Respuesta: {response.text}")
    except Exception as e:
        print(f"Error obteniendo receta: {str(e)}")
    return None

def get_daily_recipe():
    """Obtiene la receta del día o genera una nueva si es necesario"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                stored_data = json.load(f)
                if stored_data.get('date') == today:
                    return stored_data['recipe']
    except:
        pass

    # Si no hay receta almacenada o es de otro día, obtener una nueva
    recipe = fetch_vegetarian_recipe()
    
    if recipe:
        # Almacenar la nueva receta
        os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'date': today,
                'recipe': recipe
            }, f, ensure_ascii=False, indent=2)
        
        return recipe
    
    # Si no se pudo obtener una nueva receta, devolver una receta por defecto
    return {
        'title': 'Ensalada Mediterránea',
        'summary': 'Una refrescante ensalada con tomates, pepinos, aceitunas y queso feta.',
        'sourceUrl': 'https://www.recetasgratis.net/receta-de-ensalada-mediterranea-59615.html',
        'image': '',
        'readyInMinutes': 15,
        'servings': 4
    } 