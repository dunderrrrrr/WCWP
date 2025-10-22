import logging
import os

import htpy as h
import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, redirect, request, session, url_for
from flask_caching import Cache

import steam as steam_api
from components import (
    base_layout,
    common_games_list,
    error_loading_games_warning,
    friends_list_page,
    games_page,
    load_friends_content,
    login_page,
    private_profile_message,
)

load_dotenv()

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), send_default_pii=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
os.makedirs(cache_dir, exist_ok=True)

app.config["CACHE_TYPE"] = "FileSystemCache"
app.config["CACHE_DIR"] = cache_dir
app.config["CACHE_DEFAULT_TIMEOUT"] = 900

cache = Cache(app)


@cache.memoize(timeout=900)
def get_steam_friends(steam_id: str) -> list[dict]:
    return steam_api.get_steam_friends_from_api(steam_id)


@app.route("/")
def index() -> str:
    steam_id = session.get("steam_id")
    if not steam_id:
        return str(login_page())

    return str(base_layout(load_friends_content()))


@app.route("/load-friends")
def load_friends():
    steam_id = session.get("steam_id")
    if not steam_id:
        return redirect(url_for("index"))

    try:
        friends = get_steam_friends(steam_id)
    except steam_api.SteamProfileNotPublic:
        cache.delete_memoized(get_steam_friends, steam_id)
        return str(private_profile_message())

    user_details = steam_api.get_user_details(steam_id)
    user_name = user_details["player"]["personaname"]

    return str(friends_list_page(friends, user_name))


@app.route("/login")
def login():
    if "steam_id" in session:
        return redirect(url_for("index"))
    return redirect(steam_api.get_steam_login_url())


@app.route("/authorize")
def authorize():
    steam_id = steam_api.validate_steam_login()

    if steam_id:
        session["steam_id"] = steam_id
        return redirect(url_for("index"))
    else:
        logging.error("Failed to authenticate with Steam")


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

    try:
        all_user_ids = [steam_id] + friend_ids
        total_users = len(all_user_ids)
        common_games = steam_api.get_common_games(all_user_ids, total_users)
        return str(common_games_list(common_games, total_users))
    except Exception as e:
        logging.error("Error fetching common games", exception=str(e))
        return str(error_loading_games_warning())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
