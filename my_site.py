from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Matute'}
    # return render_template('index.html', title='Home', user=user)
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='', user=user, posts=posts)
    # return render_template('index.html', user=user)

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('css', filename)

if __name__ == '__main__':
    app.run(debug=True)
