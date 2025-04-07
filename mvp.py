from aiogram import executor, Bot, Dispatcher, types
import auth
import bot_data
from dbase import *

if __name__ == "__mvp__" or 1 == 1:
    bot_data.show_logo()
    executor.start_polling(auth.bot_data.dp, skip_updates=True)