from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.types import InputMediaPhoto
from aiogram.types import ParseMode


import importlib
import os
import random
import sqlite3

import bot_data
from dbase import *


@bot_data.dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    try:
        # Проверяем наличие записи в базе данных с id пользователя
        bot_data.cursor.execute("SELECT * FROM users WHERE id=?", (message.chat.id,))
        user_exists = bot_data.cursor.fetchone() is not None



        if not user_exists:
            # cursor.execute('SELECT COUNT(*) FROM users')
            # number = cursor.fetchone()[0] + 1
            # cursor.execute("INSERT INTO users (id, username, ban, number) VALUES (?, ?, ?, ?)",
            #                (message.chat.id, message.from_user.username, "FALSE", number))
            # conn.commit()

            notuserexist(bot_data.cursor, bot_data.conn, message)

            global user_id
            user_id = message.chat.id
            # Создаем клавиатуру с кнопками
            keyboard_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_ru = types.KeyboardButton('🇷🇺')
            button_en = types.KeyboardButton('🇬🇧')
            button_ua = types.KeyboardButton('🇺🇦')
            button_de = types.KeyboardButton('🇩🇪')
            button_es = types.KeyboardButton('🇪🇸')
            button_fr = types.KeyboardButton('🇫🇷')
            button_it = types.KeyboardButton('🇮🇹')
            button_pl = types.KeyboardButton('🇵🇱')
            button_pt = types.KeyboardButton('🇵🇹')
            button_tr = types.KeyboardButton('🇹🇷')
            #button_tr = types.KeyboardButton('🇹🇷')
            #ДОПОЛНИТЬ выбрать язык и добавить файл
            button_next = types.KeyboardButton('▶️')
            #button_back = types.KeyboardButton('◀️')
            keyboard_start.add(button_ua, button_en, button_ru, button_de, button_es, button_fr, button_it, button_pl, button_pt, button_tr, button_next)
            # Отправляем сообщение пользователю с клавиатурой
            await message.reply('Hello! Select language:', reply_markup=keyboard_start)
            await bot_data.RegisterUser.waiting_for_national.set()

        else:
            keyboard_anket_perexod = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_anket_perexod = types.KeyboardButton('Анкета')
            keyboard_anket_perexod.add(button_anket_perexod)

            bot_data.cursor.execute("SELECT national FROM users WHERE id=?", (message.chat.id,))
            result = bot_data.cursor.fetchone()
            n = result[0]

            texts = importlib.import_module(f"languages.texts_{n}")

            await bot_data.bot.send_message(message.chat.id, texts.already_0,
                                   reply_markup=keyboard_anket_perexod)
            await bot_data.RegisterUser.waiting_for_profile_start.set()
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_profile_start)
async def process_show_anket_start(message: types.Message, state: FSMContext):
    try:
        if message.text.lower() == texts.profile:  # Добавлено условие проверки текста
            await show_anketa(message, state)
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_national)
async def process_national(message: types.Message, state: FSMContext):
    try:
        global texts
        national1 = None
        if message.text == '🇷🇺':
            national1 = 'ru'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇬🇧':
            national1 = 'en'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇺🇦':
            national1 = 'ua'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇩🇪':
            national1 = 'de'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇪🇸':
            national1 = 'es'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇫🇷':
            national1 = 'fr'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇮🇹':
            national1 = 'it'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇵🇱':
            national1 = 'pl'
            texts = importlib.import_module(f"languages.texts_{national1}")
        elif message.text == '🇵🇹':
            national1 = 'pt'
            texts = importlib.import_module(f"languages.texts_{national1}")
        # elif message.text == '🇺🇦':
        #     national1 = 'ua'
        #     texts = importlib.import_module("languages.texts_ua")
        elif message.text == '🇹🇷':
            national1 = 'tr'
            texts = importlib.import_module(f"languages.texts_{national1}")
        # elif message.text == '▶️':
        #     national1 = 'ua'
        #     texts = importlib.import_module("languages.texts_ua")

        bot_data.cursor.execute("UPDATE users SET national = ? WHERE id = ?", (national1, message.from_user.id))
        bot_data.conn.commit()
        keyboard_ok = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_ok = types.KeyboardButton(texts.read)
        keyboard_ok.add(button_ok)
        await message.reply(texts.welcome_1, reply_markup=keyboard_ok)
        await state.finish()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(lambda message: message.text == texts.read)
