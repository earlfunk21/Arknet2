from requests.auth import HTTPBasicAuth
import requests

from send_email import send_email

auth = HTTPBasicAuth("admin", "admin123")

url = "http://127.0.0.1:6901"

res = requests.get(f"{url}/api/inactive_users", headers={'Accept': 'application/json'}, auth=auth)

if res.status_code == 200:
    for email in res.json():
        html = """\
        <html>
        <body>
            <h1>Please don't forget to pay your bill</h1>
        </body>
        </html>
        """
        send_email(email, "Your plan has been expired", html)

