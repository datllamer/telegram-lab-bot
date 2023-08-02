import telebot
from telebot import types
import config_file
import db_manipulation as db
import access_levels
from TemperatureData import TemperatureData

bot_token = config_file.bot_token
bot = telebot.TeleBot(bot_token)
active_users = {}


main_menu_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
main_menu_keyboard.add(
    types.KeyboardButton("Інфо"),
    types.KeyboardButton("Статус"),
)


def user_rights(chat_id):
    if chat_id not in active_users:
        return "not_user"
    else:
        user = active_users[chat_id]
        rights = user["rights"]
        return rights


def helpe(user_rights):
    base_commands = (
        " Доступні вам команди:\n"
        "/login\n"
        "/logout\n"
        "/registration\n"
        "/info\n"
        "/help\n"
        "/myStatus\n"
    )
    user3_commands = "/data\n"
    admin_commands = "/promote\n" "/adminInfo\n" "/users\n"
    how_to_use = (
        "   Для використаня бота - просто перетягніть дата-файл до чату, усе іньше буде виконано "
        "автоматично. Якщо ви маєте лише посилання на гугл-таблицю, просто відправте його боту, ніяких "
        "інших дій не потрібно. Результати аналізу будуть відправлені до дб автоматично, при відповідному"
        " рівні допуску\n"
    )
    please_login = (
        "!!! Для використання основних функцій увійдить до акаунту з відповідним рівнем доступу\n"
        "Щоб отримати необхідний доступ зв'яжітся з вашим науковим керівником, більше інформації про "
        "доступ"
        " - /myStatus\n"
    )
    if user_rights == "admin":
        return base_commands + admin_commands
    elif user_rights == "user3":
        return base_commands + user3_commands + how_to_use
    elif user_rights == "user2":
        return base_commands + how_to_use
    elif user_rights == "user1":
        return base_commands + how_to_use
    else:
        return base_commands + please_login


def access_denied_message(chat_id):
    bot.send_message(
        chat_id, "У вас нема доступу до цієї команди, доступні команди - /help "
    )


def info_message(chat_id):
    info = (
        "   Бот для швидкого аналізу температурних дата-файлів.\n"
        "Розроблено студентом Національного авіаційного університету\n"
        "Факультет екологічної безпеки, інженерії та технологій\n"
        "Кафедри біокібернетики та аерокосмічної медицини\n"
        "Юрковим Ф.Ю группа Бі-309Б\n"
        "За технічним завданням викладача:\n"
        "Полікарпов О.О.\n"
        "\n" + helpe(user_rights(chat_id))
    )
    bot.send_message(chat_id, info, reply_markup=main_menu_keyboard)


def check_nickname(message):
    chat_id = message.chat.id
    text = message.text
    if text == "stop":
        bot.send_message(chat_id, "Спроби входу припинено")
    elif db.authenticate_user(chat_id, text) is True:
        user_rights = db.get_user_rights(text)
        active_users[chat_id] = {"nickname": text, "rights": user_rights}
        bot.send_message(chat_id, f"Ви увійшли як {text}")
    else:
        bot.send_message(
            chat_id,
            "Такий акаунт не існує, якщо ви бажаєте припинити спроби входу введіть 'stop'",
        )
        bot.register_next_step_handler(message, check_nickname)


def reg_user(message):
    text = message.text
    chat_id = message.chat.id

    if text == "stop":
        bot.send_message(chat_id, "Реєстрація припинена")

    elif db.is_nickname_free(text) is True:
        if len(text) <= 32:
            if "/" not in text:
                db.new_user(chat_id, text, "user0")
                active_users[chat_id] = {"nickname": text, "rights": "user0"}
                bot.send_message(chat_id, "Реєстрація успішна")
                info_message(chat_id)

            else:
                bot.send_message(chat_id, "Ім'я не повинно містити /")
                bot.register_next_step_handler(message, reg_user)
        else:
            bot.send_message(
                chat_id,
                "Ім'я повинно бути до 32 символів, бажано латинськими літерами та у форматі \"Прізвище "
                'І.Б."',
            )
            bot.register_next_step_handler(message, reg_user)
    else:
        bot.send_message(
            chat_id,
            "Такий користувач вже існує, якщо ви бажаєте припинити спроби реєстрацї введіть 'stop'",
        )
        bot.register_next_step_handler(message, reg_user)


