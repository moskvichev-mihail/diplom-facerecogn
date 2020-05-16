from flask import Flask
from app import constants

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_FOR_FIND_FACE'] = constants.UPLOAD_FOLDER_FOR_FIND_FACE

from app import routes
