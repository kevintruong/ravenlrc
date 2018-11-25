import os
import time

from flask import Flask, render_template, request, flash, redirect
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
import asyncio
from flask import Flask
from Model.youtubemv import handle_input_video, handle_new_lyric
from View.view import AffectForm, MvInput, LyricForm
from db.models import get_db

app = Flask(__name__)
loop = asyncio.get_event_loop()
app.config['SECRET_KEY'] = 'any secret string'


# MySQL configurations


def init_db():
    db = get_db()
    with app.open_resource('db/youtubeCreator.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


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


@app.route('/inputmv', methods=['GET', 'POST'])
def mvinput():
    """
    submit redirect to confirm (preview page) to display current affect will add to database
    """
    mvinput = MvInput(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST':
        # start_time = time.time()
        # loop.run_until_complete(mvinput.handle_new_mv())
        # print("--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        mvinput.handle_new_mv()
        print("--- %s seconds ---" % (time.time() - start_time))
        # mvinput.handle_new_mv()
        return render_template('inputmv.html', form=mvinput)
    return render_template('inputmv.html', form=mvinput)


@app.route('/newaffect', methods=['GET', 'POST'])
def newaffect():
    """
    Add an affect
    submit redirect to confirm (preview page) to display current affect will add to database
    """

    form = AffectForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST':
        if 'affectMv' in request.files:
            print("found file {} in files upload".format(request.files['affectMv']))
        return render_template('newaffect.html', form=form)
    return render_template('newaffect.html', form=form)


@app.route('/result', methods=['GET'])
def result():
    """
    Add an affect
    submit redirect to confirm (preview page) to display current affect will add to database
    """

    form = AffectForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST':
        if 'affectMv' in request.files:
            print("found file {} in files upload".format(request.files['affectMv']))
        return render_template('result.html', form=form)
    return render_template('result.html', form=form)


@app.route('/newlyric', methods=['GET', 'POST'])
def newlyric():
    """
    Add an affect
    submit redirect to confirm (preview page) to display current affect will add to database
    """

    form = LyricForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST':
        handle_new_lyric(form)
        return 'upload a lyric '

    return render_template('newlyric.html', form=form)


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
