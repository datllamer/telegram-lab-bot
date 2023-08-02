import mysql.connector
import config_file

error_message = ""


def get_max_id():
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        query = "SELECT MAX(id) FROM users"
        cursor.execute(query)
        max_id = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return max_id

    except mysql.connector.Error as error:
        error_message = f"Помилка при читанні бази даних:\n{error}"
        print(error_message)
        return None


def get_users_all(limit=50, start_id=1):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        query = (
            f"SELECT GROUP_CONCAT(CONCAT(id, ', ', chat_id, ', ', nickname, ', ', user_rights) SEPARATOR '\n') "
            f"FROM users WHERE id >= {start_id} LIMIT {limit}"
        )
        cursor.execute(query)
        concatenated_string = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return concatenated_string

    except mysql.connector.Error as error:
        error_message = f"Помилка при читанні бази даних:\n{error}"
        print(error_message)
        return None


def create_project_db():
    try:
        connection = mysql.connector.connect(
            host=config_file.host, user=config_file.user, password=config_file.password
        )
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS project_db")
        print("База даних project_db успішно створена або вже існує.")

        cursor.close()
        connection.close()

        create_users_table()
        create_stat_data_table()

    except mysql.connector.Error as error:
        error_message = f"\nПомилка при створенні бази даних:\n{error}"
        print(error_message)


def create_users_table():
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chat_id INT,
                nickname VARCHAR(32),
                user_rights VARCHAR(5)
            )
        """
        cursor.execute(create_table_query)
        print("Таблиця users успішно створена або вже існує.")

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"\nПомилка при створенні таблиці users:\n{error}"
        print(error_message)


def create_stat_data_table():
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS stat_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chat_id INT,
                file_name VARCHAR(256),
                max FLOAT,
                min FLOAT,
                median FLOAT,
                average FLOAT,
                delta FLOAT
            )
        """
        cursor.execute(create_table_query)
        print("Таблиця stat_data успішно створена або вже існує.")

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"\nПомилка при створенні таблиці stat_data:\n{error}"
        print(error_message)


def send_stat_data_to_server(data_dict, chat_id=None, file_name=None):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )

        cursor = connection.cursor()

        insert_query = """
            INSERT INTO stat_data (chat_id, file_name, max, min, median, average, delta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data_values = (
            chat_id,
            file_name,
            data_dict["max"],
            data_dict["min"],
            data_dict["median"],
            data_dict["average"],
            data_dict["delta"],
        )
        cursor.execute(insert_query, data_values)
        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"\nПомилка при відправці до бази даних:\n{error}"
        print(error_message)


def new_user(chat_id, nickname, user_rights):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users (chat_id, nickname, user_rights) VALUES (%s, %s, %s)",
            (chat_id, nickname, user_rights),
        )
        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"\nПомилка під час збереження пароля:\n{error}"
        print(error_message)


def set_user_rights(user_rights, nickname):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE users SET user_rights = %s WHERE nickname = %s",
            (user_rights, nickname),
        )
        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"\nПомилка під час збереження прав:\n{error}"
        print(error_message)


def authenticate_user(chat_id, nickname):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE chat_id = %s AND nickname = %s",
            (chat_id, nickname),
        )
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user is not None:
            return True
        else:
            return False

    except mysql.connector.Error as error:
        error_message = f"\nПомилка під час збереження пароля:\n{error}"
        print(error_message)
        return False


def get_user_rights(nickname):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT user_rights FROM users WHERE nickname = %s", (nickname,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        a = 3
        if user:
            return user[0]
        else:
            return None

    except mysql.connector.Error as error:
        error_message = f"Помилка при читанні бази даних:\n{error}"
        print(error_message)
        return None


def check_chat_id(chat_id):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM users WHERE chat_id = %s", (chat_id,))
        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"Помилка при читанні бази даних:\n{error}"
        print(error_message)
        return False

    if count > 0:
        return True
    else:
        return False


def is_nickname_free(nickname):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM users WHERE nickname = %s", (nickname,))
        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"Помилка при читанні бази даних:\n{error}"
        print(error_message)
        return False

    if count > 0:
        return False
    else:
        return True


def update_user_data_by_id(id, chat_id, nickname):
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        update_query = "UPDATE users SET chat_id = %s, nickname = %s WHERE id = %s"
        cursor.execute(update_query, (chat_id, nickname, id))
        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        error_message = f"Помилка при оновленні даних користувача:\n{error}"
        print(error_message)


def get_stat_data():
    try:
        connection = mysql.connector.connect(
            host=config_file.host,
            user=config_file.user,
            password=config_file.password,
            database=config_file.database,
        )
        cursor = connection.cursor()

        # Запит, що вибирає всі елементи таблиці stat_data
        query = f"SELECT id, file_name, max, min, median, average, delta FROM stat_data"
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        rows_list = []
        for row in result:
            rows_list.append(list(row))

        return rows_list

    except mysql.connector.Error as error:
        error_message = f"\nПомилка при читанні бази даних:\n{error}"
        print(error_message)
        return []


create_project_db()