async def age_handler(message: types.Message):
    try:
        await bot_data.RegisterUser.waiting_for_age.set()
        await message.reply(texts.age, reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        bot_data.warning_log.warning(e)

@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        # Получаем возраст
        age = str(message.text)
        # Проверяем, что возраст больше или равен 16
        if age.isdigit() and int(age) >= 16 and int(age) <= 50:
            bot_data.cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, message.from_user.id))
            bot_data.conn.commit()
            await message.answer(texts.age_next, parse_mode=ParseMode.HTML)
            await state.finish()
            await bot_data.RegisterUser.waiting_for_name.set()
        elif age.isdigit() and int(age) < 16:
            ban(bot_data.cursor, message, bot_data.conn)
            await message.answer(texts.age_return)
            await bot_data.RegisterUser.waiting_for_banned_curva.set()
        else:
            await message.answer(texts.age_wrong)
            await bot_data.RegisterUser.waiting_for_age.set()
    except Exception as e:
        bot_data.warning_log.warning(e)

@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        # Получаем имя
        name = str(message.text)
        if len(name) <= 20:
            # Заносим имя в базу данных
            bot_data.cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, message.from_user.id))
            bot_data.conn.commit()
            # Возвращаемся в начальное состояние
            await state.finish()
            await bot_data.RegisterUser.waiting_for_my_sex.set()

            keyboard_my_sex = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_sex_m = types.KeyboardButton(texts.man)
            button_sex_w = types.KeyboardButton(texts.woman)
            keyboard_my_sex.add(button_sex_w, button_sex_m)
            await message.reply(texts.my_sex, reply_markup=keyboard_my_sex)
        else:
            await bot_data.bot.send_message(message.chat.id, texts.description_name)
            await state.finish()
            await bot_data.RegisterUser.waiting_for_name.set()
    except Exception as e:
        bot_data.warning_log.warning(e)

@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_my_sex)
async def process_my_sex_find(message: types.Message, state: FSMContext):
    try:
        # Получаем пол
        global my_sex
        if message.text == texts.man:
            my_sex = "m"
        elif message.text == texts.woman:
            my_sex = "w"
        bot_data.cursor.execute("UPDATE users SET my_sex = ? WHERE id = ?", (my_sex, message.from_user.id))
        bot_data.conn.commit()
        # Возвращаемся в начальное состояние
        await state.finish()
        await bot_data.RegisterUser.waiting_for_sex_find.set()

        keyboard_sex_find = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_sex_w = types.KeyboardButton(texts.women)
        button_sex_m = types.KeyboardButton(texts.men)
        button_sex_wm = types.KeyboardButton(texts.all)
        keyboard_sex_find.add(button_sex_w, button_sex_m, button_sex_wm)
        await message.reply(texts.sex_find, reply_markup=keyboard_sex_find)
    except Exception as e:
        bot_data.warning_log.warning(e)

@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_sex_find)
async def process_sex_find(message: types.Message, state: FSMContext):
    try:
        global sex_find
        if message.text == texts.men:
            sex_find = 'm'
        elif message.text == texts.women:
            sex_find = 'w'
        elif message.text == texts.all:
            sex_find = 'm+w'
        bot_data.cursor.execute("UPDATE users SET sex_find = ? WHERE id = ?", (sex_find, message.from_user.id))
        bot_data.conn.commit()
        # Отправляем сообщение пользователю
        await message.reply(texts.description, reply_markup=types.ReplyKeyboardRemove())
        # Возвращаемся в начальное состояние
        await state.finish()
        await bot_data.RegisterUser.waiting_for_description.set()
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    try:
        # Получаем имя
        desc = str(message.text)
        if len(desc) <= 200:
            # Заносим описание в базу данных
            bot_data.cursor.execute("UPDATE users SET description = ? WHERE id = ?", (desc, message.from_user.id))
            bot_data.conn.commit()
            # Отправляем подтверждение пользователю
            keyboard_geo = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_geo = types.KeyboardButton(text=texts.geo_share, request_location=True)
            keyboard_geo.add(button_geo)
            await bot_data.bot.send_message(message.chat.id, texts.city, reply_markup=keyboard_geo)
            # Возвращаемся в начальное состояние
            await state.finish()
            await bot_data.RegisterUser.waiting_for_geo.set()
        else:
            await bot_data.bot.send_message(message.chat.id, texts.description_return)
            await state.finish()
            await bot_data.RegisterUser.waiting_for_description.set()
    except Exception as e:
        bot_data.warning_log.warning(e)

