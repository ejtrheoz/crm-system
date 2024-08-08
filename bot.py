import config
import telebot
from telebot import types
from telebot.types import WebAppInfo
import pandas as pd
import sqlite3
import os

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['database'])
def handle_command(message):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton("Add product", url="http://195.189.227.67:8080"))
    keyboard.add(types.InlineKeyboardButton("Delete product", url="http://195.189.227.67:8080/delete"))
    keyboard.add(types.InlineKeyboardButton("Show product", url="http://195.189.227.67:8080/show"))
    keyboard.add(types.InlineKeyboardButton("Change product", url="http://195.189.227.67:8080/change"))

    bot.send_message(message.from_user.id, "Database commands:", reply_markup=keyboard)

@bot.message_handler(commands=['orders'])
def handle_command(message):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton("Add Order", url="http://195.189.227.67:8080/form"))
    keyboard.add(types.InlineKeyboardButton("Orders List", url="http://195.189.227.67:8080/orders"))

    bot.send_message(message.from_user.id, "Orders commands:", reply_markup=keyboard)


@bot.message_handler(commands=['clients'])
def handle_command(message):
    conn = sqlite3.connect('web/clients.db')
    query = "SELECT * FROM Clients"

    df = pd.read_sql_query(query, conn)
    
    excel_file_path = 'clients.xlsx'
    df.to_excel(excel_file_path, index=False)

    f = open("clients.xlsx", "rb")
    bot.send_document(message.from_user.id, f)

    f.close()
    conn.close()
    os.remove("clients.xlsx")


@bot.message_handler(commands=['profit'])
def handle_command(message):
    conn = sqlite3.connect('web/profit.db')
    query = """
        WITH total AS (
        SELECT id,
            SUM(sell_price-buy_price) AS margin
        FROM Profit
        GROUP BY id
        )
            
        SELECT *
        FROM total
        JOIN
        (SELECT SUM(margin) AS total_sum
        FROM total)

        """

    df = pd.read_sql_query(query, conn)
    
    excel_file_path = 'profit.xlsx'
    df.to_excel(excel_file_path, index=False)

    f = open("profit.xlsx", "rb")
    bot.send_document(message.from_user.id, f)

    f.close()
    conn.close()
    os.remove("profit.xlsx")



if __name__ == '__main__':
    bot.infinity_polling()
