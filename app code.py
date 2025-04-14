from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'style_secret'  # Needed for session
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'name' in session:
        name = session['name']
        tone = session['tone']
        return render_template('index.html', name=name, tone=tone)
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        session['tone'] = request.form['tone']
        session['color_theory'] = request.form['color_theory']
        session['name'] = request.form['name']
        return redirect(url_for('index'))
    return render_template('quiz.html')

@app.route('/closet')
def closet():
    clothes = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('closet.html', clothes=clothes)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('closet'))
    return redirect(url_for('index'))

@app.route('/suggest')
def suggest():
    clothes = os.listdir(app.config['UPLOAD_FOLDER'])
    suggestion = clothes[:2] if len(clothes) >= 2 else clothes
    return render_template('suggest.html', suggestion=suggestion)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
