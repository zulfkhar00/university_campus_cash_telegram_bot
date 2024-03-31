import os
from bs4 import BeautifulSoup
import requests
import telebot
from dotenv import load_dotenv
from network_manager import *
from database_manager import *
import constants

load_dotenv()

API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")

if not API_KEY:
    raise ValueError(
        "Telegram bot API key is not set in the environment variables.")

bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['start'])
def handle_start(message):
    telegram_user = message.from_user
    user = authorize_user(telegram_user)
    access_granted_to_mealplans = user.get('mealplan_password', None)
    if access_granted_to_mealplans:
        ans = constants.StartResponse.authorized_user_reponse.value
    else:
        ans = constants.StartResponse.new_join_reponse.value
    bot.reply_to(message, ans)


@bot.message_handler(commands=['grant'])
def handle_grant(message):
    # Check if the command has exactly two arguments
    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "Usage: /grant <login> <password>")
        return

    # Extract login and password from the arguments
    login, password = args
    update_access_credentials(message.from_user.id, login, password)
    bot.reply_to(
        message, "Success! Now you are authorized. Just enter the campus money name and I will give you balance and history inquiry.")


def check_if_correct(msg):
    if msg.text not in ['campus', 'flex', 'falcon', 'swipe']:
        return False
    user_can_inquire_balance = check_user(msg.from_user)
    if not user_can_inquire_balance:
        bot.reply_to(msg, constants.user_cannot_inquire_balance)
    return user_can_inquire_balance


@bot.message_handler(func=check_if_correct)
def get_data(message):
    mealplan_credentials = get_mealplan_credentials_for(message.from_user.id)
    SKEY = get_skey(mealplan_credentials)
    url = 'https://atriumconnect.atriumcampus.com/index.php?skey='+SKEY+'&cid=156&'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    balance = ""
    transactions = []

    try:
        if message.text == 'campus':
            balance += get_money_balance(soup, Money.campus)
            transactions += get_money_history(soup, Money.campus)
        elif message.text == 'flex':
            balance += get_money_balance(soup, Money.flex)
            transactions += get_money_history(soup, Money.flex)
        elif message.text == 'falcon':
            balance += get_money_balance(soup, Money.falcon)
            transactions += get_money_history(soup, Money.falcon)
        else:
            balance += get_money_balance(soup, Money.swipes)
            transactions += get_money_history(soup, Money.swipes)
    except ValueError as e:
        bot.reply_to(message, str(e))
        return

    ans = ""
    ans += balance
    ans += "\n\n"
    for date_time, place, transaction_amount in transactions:
        ans += date_time + " | " + transaction_amount + " | " + place + "\n"

    bot.reply_to(message, ans)


bot.polling()