@bot.message_handler(commands=["start"])
def start_handler(message):
    chat_id = message.chat.id
    info_message(message.chat.id)
    bot.send_message(
        chat_id,
        "Для початку роботи зареєструйтесь через /registration або увійдіть за допомогою /login."
        "Після цього звернится до вашого наукового керівника за відповідними правами доступу.",
    )


@bot.message_handler(commands=["info"])
def start_handler(message):
    info_message(message.chat.id)


@bot.message_handler(commands=["help"])
def helpe_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, helpe(user_rights(chat_id)))


@bot.message_handler(commands=["login"])
def login_handler(message):
    chat_id = message.chat.id
    if chat_id in active_users:
        bot.send_message(
            chat_id, "Спочатку вийдіть з аккаунту, для цього введіть /logout"
        )
    elif db.check_chat_id(chat_id) is False:
        bot.send_message(
            chat_id,
            "На ваш телеграм не зареєстровано жодного акаунту, щоб зареєструватися введіть /registration",
        )
    else:
        bot.send_message(chat_id, "Введіть ім'я акаунту під яким бажаєте зайти")
        bot.register_next_step_handler(message, check_nickname)


@bot.message_handler(commands=["logout"])
def logout_handler(message):
    chat_id = message.chat.id
    if chat_id in active_users:
        del active_users[chat_id]
        bot.send_message(chat_id, "Ви вийшли з системи")
    else:
        bot.send_message(chat_id, "Ви не можете вийти поки не увійшли")


@bot.message_handler(commands=["registration"])
def registration_handler(message):
    chat_id = message.chat.id
    if chat_id in active_users:
        bot.send_message(
            chat_id, "Спочатку вийдіть з аккаунту, для цього введіть /logout"
        )
    else:
        bot.send_message(
            chat_id,
            "Введіть ім'я акаунту під яким бажаєте зайти. Ім'я повинно бути до 32 символів,"
            'бажано латинськими літерами та у форматі "Прізвище І.Б."',
        )
        bot.register_next_step_handler(message, reg_user)


@bot.message_handler(commands=["myStatus"])
def my_status_handler(message):
    chat_id = message.chat.id

    if chat_id in active_users:
        rights = user_rights(chat_id)
        user = active_users[chat_id]
        nickname = user["nickname"]
        if rights == "admin":
            status_message = "У вас є доступ лише до функцій адміністрування. Основний функціонал заблокованно"
        elif rights == "user3":
            status_message = "У вас є доступ до всіх функцій крім адміністрування"
        elif rights == "user2":
            status_message = (
                "У вас є доступ до основних функцій, відправка до сервера увімкненна"
            )
        elif rights == "user1":
            status_message = (
                "У вас є доступ до основних функцій, відправка до сервера вимкненна"
            )
        elif rights == "user0":
            status_message = "У вас немає доступу до основних функцій, зв'яжіться з вашим науковим керівником"
        else:
            status_message = (
                "!!! Ваш акаунт не може існувати негайно повідомте адміністратора !!!"
            )

        return_message = (
            f"Ваш телеграм ID {chat_id}\n"
            f"Ви увійшли як {nickname}\n"
            f"{status_message}"
        )
    else:
        return_message = "Щоб мати статус увійдіть - /login "

    bot.send_message(chat_id, return_message)


# _________________________ADMINS_________________________ #


def restore_admin0(admin_id=config_file.admin_id):
    if db.is_nickname_free("admin0"):
        db.new_user(admin_id, "admin0", "admin")
    else:
        db.update_user_data_by_id(1, admin_id, "admin0")


