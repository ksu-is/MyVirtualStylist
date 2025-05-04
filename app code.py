from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'style_secret_key'

UPLOAD_FOLDER = 'static/uploads'
FAV_FILE = 'favorites.json'
SEASONS = ['summer', 'fall', 'winter', 'spring']
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure season folders exist
for season in SEASONS:
    os.makedirs(os.path.join(UPLOAD_FOLDER, season), exist_ok=True)

# Load favorites or create empty
if os.path.exists(FAV_FILE):
    with open(FAV_FILE, 'r') as f:
        favorites = json.load(f)
else:
    favorites = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_favorites():
    with open(FAV_FILE, 'w') as f:
        json.dump(favorites, f)

@app.route('/')
def index():
    if 'name' in session:
        name = session['name']
        tone = session.get('tone', '')
        if name.lower() in ['user', 'guest', '']:
            flash("Don't forget to personalize your username for a stylish welcome! ✨")
        return render_template('index.html', name=name, tone=tone)
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        session['tone'] = request.form['tone']
        session['color_theory'] = request.form['color_theory']
        session['name'] = request.form['name'].strip().title()
        return redirect(url_for('index'))
    return render_template('quiz.html')

@app.route('/closet')
def closet():
    season_clothes = {}
    for season in SEASONS:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], season)
        season_clothes[season] = os.listdir(folder_path)
    return render_template('closet.html', season_clothes=season_clothes)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files or 'season' not in request.form:
        return redirect(url_for('index'))
    file = request.files['file']
    season = request.form['season'].lower()

    if file.filename == '' or season not in SEASONS:
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], season, filename)
        file.save(save_path)
        return redirect(url_for('closet'))
    return redirect(url_for('index'))

@app.route('/suggest')
def suggest():
    suggestions = []
    for season in SEASONS:
        season_folder = os.path.join(app.config['UPLOAD_FOLDER'], season)
        clothes = os.listdir(season_folder)
        if clothes:
            suggestions.append(os.path.join(season, clothes[0]))
    return render_template('suggest.html', suggestion=suggestions)

@app.route('/favorite/<season>/<filename>')
def favorite(season, filename):
    user = session.get('name', 'guest')
    user_favs = favorites.get(user, [])
    full_path = f"{season}/{filename}"
    if full_path not in user_favs:
        user_favs.append(full_path)
    favorites[user] = user_favs
    save_favorites()
    flash("Added to your favorites! ⭐")
    return redirect(url_for('closet'))

@app.route('/favorites')
def show_favorites():
    user = session.get('name', 'guest')
    user_favs = favorites.get(user, [])
    return render_template('favorites.html', favorites=user_favs)

@app.route('/profile/<season>/<filename>')
def profile(season, filename):
    return render_template('profile.html', season=season, filename=filename)
