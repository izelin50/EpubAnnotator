from flask import Flask
from database.db import init_db

init_db()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'epub_files'

from web_app import routes