@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_geo)
async def process_geo(message: types.Message, state: FSMContext):
    try:
        if message.text:
            city = message.text.lower()
            if city in bot_data.cities_ru:
                await state.update_data(city=city)
                bot_data.cursor.execute("UPDATE users SET geo = ? WHERE id = ?", (city, message.from_user.id))
                bot_data.conn.commit()
                await message.answer(texts.photo)
                await bot_data.RegisterUser.waiting_for_photo_1.set()
            else:
                await bot_data.bot.send_message(message.chat.id, texts.city_return)
                await bot_data.RegisterUser.waiting_for_geo.set()
        else:
            await bot_data.bot.send_message(message.chat.id, texts.city_return_2)
            keyboard_geo = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_geo = types.KeyboardButton(text=texts.geo_share, request_location=True)
            keyboard_geo.add(button_geo)
            await bot_data.bot.send_message(message.chat.id, texts.city, reply_markup=keyboard_geo)
            await bot_data.RegisterUser.waiting_for_geo.set()
    except Exception as e:
        bot_data.warning_log.warning(e)

@bot_data.dp.message_handler(content_types=types.ContentType.LOCATION, state=bot_data.RegisterUser.waiting_for_geo)
async def process_location(message: types.Message, state: FSMContext):
    try:
        location = message.location
        latitude = location.latitude
        longitude = location.longitude

        # geolocator = Nominatim(user_agent="geoapiExercises")
        # location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
        # address = location.raw['address']
        # geo = address.get('city', '') or address.get('town', '') or address.get('village', '') or address.get('state', '')

        await state.update_data(latitude=latitude, longitude=longitude)
        await bot_data.bot.send_message(message.chat.id, texts.location_true, reply_markup=types.ReplyKeyboardRemove())
        bot_data.cursor.execute("UPDATE users SET latitude = ?, longitude = ? WHERE id = ?",
                       (latitude, longitude, message.from_user.id))
        bot_data.conn.commit()
        await state.finish()
        await message.answer(texts.photo)
        await bot_data.RegisterUser.waiting_for_photo_1.set()
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.PHOTO, state=bot_data.RegisterUser.waiting_for_photo_1)
async def process_image(message: types.Message, state: FSMContext):
    try:
        file_id = message.photo[-1].file_id
        file = await bot_data.bot.get_file(file_id)
        file_extension = os.path.splitext(file.file_path)[-1]


        user_id = message.from_user.id
        user_photo_dir = f"photos/{user_id}"
        os.makedirs(user_photo_dir, exist_ok=True)

        filename = f"{user_id}{file_extension}"
        full_file_path = os.path.join(user_photo_dir, filename)

        downloaded_file = await bot_data.bot.download_file(file.file_path)

        with open(full_file_path, "wb") as new_file:
            new_file.write(downloaded_file.read())


        #await bot_data.bot.send_message(message.chat.id, "текст чтобы клавиатура убралась, забей", reply_markup=types.ReplyKeyboardRemove())
        await bot_data.bot.send_message(message.chat.id, texts.q_start, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_1.set()
        #await show_anketa(message, state)
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_photo_1, content_types=types.ContentTypes.ANY)
async def wrong_file_received(message: types.Message):
    try:
        await message.answer(texts.photo_not)
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_1)
async def question_1(message: types.Message, state: FSMContext):
    try:
        keyboard_q_1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_1.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_1 + "\n\n" + "1 - " + texts.q_1_answer_0 + "\n" + "2 - " + texts.q_1_answer_1, reply_markup=keyboard_q_1)
        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_2.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_2)
async def question_2(message: types.Message, state: FSMContext):
    try:
        keyboard_q_2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_2.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_2 + "\n\n" + "1 - " + texts.q_2_answer_0 + "\n" + "2 - " + texts.q_2_answer_1, reply_markup=keyboard_q_2)

        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_3.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_3)
