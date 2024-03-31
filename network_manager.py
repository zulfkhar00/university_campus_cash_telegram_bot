import os
import time
from enum import Enum
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup
import requests

SKEY_FILE_PATH = "skey.txt"


class Money(Enum):
    campus = 'AD - Campus Dirhams'
    falcon = 'AD - Falcon Dirhams'
    swipes = 'AD - Full Board '
    flex = 'AD - Flex Dining Dirhams'

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


def validate_skey(mealplan_credentials):
    # Validate SKEY
    url = 'https://atriumconnect.atriumcampus.com/login.php?cid=156&guest=1'
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    SKEY = soup.find('input', {'name': 'skey'}).get('value')
    # cache SKEY locally
    with open(SKEY_FILE_PATH, 'w') as file:
        file.write(SKEY)
        file.close()

    mp_encoder = MultipartEncoder(
        fields={
            'loginphrase': mealplan_credentials['login'],
            'password': mealplan_credentials['password']
        }
    )
    requests.post(
        url+'&skey='+SKEY+'&fullscreen=1&wason=',
        data=mp_encoder,
        headers={'Content-Type': mp_encoder.content_type}
    )
    time.sleep(1.2)
    return SKEY

# gets new SKEY and validates it if not valid or gets money_table and returns it


def validate_skey_if_needed(SKEY, mealplan_credentials):
    checking_url = 'https://atriumconnect.atriumcampus.com/index.php?skey='+SKEY+'&cid=156&'
    res = requests.get(checking_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    money_table = soup.find('table', id=Money.campus)
    if not money_table:
        return validate_skey(mealplan_credentials)
    return SKEY


def get_skey(mealplan_credentials):
    SKEY = ""
    # Check if file exists and is not empty
    if os.path.isfile(SKEY_FILE_PATH) and os.path.getsize(SKEY_FILE_PATH) > 0:
        # Read SKEY from local cache file
        with open(SKEY_FILE_PATH, 'r') as file:
            SKEY = file.read()
            file.close()
    return validate_skey_if_needed(SKEY, mealplan_credentials)
