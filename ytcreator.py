import os
from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
from View.view import AffectForm
from db.models import get_db

app = Flask(__name__)


# MySQL configurations


def init_db():
    db = get_db()
    with app.open_resource('db/youtubeCreator.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')


@app.route('/main')
def showMain():
    return render_template('index.html')


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'input-file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['input-file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join('/tmp/', filename))
            return '{} upload success'.format(filename)
    return 'hello world'


@app.route('/newaffect', methods=['GET', 'POST'])
def newaffect():
    """
    Add an affect
    submit redirect to confirm (preview page) to display current affect will add to database
    """
    form = AffectForm(request.form)
    return render_template('newaffect.html', form=form)


if __name__ == '__main__':
    # session = models.loadSession()
    # test = session.query(models.youtubemv).all()
    # table = session.query(models.lyric)
    # newaffect = models.affect(id=00, AffectFile='helloworld', Opacity=50)
    # session.add(newaffect)
    # session.commit()
    # res = session.query(models.affect).all()
    # print("{}".format(res[1].title))

    app.run(port=5000, debug=True)
