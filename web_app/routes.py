import os
import sqlite3
from flask import render_template, request, redirect, url_for, send_file, abort
from werkzeug.utils import secure_filename
from web_app import app
from database.db import DB_PATH
from book_processor import process_book

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_profile', methods=['POST'])
def set_profile():
    name = request.form.get('name')
    language = request.form.get('language')
    level = request.form.get('level')
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO users (name, language, level) VALUES (?, ?, ?)', (name, language, level))
        conn.commit()
        user_id = c.lastrowid
    return redirect(url_for('upload', user_id=user_id))

@app.route('/upload/<int:user_id>')
def upload(user_id):
    return render_template('upload.html', user_id=user_id)

@app.route('/upload_file/<int:user_id>', methods=['POST'])
def upload_file(user_id):
    file = request.files.get('file')
    if file and file.filename.endswith('.epub'):
        filename = secure_filename(file.filename)
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        processed_path = process_book(file_path, user_id)

        if os.path.exists(processed_path):
            return send_file(processed_path, as_attachment=True)
        else:
            return "Ошибка при обработке файла.", 500

    return 'Недопустимый формат файла. Загрузите .epub.', 400