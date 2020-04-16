import face_recognition
import numpy as np


obama_image = face_recognition.load_image_file("images/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

biden_image = face_recognition.load_image_file("images/biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

yahya_image = face_recognition.load_image_file("images/yahya-original.jpg")
yahya_face_encoding = face_recognition.face_encodings(yahya_image)[0]

# Create arrays of known face encodings and their names
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
# Load an image with an unknown face
unknown_image = face_recognition.load_image_file("images/yahya-find.jpg")

# Find all the faces and face encodings in the unknown image
face_locations = face_recognition.face_locations(unknown_image)
face_encodings = face_recognition.face_encodings(unknown_image, face_locations)


# Loop through each face found in the unknown image
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    # See if the face is a match for the known face(s)
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

    name = "Unknown"

    # Or instead, use the known face with the smallest distance to the new face
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        name = known_face_names[best_match_index]

    print(name)