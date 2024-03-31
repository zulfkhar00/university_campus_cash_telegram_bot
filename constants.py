from enum import Enum


class StartResponse(Enum):
    new_join_reponse = """👋 Welcome! You are new to the bot.
In order to get your campus money balance and history inquiries, you have to grant me access to retrieve your data from Mealplans.

Here is how to do it:
1. Go to [Mealplans Account Settings](https://mealplans.nyu.edu).
2. Navigate to Grant Additional Access.
3. Scroll down and click Add.
4. Enter your personal email address (make sure all boxes are checked).
5. Click Done!

After that, you will receive a Guest Access email with login and password.

Please send them to me by typing /grant <login> <password>.

I will be waiting for ya! 😊
"""

    authorized_user_reponse = """🎉 Welcome! You are successfully authorized.

Just enter the campus money name to get balance and history.
"""


user_cannot_inquire_balance = """🙁 Oops! It seems you haven't granted me access to your MealPlan yet.

Please follow these steps to grant access:
👉 Go to [MealPlans Account Settings](https://mealplans.nyu.edu).
👉 Navigate to Grant Additional Access.
👉 Scroll down and click Add.
👉 Enter your personal email address (make sure all boxes are checked).
👉 Click Done!
"""
