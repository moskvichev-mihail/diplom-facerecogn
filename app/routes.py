import face_recognition
import numpy as np
import pymysql
import os
import base64
from app import app
from flask import request, make_response, render_template

UPLOAD_FOLDER = "app/static/images"
UPLOAD_FOLDER_FOR_FIND_FACE = "app/static/saved_images"
ALLOWED_EXTENSIONS = (['png', 'jpg', 'jpeg'])

sql_get_all_users_photo = "SELECT user_id, path FROM path_to_photo_of_user"
sql_get_user = "SELECT user_id FROM user WHERE user_id=%s"
sql_get_path = "SELECT path FROM path_to_photo_of_user  WHERE user_id=%s"
sql_get_photo_id = "SELECT path_to_photo_of_user_id FROM path_to_photo_of_user  WHERE user_id=%s"
sql_insert_path_photo = "INSERT INTO path_to_photo_of_user (path_to_photo_of_user_id, user_id, path) VALUES (NULL, %s, %s)"
sql_delete_path_photo = "DELETE FROM `path_to_photo_of_user` WHERE `path_to_photo_of_user`.`path_to_photo_of_user_id` = %s"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_FOR_FIND_FACE'] = UPLOAD_FOLDER_FOR_FIND_FACE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def connect_to_db(host, user, password, db):
    connection = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    return connection

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/docs')
def docs():
    return render_template("docs.html", title="Документация")

@app.route('/api/v1/getPhoto/user/<int:user_id>', methods=['GET', 'POST'])
def send_photo_on_user_id(user_id):
    if request.method == 'GET':
        connection = connect_to_db('petrodim.beget.tech', 'petrodim_test_db', 'M2&pWHkR', 'petrodim_test_db')
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) != 0:
                    cursor.execute(sql_get_path, user_id)
                    result = cursor.fetchall()
                    if len(result) != 0:
                        cursor.execute(sql_get_path, user_id)
                        for row in cursor:
                            name_photo = row["path"]
                            path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                        #connection.close()
                        if os.path.exists(path_to_image):
                            # return send_from_directory(app.config['UPLOAD_FOLDER'], name_photo)
                            image = open(path_to_image, "rb")
                            image_read = image.read()
                            image_encode = base64.b64encode(image_read)
                            result = {'status_code': 200, 'image': str(image_encode)}
                            return make_response(result, 200)
                            #post_request = requests.post('http://localhost:5000/api/v1/savePhotoOnServer/user/6', files=image)
                            #return post_request.text
                        else:
                            result = {'status_code': 400, 'description': 'Фото пользователя отсутствует на сервере'}
                            return make_response(result, 400)
                    else:
                        result = {'status_code': 400, 'description': 'Для user_id нет записи с фотографией в БД'}
                        return make_response(result, 400)
                else:
                    result = {'status_code': 400, 'description': 'Введённый user_id отсутствует в БД'}
                    return make_response(result, 400)
    else:
        result = {'status_code': 400, 'description': 'Разрешённый метод для данного запроса: GET'}
        return make_response(result, 400)

@app.route('/api/v1/addPhoto/user/<int:user_id>', methods=['GET', 'POST'])
def save_photo_on_server(user_id):
    if request.method == 'POST':
        connection = connect_to_db('petrodim.beget.tech', 'petrodim_test_db', 'M2&pWHkR', 'petrodim_test_db')
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) == 0:
                    result = {'status_code': 400, 'description': 'Введённый user_id отсутствует в БД'}
                    return make_response(result, 400)
                else:
                    image = request.files.get('image')
                    path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                    if os.path.exists(path_to_image):
                        result = {'status_code': 400, 'description': 'Ошибка, фотография уже существует на сервере'}
                        return make_response(result, 400)
                    else:
                        if image and allowed_file(image.filename):
                            cursor.execute(sql_insert_path_photo, (user_id, image.filename))
                            image.save(path_to_image)
                            if os.path.exists(path_to_image):
                                result = {'status_code': 200, 'description': 'Фотография успешно сохранена'}
                                return make_response(result, 200)
                            else:
                                result = {'status_code': 400, 'description': 'Ошибка, фотография не сохранена'}
                                return make_response(result, 400)
                        else:
                            result = {'status_code': 400, 'description': 'Ошибка, разрешенный формат для фотографий: jpg, png, jpeg'}
                            return make_response(result, 400)
    else:
        result = {'status_code': 400, 'description': 'Разрешённый метод для данного запроса: POST'}
        return make_response(result, 400)

