from flask import Flask, render_template, send_from_directory
import random

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
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
    frase_del_dia = random.choice(frases)
    return render_template('index.html', 
                         title='Daily Inspiration',
                         frase=frase_del_dia)
    # return render_template('index.html', user=user)

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('css', filename)

if __name__ == '__main__':
    app.run(debug=True)
