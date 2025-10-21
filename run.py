import os
import re

import htpy as h
import httpx
import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, redirect, request, session, url_for
from flask_caching import Cache
from steam_web_api import Steam

from components import (
    base_layout,
    common_games_list,
    friends_list_page,
    games_page,
    loading_spinner,
    login_page,
    private_profile_message,
)

load_dotenv()

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), send_default_pii=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configure filesystem cache
cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
os.makedirs(cache_dir, exist_ok=True)

app.config["CACHE_TYPE"] = "FileSystemCache"
app.config["CACHE_DIR"] = cache_dir
app.config["CACHE_DEFAULT_TIMEOUT"] = 900

cache = Cache(app)

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
STEAM_API_URL = "http://api.steampowered.com/ISteamUser"


steam = Steam(STEAM_API_KEY)


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


UNAUTHORIZED = 401


@cache.memoize(timeout=900)
def get_steam_friends(steam_id):
    try:
        response = httpx.get(
            f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&relationship=friend"
        )

        data = response.json()

        if "friendslist" not in data:
            if response.status_code == 401 or (
                isinstance(data, dict) and data.get("error")
            ):
                return UNAUTHORIZED
            return []  # Empty friends list

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

    content = h.div(
        id="content-area",
        **{
            "hx-get": url_for("load_friends"),
            "hx-trigger": "load",
            "hx-swap": "innerHTML",
        },
    )[loading_spinner("Loading your friends...")]

    return str(base_layout(content))


@app.route("/load-friends")
def load_friends():
    steam_id = session.get("steam_id")
    if not steam_id:
        return redirect(url_for("index"))

    friends = get_steam_friends(steam_id)

    if friends == UNAUTHORIZED:
        cache.delete_memoized(get_steam_friends, steam_id)
        return str(private_profile_message())

    # Get user's own details for display
    user_details = steam.users.get_user_details(steam_id)
    user_name = user_details["player"]["personaname"]

    return str(friends_list_page(friends, user_name))


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
    return str(games_page(selected_friends))


@app.route("/load-common-games")
def load_common_games():
    friend_ids_str = request.args.get("friend_ids", "")
    if not friend_ids_str:
        return str(h.p["No friends selected."])

    friend_ids = friend_ids_str.split(",")

    steam_id = session.get("steam_id")
    if not steam_id:
        return redirect(url_for("index"))

    all_user_ids = [steam_id] + friend_ids
    total_users = len(all_user_ids)

    try:
        user_details = {}
        for user_id in all_user_ids:
            try:
                details = steam.users.get_user_details(user_id)
                user_details[user_id] = details["player"]["personaname"]
            except Exception:
                user_details[user_id] = "Unknown User"

        user_games = {}
        all_games = {}
        game_owners = {}

        for user_id in all_user_ids:
            games = steam.users.get_owned_games(user_id)
            if games and "games" in games:
                user_games[user_id] = set()
                for game in games["games"]:
                    appid = game["appid"]
                    user_games[user_id].add(appid)
                    if appid not in all_games:
                        all_games[appid] = game
                    if appid not in game_owners:
                        game_owners[appid] = []
                    game_owners[appid].append(user_id)
            else:
                user_games[user_id] = set()

        game_owner_counts = {}
        for appid in all_games.keys():
            count = sum(
                1 for user_game_set in user_games.values() if appid in user_game_set
            )
            game_owner_counts[appid] = count

        min_owners = max(2, int(total_users * 0.5))

        common_games = []
        for appid, count in game_owner_counts.items():
            if count >= min_owners:
                game_info = all_games[appid].copy()
                game_info["owner_count"] = count
                game_info["owner_names"] = [
                    user_details[uid] for uid in game_owners[appid]
                ]
                common_games.append(game_info)

        common_games.sort(key=lambda x: (-x["owner_count"], x.get("name", "").lower()))

        return str(common_games_list(common_games, total_users))

    except Exception as e:
        print(f"Error fetching common games: {e}")
        import traceback

        traceback.print_exc()
        return str(
            h.div(style="text-align: center; padding: 2rem;")[
                h.p["Error loading games. Please try again."],
            ]
        )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
