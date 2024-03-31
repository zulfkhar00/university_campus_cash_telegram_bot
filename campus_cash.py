import os
import time
from enum import Enum
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup
import requests
import telebot
from dotenv import load_dotenv

load_dotenv()


class Money(Enum):
    campus = 'AD - Campus Dirhams'
    falcon = 'AD - Falcon Dirhams'
    swipes = 'AD - Full Board '
    flex = 'AD - Flex Dining Dirhams'


SKEY_FILE_PATH = "skey.txt"
SKEY = ""
API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")

if not API_KEY:
    raise ValueError(
        "Telegram bot API key is not set in the environment variables.")

bot = telebot.TeleBot(API_KEY)

# -------------------------------------------Network related methods--------------------------------------------------------
# returns Campus dirham balance


def get_money_balance(s, money):
    money_table = s.find('table', id=money.value)

    if money_table:
        # Find the row containing the current balance
        current_balance_row = money_table.find_all('tr')[1]
        if current_balance_row:
            # Find the cell containing the balance value
            balance_cell = current_balance_row.find('td', class_='jsa_amount')
            if balance_cell:
                # Extract the balance value
                balance_value = balance_cell.contents[0].strip()
                balance_value += " AED" if money == Money.flex else ""
                return balance_value
            else:
                raise ValueError("Balance cell not found.")
        else:
            raise ValueError("Current balance row not found.")
    else:
        raise ValueError("Too much trial. Try later :)")

# returns list of Campus dirham transactions where each transaction is like: [date_time_th, place, transaction_amount]


def get_money_history(s, money):
    money_table = s.find('table', id=money.value)

    if money_table:
        # Find the row containing the current balance
        rows = money_table.find_all('tr')
        if len(rows) <= 2:
            return []
        transaction_rows = rows[2:]
        results = []
        for transaction_tr in transaction_rows:
            date_time = transaction_tr.find(
                'th', class_='jsa_month').contents[0].strip()
            place = transaction_tr.find(
                'td', class_='jsa_desc').contents[0].strip()
            transaction_amount = transaction_tr.find(
                'td', class_='jsa_amount').contents[0].strip()
            if money == Money.flex:
                transaction_amount = '{:.2f}'.format(
                    int(transaction_amount)/100)

            results.append([date_time, place, transaction_amount])
        return results
    raise ValueError("Too much trial. Try later :)")


def validate_skey():
    # Validate SKEY
    url = 'https://atriumconnect.atriumcampus.com/login.php?cid=156&guest=1'
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    # ASSIGN SKEY
    global SKEY
    SKEY = soup.find('input', {'name': 'skey'}).get('value')
    # cache SKEY locally
    with open(SKEY_FILE_PATH, 'w') as file:
        file.write(SKEY)
        file.close()

    mp_encoder = MultipartEncoder(
        fields={
            'loginphrase': 'zhanarbek.zulfkhar@gmail.com',
            'password': 'Y2P1P3QDBN'
        }
    )
    requests.post(
        url+'&skey='+SKEY+'&fullscreen=1&wason=',
        data=mp_encoder,
        headers={'Content-Type': mp_encoder.content_type}
    )
    time.sleep(2.0)

# gets new SKEY and validates it if not valid or gets money_table and returns it


def validate_skey_if_needed():
    checking_url = 'https://atriumconnect.atriumcampus.com/index.php?skey='+SKEY+'&cid=156&'
    res = requests.get(checking_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    money_table = soup.find('table', id=Money.campus)
    if not money_table:
        validate_skey()


def get_skey():
    # Check if file exists and is not empty
    if os.path.isfile(SKEY_FILE_PATH) and os.path.getsize(SKEY_FILE_PATH) > 0:
        # Read SKEY from local cache file
        with open(SKEY_FILE_PATH, 'r') as file:
            global SKEY
            SKEY = file.read()
            file.close()
    validate_skey_if_needed()
# -------------------------------------------Network End--------------------------------------------------------------------


def check_if_correct(msg):
    if msg.text in ['campus', 'flex', 'falcon', 'swipe']:
        return True
    return False


@bot.message_handler(func=check_if_correct)
def get_data(message):
    get_skey()
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
