from flask import Flask, redirect, url_for, session, request
import httpx
import re
import os
import htpy as h
from dotenv import load_dotenv
from steam_web_api import Steam
from components import base_layout, friends_list_page, games_page
from flask_caching import Cache

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
STEAM_API_URL = "http://api.steampowered.com/ISteamUser"


# Configure cache
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 300,
    },
)


steam = Steam(STEAM_API_KEY)


def login_page():
    """Login page content"""
    return base_layout(
        h.div[
            h.p(style="text-align: center; margin-bottom: 1.5rem;")[
                "Sign in with your Steam account to find games you can play with your friends"
            ],
            h.a(".steam-btn", href=url_for("login"))["Sign in through Steam"],
        ],
        container_width="500px",
    )


def get_steam_login_url():
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": url_for("authorize", _external=True),
        "openid.realm": request.host_url,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    query_string = "&".join(
        [
            f"{key}={httpx.QueryParams({key: value})[key]}"
            for key, value in params.items()
        ]
    )
    return f"{STEAM_OPENID_URL}?{query_string}"


def validate_steam_login():
    params = {
        key: value for key, value in request.args.items() if key.startswith("openid.")
    }
    params["openid.mode"] = "check_authentication"

    response = httpx.post(STEAM_OPENID_URL, data=params)

    if "is_valid:true" in response.text:
        claimed_id = request.args.get("openid.claimed_id", "")
        match = re.search(r"steamcommunity.com/openid/id/(\d+)", claimed_id)
        if match:
            return match.group(1)

    return None


@cache.memoize(timeout=900)
def get_steam_friends(steam_id):
    """Get Steam friends list with full details"""
    try:
        # Get the friends list
        response = httpx.get(
            f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&relationship=friend"
        )

        data = response.json()
        if "friendslist" not in data:
            return []  # user is probably private

        friend_ids = [friend["steamid"] for friend in data["friendslist"]["friends"]]

        return [steam.users.get_user_details(friend_id) for friend_id in friend_ids]

    except Exception as e:
        print(f"Error fetching friends: {e}")
        import traceback

        traceback.print_exc()
        return []


@app.route("/")
def index():
    steam_id = session.get("steam_id")

    if not steam_id:
        return str(login_page())

    friends = get_steam_friends(steam_id)
    return str(friends_list_page(friends))


@app.route("/login")
def login():
    if "steam_id" in session:
        return redirect(url_for("index"))
    return redirect(get_steam_login_url())


@app.route("/authorize")
def authorize():
    steam_id = validate_steam_login()

    if steam_id:
        session["steam_id"] = steam_id
        return redirect(url_for("index"))
    else:
        return "Failed to authenticate with Steam", 401


@app.route("/logout")
def logout():
    session.pop("steam_id", None)
    return redirect(url_for("index"))


@app.route("/select-games", methods=["POST"])
def select_games():
    selected_friends = request.form.getlist("selected_friends")
    session["selected_friends"] = selected_friends
    return str(games_page(len(selected_friends)))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
