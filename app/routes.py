import face_recognition
import numpy as np
import os
import base64
from app import app
from app import functions
from app import constants
from flask import request, make_response, render_template


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/docs')
def docs():
    return render_template("docs.html", title="Документация")


@app.route('/api/v1/getPhoto/user/<int:user_id>', methods=['GET', 'POST'])
def send_photo_on_user_id(user_id):
    if request.method == 'GET':
        connection = functions.connect_to_db(constants.connect_db_hostname, constants.connect_db_user, constants.connect_db_password, constants.connect_db_dbname)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(constants.sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) != 0:
                    cursor.execute(constants.sql_get_path, user_id)
                    result = cursor.fetchall()
                    if len(result) != 0:
                        cursor.execute(constants.sql_get_path, user_id)
                        for row in cursor:
                            name_photo = row["path"]
                            path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                        # connection.close()
                        if os.path.exists(path_to_image):
                            # return send_from_directory(app.config['UPLOAD_FOLDER'], name_photo)
                            image = open(path_to_image, "rb")
                            image_read = image.read()
                            image_encode = base64.b64encode(image_read)
                            result = {'status_code': 200, 'image': str(image_encode)}
                            return make_response(result, 200)
                            # post_request = requests.post('http://localhost:5000/api/v1/savePhotoOnServer/user/6', files=image)
                            # return post_request.text
                        else:
                            result = {'status_code': 400, 'description': constants.not_exist_photo_error_description}
                            return make_response(result, 400)
                    else:
                        result = {'status_code': 400, 'description': constants.not_exist_photo_in_db_error_description}
                        return make_response(result, 400)
                else:
                    result = {'status_code': 400, 'description': constants.not_exist_user_in_db_error_description}
                    return make_response(result, 400)
    else:
        result = {'status_code': 400, 'description': constants.allow_get_method_error_description}
        return make_response(result, 400)


@app.route('/api/v1/addPhoto/user/<int:user_id>', methods=['GET', 'POST'])
def save_photo_on_server(user_id):
    if request.method == 'POST':
        connection = functions.connect_to_db(constants.connect_db_hostname, constants.connect_db_user, constants.connect_db_password, constants.connect_db_dbname)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(constants.sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) == 0:
                    result = {'status_code': 400, 'description': constants.not_exist_user_in_db_error_description}
                    return make_response(result, 400)
                else:
                    cursor.execute(constants.sql_check_exist_photo, user_id)
                    result = cursor.fetchall()
                    if len(result) != 0:
                        result = {'status_code': 400, 'description': constants.exist_photo_error_description}
                        return make_response(result, 400)
                    else:
                        if (request.files.get('image')):
                            image = request.files.get('image')
                        else:
                            result = {'status_code': 400, 'description': constants.not_sending_photo_in_route}
                            return make_response(result, 400)
                        path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                        if os.path.exists(path_to_image):
                            result = {'status_code': 400, 'description': constants.exist_photo_error_description}
                            return make_response(result, 400)
                        else:
                            if image and functions.allowed_file(image.filename):
                                cursor.execute(constants.sql_insert_path_photo, (user_id, image.filename))
                                image.save(path_to_image)
                                if os.path.exists(path_to_image):
                                    result = {'status_code': 200, 'description': constants.success_save_photo_description}
                                    return make_response(result, 200)
                                else:
                                    result = {'status_code': 400, 'description': constants.not_save_photo_error_description}
                                    return make_response(result, 400)
                            else:
                                result = {'status_code': 400, 'description': constants.allow_format_img_error_description}
                                return make_response(result, 400)
    else:
        result = {'status_code': 400, 'description': constants.allow_post_method_error_description}
        return make_response(result, 400)