async def question_3(message: types.Message, state: FSMContext):
    try:
        keyboard_q_3 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_3.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_3 + "\n\n" + "1 - " + texts.q_3_answer_0 + "\n" + "2 - " + texts.q_3_answer_1, reply_markup=keyboard_q_3)

        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_4.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_4)
async def question_4(message: types.Message, state: FSMContext):
    try:
        keyboard_q_4 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_4.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_4 + "\n\n" + "1 - " + texts.q_4_answer_0 + "\n" + "2 - " + texts.q_4_answer_1, reply_markup=keyboard_q_4)

        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_5.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_5)
async def question_5(message: types.Message, state: FSMContext):
    try:
        keyboard_q_5 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_5.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_5 + "\n\n" + "1 - " + texts.q_5_answer_0 + "\n" + "2 - " + texts.q_5_answer_1, reply_markup=keyboard_q_5)

        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_6.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_6)
async def question_6(message: types.Message, state: FSMContext):
    try:
        keyboard_q_6 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_6.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_6 + "\n\n" + "1 - " + texts.q_6_answer_0 + "\n" + "2 - " + texts.q_6_answer_1, reply_markup=keyboard_q_6)

        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_7.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_7)
async def question_7(message: types.Message, state: FSMContext):
    try:
        keyboard_q_7 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_7.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_7 + "\n\n" + "1 - " + texts.q_7_answer_0 + "\n" + "2 - " + texts.q_7_answer_1, reply_markup=keyboard_q_7)

        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_8.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_8)
async def question_8(message: types.Message, state: FSMContext):
    try:
        keyboard_q_8 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_8.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_8 + "\n\n" + "1 - " + texts.q_8_answer_0 + "\n" + "2 - " + texts.q_8_answer_1,reply_markup=keyboard_q_8)
        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_9.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_9)
async def question_9(message: types.Message, state: FSMContext):
    try:
        keyboard_q_9 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_9.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_9 + "\n\n" + "1 - " + texts.q_9_answer_0 + "\n" + "2 - " + texts.q_9_answer_1, reply_markup=keyboard_q_9)
        await state.finish()
        await bot_data.RegisterUser.waiting_for_q_10.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(content_types=types.ContentTypes.TEXT, state=bot_data.RegisterUser.waiting_for_q_10)
async def question_10(message: types.Message, state: FSMContext):
    try:
        keyboard_q_10 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_0 = types.KeyboardButton("1")
        button_1 = types.KeyboardButton("2")
        keyboard_q_10.add(button_0, button_1)
        await bot_data.bot.send_message(message.chat.id, texts.q_10 + "\n\n" + "1 - " + texts.q_10_answer_0 + "\n" + "2 - " + texts.q_10_answer_1, reply_markup=keyboard_q_10)
        await state.finish()
        await bot_data.RegisterUser.waiting_for_profile.set()

    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_profile)
async def show_anketa(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        photos_dir = os.path.join(os.getcwd(), 'photos', str(user_id))
        if not os.path.isdir(photos_dir):
            await message.reply(texts.photo_located_not)
            return

        photo_files = os.listdir(photos_dir)

        bot_data.cursor.execute("SELECT name, age, geo, description FROM users WHERE id=?", (message.chat.id,))
        result = bot_data.cursor.fetchall()

        for row in result:
            name = row[0]
            age = row[1]
            geo = row[2]
            description = row[3]

            media_group = [InputMediaPhoto(media=open(os.path.join(photos_dir, file), 'rb'),
                                           caption=(f'{name}, {age}, {geo}\n{description}')) for file in photo_files]

            await bot_data.bot.send_media_group(message.chat.id, media=media_group)

        await state.finish()
        keyboard_ex_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_menu = types.KeyboardButton(texts.menu)
        button_smotr = types.KeyboardButton(texts.profile)
        keyboard_ex_profile.add(button_menu, button_smotr)
        await bot_data.bot.send_message(message.chat.id, texts.profile_exotic, reply_markup=keyboard_ex_profile)
        await bot_data.RegisterUser.waiting_for_inresult.set()
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_inresult, content_types=types.ContentTypes.TEXT)
async def inresult(message: types.Message, state: FSMContext):
    try:
        if message.text == texts.profile:
            await state.finish()
            await search_profiles(message, state)
        elif message.text == texts.menu:
            await state.finish()
            await main_menu(message, state)
    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_prosmotr_anket, content_types=types.ContentTypes.ANY)
