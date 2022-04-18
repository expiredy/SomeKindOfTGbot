from turtle import right
from telebot import types

import asyncio
import requests

from pandas import read_csv

#Hints 
from collections.abc import Callable

#system variables and constants
from os import getenv
from dotenv import load_dotenv
load_dotenv(".env")
TELEGRAM_BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')
DATABASE_PATH_NAME  = getenv('DATABASE_PATH_NAME')

from telebot.async_telebot import AsyncTeleBot

TOTAL_BOOKS_VIEW_ON_PAGE = 4

def get_all_available_data(from_index: int, to_index: int) -> list:
    if DATABASE_PATH_NAME.endswith(".csv"):
        return read_csv(DATABASE_PATH_NAME, sep=";").values.tolist()[from_index:to_index]
    return []


def generate_markup(page_index: int = 1, from_index: int = 0):
    def get_article_link_title(link: str) -> str:
        return link.replace("https://telegra.ph/", "").replace(" ", "")

    button_column = []

    for index, link in enumerate(get_all_available_data(from_index + TOTAL_BOOKS_VIEW_ON_PAGE * (page_index - 1),
                                                        from_index + TOTAL_BOOKS_VIEW_ON_PAGE * page_index)):
        article_title = "Книга номер " + str(index)
        try:
            article_title = requests.get(f"https://api.telegra.ph/getPage/{get_article_link_title(link[-1])}?return_content=false").json()["result"]["title"]
        except:
            pass

        button_column.append([types.InlineKeyboardButton(text=article_title, url=link[-1])])
    markup = types.InlineKeyboardMarkup(button_column)
    markup.add(types.InlineKeyboardButton(text="<", callback_data="-1"),
               types.InlineKeyboardButton(text=page_index, callback_data="current_data"),
               types.InlineKeyboardButton(text=">", callback_data="1"))
    return markup


bot_controller = AsyncTeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

@bot_controller.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    index = int(call.message.reply_markup.keyboard[-1][1].text) + int(call.data)
    await bot_controller.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=generate_markup(index))


@bot_controller.message_handler(commands=['start', 'help'])
async def start(message: types.Message):


    await bot_controller.send_message(message.chat.id, "Список доступных книг:", reply_markup=generate_markup())


asyncio.run(bot_controller.infinity_polling())

