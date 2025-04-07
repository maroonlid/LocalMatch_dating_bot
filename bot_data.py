from aiogram import executor, Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputMediaPhoto
from aiogram.types import ParseMode
import auth


import importlib
import logging
import math
import os
import random
import sqlite3
import time


if not os.path.exists('databases'):
    os.makedirs('databases')

if not os.path.exists('logs'):
    os.makedirs('logs')

if not os.path.exists('photos'):
    os.makedirs('photos')

if not os.path.exists('photos/man'):
    os.makedirs('photos/man')

if not os.path.exists('photos/woman'):
    os.makedirs('photos/woman')

db_path = os.path.join('databases', 'maindb.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS actions (
        from_who INTEGER,
        whom INTEGER,
        action TEXT,
        relevance BOOLEAN
    )
''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    number INTEGER,
    ban BOOLEAN, 
    national TEXT, 
    id INTEGER, 
    username TEXT, 
    my_sex TEXT, 
    sex_find TEXT, 
    name TEXT, 
    age INTEGER, 
    geo TEXT,
    latitude TEXT, 
    longitude TEXT, 
    description TEXT)''')




#  action = LIKE / LIKE&MSG / LIKE&PRESENT
#  relevance = TRUE / FALSE

conn.commit()

bot = Bot(token='6869311800:AAGBUxlCjBIdfi_Z1WEqmpVUPyUjCOrZBlI')
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(filename=os.path.join('logs', 'all_log.log'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
warning_log = logging.getLogger("warning_log")
warning_log.setLevel(logging.WARNING)
fh = logging.FileHandler(os.path.join('logs', 'warning_log.log'))
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
warning_log.addHandler(fh)

user_id = None
# texts = None
global random_profile_id
cities_ru = ["москва"]


class RegisterUser(StatesGroup):
    waiting_for_age = State()
    waiting_for_national = State()
    waiting_for_banned_curva = State()
    waiting_for_name = State()
    waiting_for_my_sex = State()
    waiting_for_sex_find = State()
    waiting_for_description = State()
    waiting_for_geo = State()
    waiting_for_alt_geo = State()
    waiting_for_photo_1 = State()
    waiting_for_q_1 = State()
    waiting_for_q_2 = State()
    waiting_for_q_3 = State()
    waiting_for_q_4 = State()
    waiting_for_q_5 = State()
    waiting_for_q_6 = State()
    waiting_for_q_7 = State()
    waiting_for_q_8 = State()
    waiting_for_q_9 = State()
    waiting_for_q_10 = State()
    waiting_for_profile = State()
    waiting_for_profile_start = State()
    waiting_for_prosmotr_anket = State()
    waiting_for_loading_anket = State()
    waiting = State()
    waiting_for_menu = State()
    waiting_for_inresult = State()


# Создание папки logs, если ее нет
if not os.path.exists('logs'):
    os.makedirs('logs')


def show_logo():
    print("┌───────────────────────────────────────────────────┐")
    print("│ _                 _                 _       _     │")
    print("│| | ___   ___ __ _| |_ __ ___   __ _| |_ ___| |__  │")
    print("│| |/ _ \ / __/ _` | | '_ ` _ \ / _` | __/ __| '_ \ │")
    print("│| | (_) | (_| (_| | | | | | | | (_| | || (__| | | |│")
    print("│|_|\___/ \___\__,_|_|_| |_| |_|\__,_|\__\___|_| |_|│")
    print("└───────────────────────────────────────────────────┘")