async def main_menu(message: types.Message, state: FSMContext):
    try:
        await bot_data.bot.send_message(message.chat.id, texts.in_menu)
        inline_keyboard = types.InlineKeyboardMarkup()
        inline_keyboard.row(
            types.InlineKeyboardButton(text=texts.name, callback_data='name'),
            types.InlineKeyboardButton(text=texts.age_0, callback_data='age'),
            types.InlineKeyboardButton(text=texts.geo, callback_data='geo'),
            types.InlineKeyboardButton(text=texts.events, callback_data='events'),
        )
        await bot_data.bot.send_message(message.chat.id, texts.in_menu_1, reply_markup=inline_keyboard)
        if message.text == "Анкеты":
            await search_profiles(message, state)
        await main_menu_handler(bot_data.callback_data, message.from_user.id, state)

    except Exception as e:
        bot_data.warning_log.warning(e)




async def main_menu_handler(message: types.Message, state: FSMContext):
    try:
        if bot_data.callback_data == 'button1':
            return


    except Exception as e:
        bot_data.warning_log.warning(e)


@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_prosmotr_anket, content_types=types.ContentTypes.ANY)
async def search_profiles(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        print(f"user_id: {user_id}")

        bot_data.cursor.execute("SELECT age FROM users WHERE id = ?", (user_id,))
        age_user = bot_data.cursor.fetchone()[0]
        print(f"age_user: {age_user}")

        bot_data.cursor.execute("SELECT my_sex FROM users WHERE id = ?", (user_id,))
        my_sex_user = bot_data.cursor.fetchone()[0]
        print(f"my_sex_user: {my_sex_user}")

        bot_data.cursor.execute("SELECT sex_find FROM users WHERE id = ?", (user_id,))
        sex_find_user = bot_data.cursor.fetchone()[0]
        print(f"sex_find_user: {sex_find_user}")

        bot_data.cursor.execute("SELECT * FROM users WHERE my_sex = ? AND sex_find = ? AND ? - 2 < age AND age < ? + 2",
                       (sex_find_user, my_sex_user, age_user, age_user))
        potential_profiles = bot_data.cursor.fetchall()
        print(f"pot_prof: {potential_profiles}")

        if potential_profiles:
            potential_profiles = [profile for profile in potential_profiles if profile[3] != user_id]
            if potential_profiles:
                random_profile = random.choice(potential_profiles)

                random_profile_id = random_profile[3]

                print(random_profile_id)
                await state.finish()
                await show_anketa_random(message, random_profile_id=random_profile_id)  # Передайте параметр random_profile_id
            else:
                await message.answer(texts.radius)
        else:
            print("No close profiles found.")
            await bot_data.bot.send_message(message.chat.id, texts.not_found)
            await show_anketa()
            #  await search_profiles(message, state)  # Если расстояние больше 5 км, повторяем выбор профиля
        bot_data.conn.close()
    except Exception as e:
        bot_data.warning_log.warning(e)


# def check_distance(profile, message):
#     try:
#         conn = sqlite3.connect('maindb.db')
#         cursor = conn.cursor()
#
#         cursor.execute("SELECT latitude, longitude FROM users WHERE id = ?", (profile[0],))
#         result = cursor.fetchone()
#         lat1, lon1 = result
#
#         lat2, lon2 = profile[9], profile[10]  # Предполагая, что широта находится под индексом 9, а долгота - под индексом 10
#
#         R = 6371  # Радиус Земли в километрах
#
#         dlat = math.radians(lat2 - lat1)
#         dlon = math.radians(lon2 - lon1)
#
#         a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
#             math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
#         c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#
#         distance = R * c  # Расстояние между двумя точками в километрах
#         rounded_distance = round(distance)  # Округление до ближайшего километра
#         global rounded_distance
#         return rounded_distance
#     except Exception as e:
#         warning_log.warning(e)

@bot_data.dp.message_handler(state=bot_data.RegisterUser.waiting_for_loading_anket)
async def show_anketa_random(message, random_profile_id):
    try:
        # geo = ('📍', distance, 'км')

        photos_dir = os.path.join(os.getcwd(), 'photos', str(random_profile_id))  # Проверьте, что путь формируется правильно
        #
        # if not os.path.isdir(photos_dir):
        #     await message.reply("Фотографии не найдены")
        #     return

        photo_files = [file for file in os.listdir(photos_dir) if file.endswith('.jpg')]

        if not photo_files:
            await message.reply(texts.photo_not)
            return

        bot_data.cursor.execute("SELECT name, age, description FROM users WHERE id=?", (random_profile_id,))
        result = bot_data.cursor.fetchall()

        for row in result:
            name = row[0]
            age = row[1]
            description = row[2]
            geo = "Москва"
            media_group = [InputMediaPhoto(media=open(os.path.join(photos_dir, file), 'rb'),
                                           caption=(f'{name}, {age}, {geo}\n{description}')) for file in photo_files]

            keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
            button_like = types.KeyboardButton('👍')
            button_text = types.KeyboardButton('💌')
            button_super_like = types.KeyboardButton('⭐️')
            button_dislike = types.KeyboardButton('👎')
            button_sleep = types.KeyboardButton('🥱')
            keyboard_main.add(button_like, button_text, button_super_like, button_dislike, button_sleep)
            await bot_data.bot.send_message(message.chat.id, "🔍", reply_markup=keyboard_main)

            await bot_data.bot.send_media_group(message.chat.id, media=media_group)
    except Exception as e:
        bot_data.warning_log.warning(e)

async def handle_main_keyboard_press(message, bot, state, random_profile_id, texts):
    try:
        if message.text == '👍':
            conn = sqlite3.connect('maindb.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO likes (from_user_id, to_user_id, relevance) VALUES (?, ?, ?)
            ''', (message.from_user.id, random_profile_id, False))
            conn.commit()
            conn.close()
            await bot.send_message(random_profile_id, texts.liked)

            await show_anketa_random(message, state)

        elif message.text == '💌':
            await bot.send_message(message.chat.id, texts.what_write)
            while True:
                response = await bot.wait_for('message')
                if response.text:
                    like_text = response.text
                    data = await state.get_data()
                    random_profile_id = data.get("random_profile_id")
                    if random_profile_id:
                        await bot.send_message(random_profile_id, texts.liked_and_wrote + like_text)
                        break
                    else:
                        await bot.send_message(message.chat.id, texts.not_found_user)
                else:
                    await bot.send_message(message.chat.id, texts.empty_text)

        elif message.text == '⭐️':
            inline_keyboard = types.InlineKeyboardMarkup()
            inline_keyboard.row(
                types.InlineKeyboardButton(text='⚠️', callback_data='button1'),
                types.InlineKeyboardButton(text='🧸', callback_data='button2'),
                types.InlineKeyboardButton(text='🌺', callback_data='button3'),
            )

            await bot.send_message(message.chat.id, texts.exceptiton, reply_markup=inline_keyboard)
            await handle_inline_keyboard_press(message, bot)

        elif message.text == '👎':
            await show_anketa_random(message, state)

        elif message.text == '🥱':
            await bot.send_message(message.chat.id, texts.wait)
            keyboard_waiting = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            button_my_profile = types.KeyboardButton('👤')
            button_searching = types.KeyboardButton('🫂')
            button_stop = types.KeyboardButton('❌')
            keyboard_waiting.add(button_my_profile, button_searching, button_stop)
            await bot.send_message(message.chat.id, texts.options, reply_markup=keyboard_waiting)
            await waiting(message, state)
        else:
            await bot.send_message(message.chat.id, texts.strange_command)
    except Exception as e:
        bot_data.warning_log.warning(e)


async def handle_inline_keyboard_press(callback_query, bot):
    try:
        if callback_query.data == 'button1':
            return
        elif callback_query.data == 'button2':
            data = await state.get_data()
            random_profile_id = data.get("random_profile_id")
            if state == bot_data.RegisterUser.waiting_for_loading_anket:
                await bot.send_message(random_profile_id, texts.bear_gift)
        elif callback_query.data == 'button3':
            await bot.send_message(callback_query.message.chat.id, texts.flowers_delivery)
            return
        else:
            await bot.send_message(callback_query.message.chat.id, texts.strange_command)
    except Exception as e:
        bot_data.warning_log.warning(e)


async def waiting(callback_query, bot):
    return