@app.route('/api/v1/updatePhoto/user/<int:user_id>', methods=['GET', 'PUT'])
def update_photo(user_id):
    if request.method == 'PUT':
        connection = functions.connect_to_db(constants.connect_db_hostname, constants.connect_db_user, constants.connect_db_password, constants.connect_db_dbname)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(constants.sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) == 0:
                    result = {'status_code': 400, 'description': constants.not_exist_user_in_db_error_description}
                    return make_response(result, 400)
                else:
                    if (request.files.get('image')):
                        image = request.files.get('image')
                    else:
                        result = {'status_code': 400, 'description': constants.not_sending_photo_in_route}
                        return make_response(result, 400)
                    if image and functions.allowed_file(image.filename):
                        path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                        cursor.execute(constants.sql_get_path, user_id)
                        result = cursor.fetchall()
                        if len(result) != 0:
                            cursor.execute(constants.sql_get_path, user_id)
                            for row in cursor:
                                sql_path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                            if os.path.exists(sql_path_to_image):
                                os.remove(sql_path_to_image)
                                image.save(path_to_image)
                                # update запрос к БД
                            else:
                                result = {'status_code': 400, 'description': constants.not_exist_photo_error_description}
                                return make_response(result, 400)
                        else:
                            result = {'status_code': 400, 'description': constants.not_exist_photo_in_db_error_description}
                            return make_response(result, 400)
                    else:
                        result = {'status_code': 400, 'description': constants.allow_format_img_error_description}
                        return make_response(result, 400)
    else:
        result = {'status_code': 400, 'description': constants.allow_put_method_error_description}
        return make_response(result, 400)


@app.route('/api/v1/deletePhoto/user/<int:user_id>', methods=['GET', 'DELETE'])
def delete_photo_from_server(user_id):
    if request.method == 'DELETE':
        connection = functions.connect_to_db(constants.connect_db_hostname, constants.connect_db_user, constants.connect_db_password, constants.connect_db_dbname)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(constants.sql_get_user, user_id)
                result = cursor.fetchall()
                if len(result) == 0:
                    result = {'status_code': 400, 'description': constants.not_exist_user_in_db_error_description}
                    return make_response(result, 400)
                else:
                    cursor.execute(constants.sql_get_path, user_id)
                    for row in cursor:
                        path_to_image = os.path.join(app.config['UPLOAD_FOLDER'], row["path"])
                    if not os.path.exists(path_to_image):
                        result = {'status_code': 400, 'description': constants.not_exist_photo_error_description}
                        return make_response(result, 400)
                    else:
                        cursor.execute(constants.sql_get_photo_id, user_id)
                        for row in cursor:
                            path_id = row["path_to_photo_of_user_id"]
                        os.remove(path_to_image)
                        cursor.execute(constants.sql_delete_path_photo, path_id)
                        # connection.close()
                        result = {'status_code': 200, 'description': constants.success_delete_photo_description}
                        return make_response(result, 200)
    else:
        result = {'status_code': 400, 'description': constants.allow_delete_method_error_description}
        return make_response(result, 400)


@app.route('/api/v1/findFaceOnPhoto', methods=['GET', 'POST'])
def find_face_on_photo():
    if request.method == 'GET':
        connection = functions.connect_to_db(constants.connect_db_hostname, constants.connect_db_user, constants.connect_db_password, constants.connect_db_dbname)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(constants.sql_get_all_users_photo)
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
        # connection.close()
        if (request.files.get('image')):
            image = request.files.get('image')
        else:
            result = {'status_code': 400, 'description': constants.not_sending_photo_in_route}
            return make_response(result, 400)
        path_to_image = os.path.join(app.config['UPLOAD_FOLDER_FOR_FIND_FACE'], image.filename)
        if image and functions.allowed_file(image.filename):
            image.save(path_to_image)
        if not os.path.exists(path_to_image):
            result = {'status_code': 400, 'description': constants.not_save_photo_error_description}
            return make_response(result, 400)
        unknown_image = face_recognition.load_image_file(path_to_image)
        os.remove(path_to_image)

        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        str_user_id = "Unknown"
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
        result = {'status_code': 400, 'description': constants.allow_get_method_error_description}
        return make_response(result, 400)
