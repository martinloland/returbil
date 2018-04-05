import http.client
import urllib


def send_push(title, message, url=None, token=None, user=None):
    RETURBIL_PUSH_TOKEN = token
    PUSHOVER_USER_KEY_MARTIN = user
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    if url:
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode({
                         "token": RETURBIL_PUSH_TOKEN,
                         "user": PUSHOVER_USER_KEY_MARTIN,
                         "title": title,
                         "message": message,
                         "url": url
                     }), {"Content-type": "application/x-www-form-urlencoded"})
    else:
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode({
                         "token": RETURBIL_PUSH_TOKEN,
                         "user": PUSHOVER_USER_KEY_MARTIN,
                         "title": title,
                         "message": message
                     }), {"Content-type": "application/x-www-form-urlencoded"})
    response = conn.getresponse()
    if response.status is not 200:
        print(response.status)
