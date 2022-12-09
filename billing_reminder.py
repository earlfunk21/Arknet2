import datetime
from requests.auth import HTTPBasicAuth
import requests
from requests.exceptions import ConnectionError

from send_email import send_email


auth = HTTPBasicAuth("admin", "admin123")

url = "http://127.0.0.1:6901"

try:
    res = requests.get(f"{url}/api/almost_expired_users", headers={'Accept': 'application/json'}, auth=auth)

    if res.status_code == 200:
        for user in res.json():
            date = datetime.datetime.strptime(user["date"], "%Y-%m-%d") - datetime.datetime.today()
            username = user["username"]
            html = """\
            <html>
            <body>
                <h1>Hi! {}. Your Plan was going to expire soon.</h1>
                <h3>Days left before expiration: {}</h3>
            </body>
            </html>
            """.format(username, date.days)
            send_email(None, "Billing reminder", html)

except ConnectionError:
    print("Connection error")


try:
    res = requests.get(f"{url}/api/inactive_users", headers={'Accept': 'application/json'}, auth=auth)

    if res.status_code == 200:
        for user in res.json():
            username = user["username"]
            html = """\
            <html>
            <body>
                <h1>Hi! {}. Your plan has been expired.</h1>
                <p>Please update your plan now.</p>
            </body>
            </html>
            """.format(username)
            send_email(None, "Billing reminder", html)
except ConnectionError:
    print("Connection error")


