import datetime
from requests.auth import HTTPBasicAuth
import requests
from requests.exceptions import ConnectionError

from send_email import send_email


auth = HTTPBasicAuth("admin", "admin123")

url = "http://127.0.0.1:6901"

def get_html_almost(username, days):
    return """\
            <html>
            <body>
                <h1>Hi! {}. Your Plan was going to expire soon.</h1>
                <h3>Days left before expiration: {}</h3>
            </body>
            </html>
            """.format(username, days)


def get_html_expired(username):
    return """\
            <html>
            <body>
                <h1>Hi! {}. Your plan has been expired.</h1>
                <p>Please update your plan now.</p>
            </body>
            </html>
            """.format(username)

def check_almost_expired():
    try:
        res = requests.get(f"{url}/api/almost_expired_users", headers={'Accept': 'application/json'}, auth=auth)

        if res.status_code == 200:
            for user in res.json():
                date = datetime.datetime.strptime(user["date"], "%Y-%m-%d") - datetime.datetime.today()
                username = user["username"]
                send_email(None, "Billing reminder", get_html_almost(username, date.days))

    except ConnectionError:
        print("Connection error")


def check_expired_users():
    try:
        res = requests.get(f"{url}/api/inactive_users", headers={'Accept': 'application/json'}, auth=auth)

        if res.status_code == 200:
            if res is list:
                for user in res.json():
                    username = user["username"]
                    send_email(None, "Billing reminder", get_html_expired(username))
            else:
                username = res.json()["username"]
                send_email(None, "Billing reminder", get_html_expired(username))

    except ConnectionError:
        print("Connection error")


if __name__ == "__main__":
    check_almost_expired()
    check_expired_users()

