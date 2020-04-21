import face_recognition
import numpy as np
import pymysql.cursors
import os
import requests
from flask import Flask, request, make_response

app = Flask(__name__)

connection = pymysql.connect(host='petrodim.beget.tech',
                                 user='petrodim_test_db',
                                 password='M2&pWHkR',
                                 db='petrodim_test_db',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

UPLOAD_FOLDER = "images"
UPLOAD_FOLDER_FOR_FIND_FACE = "saved_images"
ALLOWED_EXTENSIONS = (['png', 'jpg', 'jpeg'])
sql_get_user = "SELECT user_id FROM user WHERE user_id=%s"
sql_get_path = "SELECT path FROM path_to_photo_of_user  WHERE user_id=%s"
sql_insert_path_photo = "INSERT INTO path_to_photo_of_user (path_to_photo_of_user_id, user_id, path) VALUES (NULL, %s, %s)"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_FOR_FIND_FACE'] = UPLOAD_FOLDER_FOR_FIND_FACE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return "Hello, world!"

@app.route('/api/v1/getPhoto/user/<int:user_id>', methods=['GET', 'POST'])
def send_photo_on_user_id(user_id):
    if request.method == 'GET':
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
                            path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                        if os.path.exists(path_to_image):
                            image = {"image": open(path_to_image, "rb")}
                            post_request = requests.post('http://localhost:5000/api/v1/savePhotoOnServer/user/6', files=image)
                            return post_request.text
                        else:
                            return make_response("Фото пользователя отсутствует на сервере", 400)
                    else:
                        return make_response("Для введённого user_id нет записи с фотографией в БД", 400)
                else:
                    return make_response("Введённый user_id отсутствует в БД", 400)
    else:
        return make_response("Разрешённый метод для данного запроса: GET", 400)

@app.route('/api/v1/savePhotoOnServer/user/<int:user_id>', methods=['GET', 'POST'])
def save_photo_on_server(user_id):
    if request.method == 'POST':
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) == 0:
                    return make_response("Введённый user_id отсутствует в БД", 400)
                else:
                    image = request.files.get('image')
                    path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                    if os.path.exists(path_to_image):
                        return make_response("Ошибка, фотография уже существует на сервере", 400)
                    else:
                        if image and allowed_file(image.filename):
                            cursor.execute(sql_insert_path_photo, (user_id, image.filename))
                            image.save(path_to_image)
                            if os.path.exists(path_to_image):
                                return make_response("Фотография успешно сохранена", 200)
                            else:
                                return make_response("Ошибка, фотография не сохранена", 400)
    else:
        return make_response("Разрешённый метод для данного запроса: POST", 400)

@app.route('/api/v1/findFaceOnPhoto', methods=['GET', 'POST'])
def find_face_on_photo():
    if request.method == 'POST':
        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT user_id, path FROM path_to_photo_of_user"
                cursor.execute(sql)
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

        image = request.files.get('image')
        path_to_image = os.path.join(app.config['UPLOAD_FOLDER_FOR_FIND_FACE'], image.filename)
        if image and allowed_file(image.filename):
            image.save(path_to_image)
        if not os.path.exists(path_to_image):
            return make_response("Ошибка, фотография не сохранена", 400)
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

        result = {'user_id': str_user_id}

        return result
    else:
        return make_response("Разрешённый метод для данного запроса: POST", 400)

if __name__ == '__main__':
    app.run(debug=True)
