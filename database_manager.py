
from pymongo.mongo_client import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

username = quote_plus(MONGO_USERNAME)
password = quote_plus(MONGO_PASSWORD)
cluster = 'cluster0.xbstwqr.mongodb.net'
uri = "mongodb+srv://" + username + ":" + password + "@" + \
    cluster + "/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri)
db = client["main"]
users_collection = db["users"]


def authorize_user(telegram_user):
    query = {"user_id": telegram_user.id}
    user = users_collection.find_one(query)
    if not user:
        user_document = {
            "user_id": telegram_user.id,
            "username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "mealplan_login": None,
            "mealplan_password": None
        }
        users_collection.insert_one(user_document)
    return users_collection.find_one(query)


def update_access_credentials(user_id, login, password):
    query = {"user_id": user_id}
    update = {"$set": {"mealplan_login": login, "mealplan_password": password}}
    users_collection.update_one(query, update)


def check_user(telegram_user):
    query = {"user_id": telegram_user.id}
    user = users_collection.find_one(query)
    return user.get("mealplan_password", None) != None


def get_mealplan_credentials_for(user_id):
    query = {"user_id": user_id}
    user = users_collection.find_one(query)
    return {
        'login': user.get("mealplan_login", None),
        'password': user.get("mealplan_password", None)
    }


# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
