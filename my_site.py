from flask import Flask, render_template, send_from_directory
import random

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    frases = ["Vortelyx do a general body scan",
              "Focus your energy on your aura goal",
              "Today focus on the root, sacral chakra",
              "Today focus on the solar plexus chakra",
              "Today focus on the heart chakra",
              "Today focus on the throat chakra",
              "Today focus on the third eye chakra",
              "Today focus on the crown chakra",]
    frase = random.choice(frases)
    return render_template('index.html', title='', frase=frase)
    # return render_template('index.html', user=user)

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('css', filename)

if __name__ == '__main__':
    app.run(debug=True)