@bot.message_handler(commands=["users"])
def users_handler(message):
    chat_id = message.chat.id
    rights = user_rights(chat_id)
    text = message.text
    arguments = message.text.split(" ")

    if access_levels.admin.is_access_granted(rights) is False:
        access_denied_message(chat_id)

    elif len(arguments) == 1:
        bot.send_message(
            chat_id,
            "При використанні /users використовуйте аргументи\n"
            "allusers    - усі користувачі з бд\n"
            "active - лише активні\n",
        )

    elif arguments[1] == "allusers":
        max_id = db.get_max_id()
        current_id = 1
        allusers = ""
        while current_id <= max_id:
            users = db.get_users_all(start_id=current_id)
            allusers += users
            current_id += 50
            bot.send_message(chat_id, allusers)

    elif arguments[1] == "active":
        active = "id                    rights    name \n"
        if len(active_users) == 50:
            for user in active_users:
                id_user = user
                user = active_users[user]
                rights = user["rights"]
                nickname = user["nickname"]
                active += f"{id_user}|{rights}|{nickname}\n"
            bot.send_message(chat_id, active)

            # Забагато користувачів

        else:
            active_users__ = []
            users_list = list(active_users)

            while len(users_list) != 0:
                active = "id                      rights      name \n"
                while len(active_users__) < 50 and len(users_list) != 0:
                    popd = users_list.pop()
                    active_users__.append(popd)
                    id_user = popd
                    user = active_users[popd]
                    rights = user["rights"]
                    nickname = user["nickname"]
                    active += f"{id_user} | {rights} | {nickname}\n"
                bot.send_message(chat_id, active)


@bot.message_handler(commands=["promote"])
def promote_handler(message):
    chat_id = message.chat.id
    rights = user_rights(chat_id)
    arguments = message.text.split(" ")

    if access_levels.admin.is_access_granted(rights) is False:
        access_denied_message(chat_id)

    elif len(arguments) != 3:
        bot.send_message(
            chat_id,
            "При використанні /promote використовуйте аргументи як \n"
            "/promote USER RIGHTS \n"
            'де RIGHTS - ("user0", "user1", "user2", "user3", "admin")\n'
            "USER можливо дізнатись через /users",
        )

    elif db.is_nickname_free(arguments[1]):
        bot.send_message(chat_id, "Користувач не існує")

    elif arguments[2] not in ("user0", "user1", "user2", "user3", "admin"):
        bot.send_message(chat_id, "Рівень прав не існує")

    else:
        db.set_user_rights(arguments[2], arguments[1])
        bot.send_message(
            chat_id, "Рівень прав встановлено, права оновляться з входом користувача"
        )


@bot.message_handler(commands=["adminInfo"])
def admininfo_handler(message):
    chat_id = message.chat.id
    rights = user_rights(chat_id)

    if access_levels.admin.is_access_granted(rights) is False:
        access_denied_message(chat_id)

    else:
        bot.send_message(
            chat_id,
            "Для рівня прав адмін доступні спеціальні команди, що потребують аргуметів при визові"
            ". Якщо аргументи відсутні, команда виведе підказку до себе. Спеціальний "
            "адміністратор (admin0) автоматично відновлюється при перезавантаженні бота ,"
            "його chat_id встановлюється за конфігом."
            "\n Команди: \n"
            "/promote USER RIGHTS - встановлює права RIGHTS для користувача USER\n"
            "/users (all або active) - виводить інформацію стосовно користувачів,"
            " усіх або активних відповідно\n",
        )


# _________________________SUPERUSERS_________________________ #


