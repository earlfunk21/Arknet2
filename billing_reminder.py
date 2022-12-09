import datetime
from requests.auth import HTTPBasicAuth
import requests
from requests.exceptions import ConnectionError

from send_email import send_email


auth = HTTPBasicAuth("admin", "admin123")

url = "http://127.0.0.1:6901"

def get_html_almost(username, plan, date):
    return """\
            <html>
            <body>
                <h1>Hi! {}. Your plan was going to expire soon.</h1>
                <p>Plan: <b>{}</b></p><br/>
                <p>Expired on <b>{}</b>.</p>
            </body>
            </html>
            """.format(username, plan, date)


def get_html_expired(username, plan):
    return """\
            <html>
            <body>
                <h1>Hi! {}. Your plan has been expired.</h1>
                <p>Plan: <b>{}</b></p><br/>
                <p>Please update your plan now.</p>
            </body>
            </html>
            """.format(username, plan)

def check_almost_expired():
    try:
        res = requests.get(f"{url}/api/almost_expired_users", headers={'Accept': 'application/json'}, auth=auth)

        if res.status_code == 200:
            users = []
            if res is not list:
                users.append(res.json())
            else:
                users = res.json()
            for user in users:
                send_email(None, "Billing reminder", get_html_almost(user["username"], user["plan"], user["date"]))

    except ConnectionError:
        print("Connection error")


def check_expired_users():
    try:
        res = requests.get(f"{url}/api/inactive_users", headers={'Accept': 'application/json'}, auth=auth)

        if res.status_code == 200:
            users = []
            if res is not list:
                users.append(res.json())
            else:
                users = res.json()
            for user in users:
                send_email(None, "Billing reminder", get_html_expired(user["username"], user["plan"]))

    except ConnectionError:
        print("Connection error")


if __name__ == "__main__":
    check_almost_expired()
    check_expired_users()

