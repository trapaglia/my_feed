from flask import Flask, render_template, send_from_directory
import random
import json
from datetime import datetime
import os
from paper_fetchers import fetch_arxiv_papers

app = Flask(__name__)

def get_daily_phrase():
    # Ruta al archivo que almacenará la frase del día
    storage_file = 'daily_phrase.json'
    
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
    arxiv_papers = fetch_arxiv_papers()
    frase_del_dia = get_daily_phrase()
    return render_template('index.html', 
                         title='Daily Inspiration',
                         frase=frase_del_dia,
                         arxiv_papers=arxiv_papers)
    # return render_template('index.html', user=user)

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def js(filename):
    return send_from_directory('static/js', filename)

if __name__ == '__main__':
    app.run(debug=True)
