import os
import json
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"
TOKEN_FILE = os.path.join("secrets", "token.json")


class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        code = query.get("code", [None])[0]

        if code is None:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"OAuth error")
            return

        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
        )

        token = response.json()

        data_to_save = {
            "access_token": token["access_token"],
            "expires_at": token["expires_at"],
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(data_to_save, f)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Token retrieved. You can close this page")


def get_access_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)

            expires_at = data["expires_at"]
            access_token = data["access_token"]
            if expires_at and access_token:
                if datetime.now().timestamp() < (expires_at - 300):
                    return access_token

    scope = "read,activity:read_all,profile:read_all"
    auth_url = f"http://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope={scope}"

    webbrowser.open(auth_url)
    server = HTTPServer(("localhost", 8000), OAuthHandler)
    server.handle_request()

    with open(TOKEN_FILE) as f:
        return json.load(f)["access_token"]


def main():
    token = get_access_token()
    print(f"TOKEN : {token}")


if __name__ == "__main__":
    main()
