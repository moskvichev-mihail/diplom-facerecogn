UPLOAD_FOLDER = "app/static/images"
UPLOAD_FOLDER_FOR_FIND_FACE = "app/static/saved_images"
ALLOWED_EXTENSIONS = (['png', 'jpg', 'jpeg'])

sql_get_all_users_photo = "SELECT user_id, path FROM path_to_photo_of_user"
sql_get_user = "SELECT user_id FROM user WHERE user_id=%s"
sql_get_path = "SELECT path FROM path_to_photo_of_user  WHERE user_id=%s"
sql_check_exist_photo = "SELECT * FROM path_to_photo_of_user  WHERE user_id=%s"
sql_get_photo_id = "SELECT path_to_photo_of_user_id FROM path_to_photo_of_user  WHERE user_id=%s"
sql_insert_path_photo = "INSERT INTO path_to_photo_of_user (path_to_photo_of_user_id, user_id, path) VALUES (NULL, %s, %s)"
sql_delete_path_photo = "DELETE FROM `path_to_photo_of_user` WHERE `path_to_photo_of_user`.`path_to_photo_of_user_id` = %s"
sql_update_path_photo = ""

connect_db_hostname = "petrodim.beget.tech"
connect_db_user = "petrodim_test_db"
connect_db_password = "M2&pWHkR"
connect_db_dbname = "petrodim_test_db"

not_exist_photo_error_description = "Фото пользователя отсутствует на сервере"
not_exist_photo_in_db_error_description = "Для user_id нет записи с фотографией в БД"
not_exist_user_in_db_error_description = "Введённый user_id отсутствует в БД"
exist_photo_error_description = "Ошибка, фотография уже существует на сервере"
not_save_photo_error_description = "Ошибка, фотография не сохранена"
success_delete_photo_description = "Фотография успешно удалена"
success_save_photo_description = "Фотография успешно сохранена"
not_sending_photo_in_route = "В запросе отсутствует фотография"
allow_format_img_error_description = "Ошибка, разрешенный формат для фотографий: jpg, png, jpeg"
allow_get_method_error_description = "Разрешённый метод для данного запроса: GET"
allow_post_method_error_description = "Разрешённый метод для данного запроса: POST"
allow_put_method_error_description = "Разрешённый метод для данного запроса: PUT"
allow_delete_method_error_description = "Разрешённый метод для данного запроса: DELETE"
