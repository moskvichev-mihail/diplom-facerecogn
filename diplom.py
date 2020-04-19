import face_recognition
import numpy as np
import pymysql.cursors
from flask import Flask

connection = pymysql.connect(host='petrodim.beget.tech',
                             user='petrodim_test_db',
                             password='M2&pWHkR',
                             db='petrodim_test_db',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

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

# Образец данных
obama_image = face_recognition.load_image_file("images/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

biden_image = face_recognition.load_image_file("images/biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

yahya_image = face_recognition.load_image_file("images/yahya-islamov.jpg")
yahya_face_encoding = face_recognition.face_encodings(yahya_image)[0]

known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    yahya_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden",
    "Yahya Islamov"
]
# Конец образца данных
# Load an image with an unknown face
unknown_image = face_recognition.load_image_file("images/yahya-islamov.jpg")

# Find all the faces and face encodings in the unknown image
face_locations = face_recognition.face_locations(unknown_image)
face_encodings = face_recognition.face_encodings(unknown_image, face_locations)


# Loop through each face found in the unknown image
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    # See if the face is a match for the known face(s)
    matches = face_recognition.compare_faces(known_face_encodings_images, face_encoding)

    name = "Unknown"

    # Or instead, use the known face with the smallest distance to the new face
    face_distances = face_recognition.face_distance(known_face_encodings_images, face_encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        name = known_faces_user_id[best_match_index]

    print(name)