import face_recognition
import numpy as np
import pymysql.cursors
from flask import Flask, request, make_response, send_from_directory

# Для запуска виртуального окружения зайти в папку с проектом и написать source flask-env/bin/activate
# python app.py для запуска исполняемого файла
# deactivate для выключения виртуальной среды

app = Flask(__name__)

connection = pymysql.connect(host='petrodim.beget.tech',
                                 user='petrodim_test_db',
                                 password='M2&pWHkR',
                                 db='petrodim_test_db',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return "Hello, world!"

@app.route('/api/v1/sendPhoto/user_id/<int:user_id>', methods=['GET'])
def sendPhotoOnUserID(user_id):
    if request.method == 'GET':
        file = request.files['file']
        return "sendPhoto"
    else:
        return make_response("Allow method for get image: GET", 400)

@app.route('/api/v1/savePhotoOnServer', methods=['GET', 'POST'])
def savePhotoOnServer():
    if request.method == 'POST':
        file = request.files['file']
        return "savePhotoOnServer"
    else:
        return make_response("Allow method for save image: POST", 400)

@app.route('/api/v1/findFaceOnPhoto', methods=['GET', 'POST'])
def findFaceOnPhoto():
    if request.method == 'POST':
        file = request.files['file']
        try:
            with connection.cursor() as cursor:
                sql = "SELECT user_id, path FROM path_to_photo_of_user"
                cursor.execute(sql)
                known_faces_user_id = []
                known_faces_images_path = []
                known_face_encodings_images = []
                for row in cursor:
                    known_faces_user_id.append(row["user_id"])
                    known_faces_images_path.append(row["path"])
                    image = face_recognition.load_image_file(row["path"])
                    image_face_encoding = face_recognition.face_encodings(image)[0]
                    known_face_encodings_images.append(image_face_encoding)

        finally:
            connection.close()

        unknown_image = face_recognition.load_image_file("images/yahya-islamov.jpg")

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

        return "Find face in photo of user with user_id: " + str_user_id
    else:
        return make_response("Allow method for save image: POST", 400)

if __name__ == '__main__':
    app.run(debug=True)