from flask import Flask, render_template

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

if __name__ == '__main__':
    app.run(debug=True)
