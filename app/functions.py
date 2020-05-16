from app import constants
import pymysql


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in constants.ALLOWED_EXTENSIONS


def connect_to_db(host, user, password, db):
    connection = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    return connection