@app.route('/api/v1/updatePhoto/user/<int:user_id>', methods=['GET', 'PUT'])
def update_photo(user_id):
    if request.method == 'PUT':
        connection = connect_to_db('petrodim.beget.tech', 'petrodim_test_db', 'M2&pWHkR', 'petrodim_test_db')
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) == 0:
                    result = {'status_code': 400, 'description': 'Введённый user_id отсутствует в БД'}
                    return make_response(result, 400)
                else:
                    image = request.files.get('image')
                    path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                    cursor.execute(sql_get_path, user_id)
                    result = cursor.fetchall()
                    if len(result) != 0:
                        cursor.execute(sql_get_path, user_id)
                        for row in cursor:
                            sql_path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                        if os.path.exists(sql_path_to_image):
                            os.remove(sql_path_to_image)
                            image.save(path_to_image)
                            # update запрос к БД
                        else:
                            result = {'status_code': 400, 'description': 'Старое фото пользователя отсутствует на сервере'}
                            return make_response(result, 400)
                    else:
                        result = {'status_code': 400, 'description': 'Для user_id нет записи с фотографией в БД'}
                        return make_response(result, 400)
    else:
        result = {'status_code': 400, 'description': 'Разрешённый метод для данного запроса: PUT'}
        return make_response(result, 400)

@app.route('/api/v1/deletePhoto/user/<int:user_id>', methods=['GET', 'DELETE'])
def delete_photo_from_server(user_id):
    if request.method == 'DELETE':
        connection = connect_to_db('petrodim.beget.tech', 'petrodim_test_db', 'M2&pWHkR', 'petrodim_test_db')
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) == 0:
                    result = {'status_code': 400, 'description': 'Введённый user_id отсутствует в БД'}
                    return make_response(result, 400)
                else:
                    cursor.execute(sql_get_path, user_id)
                    for row in cursor:
                        path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                    if not os.path.exists(path_to_image):
                        result = {'status_code': 400, 'description': 'Ошибка, фотография отсутствует на сервере'}
                        return make_response(result, 400)
                    else:
                        cursor.execute(sql_get_photo_id, user_id)
                        for row in cursor:
                            path_id = row["path_to_photo_of_user_id"]
                        os.remove(path_to_image)
                        cursor.execute(sql_delete_path_photo, path_id)
                        #connection.close()
                        result = {'status_code': 200, 'description': 'Фотография успешно удалена'}
                        return make_response(result, 200)
    else:
        result = {'status_code': 400, 'description': 'Разрешённый метод для данного запроса: DELETE'}
        return make_response(result, 400)

@app.route('/api/v1/findFaceOnPhoto', methods=['GET', 'POST'])
def find_face_on_photo():
    if request.method == 'GET':
        connection = connect_to_db('petrodim.beget.tech', 'petrodim_test_db', 'M2&pWHkR', 'petrodim_test_db')
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_get_all_users_photo)
                known_faces_user_id = []
                known_faces_images_path = []
                known_face_encodings_images = []
                for row in cursor:
                    known_faces_user_id.append(row["user_id"])
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                    known_faces_images_path.append(image_path)
                    image = face_recognition.load_image_file(image_path)
                    image_face_encoding = face_recognition.face_encodings(image)[0]
                    known_face_encodings_images.append(image_face_encoding)
        #connection.close()
        image = request.files.get('image')
        path_to_image = os.path.join(app.config['UPLOAD_FOLDER_FOR_FIND_FACE'], image.filename)
        if image and allowed_file(image.filename):
            image.save(path_to_image)
        if not os.path.exists(path_to_image):
            result = {'status_code': 400, 'description': 'Ошибка, фотография не сохранена'}
            return make_response(result, 400)
        unknown_image = face_recognition.load_image_file(path_to_image)
        os.remove(path_to_image)

        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings_images, face_encoding)
            user_id = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings_images, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                user_id = known_faces_user_id[best_match_index]
            str_user_id = str(user_id)

        result = {'status_code': 200, 'user_id': str_user_id}

        return make_response(result, 200)
    else:
        result = {'status_code': 400, 'description': 'Разрешённый метод для данного запроса: GET'}
        return make_response(result, 400)
