import datetime
from requests.auth import HTTPBasicAuth
import requests
from requests.exceptions import ConnectionError
import json

from send_email import send_email


auth = HTTPBasicAuth("admin", "admin123")

url = "https://app.arknetfiber.com"

def get_html_almost(username, plan, date):
    return """\
            <html>
            <body>
                <h1>Hi! {}. Your plan: {}. was going to expire soon.</h1>
                <p>Expired on <b>{}</b>.</p>
            </body>
            </html>
            """.format(username, plan, date)


def get_html_expired(username, plan):
    return """\
            <html>
            <body>
                <h1>Hi! {}. Your plan: {}. has been expired.</h1>
                <p>Please update your plan now.</p>
            </body>
            </html>
            """.format(username, plan)

def check_almost_expired():
    try:
        res = requests.get(f"{url}/api/almost_expired_users", headers={'Accept': 'application/json'}, auth=auth)

        if res.status_code == 200:
            if type(res.json()) is list:
                for user in res.json():
                    username = user["username"]
                    plan = user["plan"]
                    date = user["date"]
                    print(username, plan, date)
                    send_email(None, "Billing reminder", get_html_almost(username, plan, date))
            else:
                username = res.json()["username"]
                plan = res.json()["plan"]
                date = res.json()["date"]
                send_email(None, "Billing reminder", get_html_almost(username, plan, date))

    except ConnectionError:
        print("Connection error")


def check_expired_users():
    try:
        res = requests.get(f"{url}/api/inactive_users", headers={'Accept': 'application/json'}, auth=auth)

        if res.status_code == 200:
            if type(res.json()) is list:
                for user in res.json():
                    username = user["username"]
                    plan = user["plan"]
                    send_email(None, "Billing reminder", get_html_expired(username, plan))
            else:
                username = res.json()["username"]
                plan = res.json()["plan"]
                send_email(None, "Billing reminder", get_html_expired(username, plan))
            

    except ConnectionError:
        print("Connection error")


if __name__ == "__main__":
    check_almost_expired()
    check_expired_users()