@bot.message_handler(commands=["data"])
def data_handler(message):
    chat_id = message.chat.id
    rights = user_rights(chat_id)

    if chat_id not in active_users:
        bot.send_message(chat_id, "Спочатку увійдіть /login")

    if access_levels.user3.is_access_granted(rights) is False:
        access_denied_message(chat_id)

    else:
        try:
            stat_data = db.get_stat_data()
            single_message = "\n"
            for i in stat_data:
                if len(single_message) < 4000:
                    b = len(single_message)
                    sample_id = i[0]
                    name_of_file = i[1]
                    if "https://docs.google.com/spreadsheets/d/" in name_of_file:
                        name_of_file = name_of_file.split("/")[5]
                    maximum = TemperatureData.convert_num_for_tab(i[2])
                    minimum = TemperatureData.convert_num_for_tab(i[3])
                    median = TemperatureData.convert_num_for_tab(i[4])
                    average = TemperatureData.convert_num_for_tab(i[5])
                    delta = TemperatureData.convert_num_for_tab(i[6])
                    single_unit = (
                        f"ID: {sample_id}\n"
                        f"NAME: {name_of_file}\n"
                        f"max___ min___ med___ avr___ dlt___\n"
                        f"{maximum}|{minimum}|{median}|{average}|{delta}\n"
                    )
                    single_message = single_message + single_unit
                if len(single_message) > 3500:
                    bot.send_message(chat_id, single_message)
                    single_message = "\n"
        except:
            bot.send_message(chat_id, "Помилка під час читання БД")


# _________________________MAIN-FEATURE_________________________ #


@bot.message_handler(content_types=["document"])
def handle_documents(message):
    chat_id = message.chat.id

    if chat_id not in active_users:
        bot.send_message(chat_id, "Спочатку увійдіть /login")

    if access_levels.user1.is_access_granted(user_rights(chat_id)) is False:
        access_denied_message(chat_id)

    else:
        file = bot.get_file(message.document.file_id)
        file_name = file.file_path
        if ".xlsx" in file_name:
            try:
                downloaded_file = bot.download_file(file_name)
                data = TemperatureData()
                data.set_data_from_xlsx(downloaded_file)

                if access_levels.user2.is_access_granted(user_rights(chat_id)):
                    data.send_to_db(chat_id, file_name)

                tab_message = data.get_info_tab()
                bot.send_message(chat_id, tab_message)

            except:
                bot.send_message(
                    chat_id,
                    "Некоректний тип файлу, відправте фал звіту. Ви можете определити їх по наявності "
                    "INSTR_ в назві",
                )


@bot.message_handler(
    func=lambda message: message.entities is not None
    and any(entity.type == "url" for entity in message.entities),
    content_types=["text"],
)
def handle_links(message):
    chat_id = message.chat.id

    if chat_id not in active_users:
        bot.send_message(chat_id, "Спочатку увійдіть /login")

    if access_levels.user1.is_access_granted(user_rights(chat_id)) is False:
        access_denied_message(chat_id)

    else:
        links = [entity for entity in message.entities if entity.type == "url"]
        for link in links:
            try:
                url = message.text[link.offset : link.offset + link.length]
                data = TemperatureData()
                data.set_data_from_google_doc_link(url)

                if access_levels.user2.is_access_granted(user_rights(chat_id)):
                    data.send_to_db(chat_id, url)

                tab_message = data.get_info_tab()
                bot.send_message(chat_id, tab_message)

            except:
                bot.send_message(
                    chat_id,
                    "Невідповідний формат файлу. Використовуйте лише завантажені до гугл таблиці файли."
                    " Перевірте формат посилання, файл може бути збережений у форматі ексель. Перевірте "
                    "чи є файл одним з автоматично створених",
                )


# _________________________BUTTONS_________________________ #


@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_buttons(message):
    chat_id = message.chat.id
    if chat_id in active_users:
        if message.text == "Інфо":
            info_message(chat_id)
        elif message.text == "Статус":
            my_status_handler(message)
        else:
            bot.send_message(
                message.chat.id,
                "Неправильний ввід. для підказки натисніть - /info, "
                "доступні команди - /help.",
            )
    else:
        bot.send_message(
            message.chat.id, "Будь ласка, авторизуйтесь, для цого введіть /login"
        )
