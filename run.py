import base64
import json
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
    invalid_share_link_warning,
    load_friends_content,
    loading_spinner,
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


@app.route("/refresh-friends")
def refresh_friends():
    steam_id = session.get("steam_id")
    if not steam_id:
        return redirect(url_for("index"))

    cache.delete_memoized(get_steam_friends, steam_id)

    # Return loading spinner that will trigger the actual load
    return str(
        h.div(
            **{
                "hx-get": url_for("load_friends"),
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            }
        )[loading_spinner("Refreshing friends list...")]
    )


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
    steam_id = session.get("steam_id")
    all_ids = [steam_id] + selected_friends if steam_id else selected_friends
    return str(games_page(selected_friends, all_ids))


@app.route("/load-common-games")
def load_common_games():
    friend_ids_str = request.args.get("friend_ids", "")
    if not friend_ids_str:
        return str(h.p["No friends selected."])

    friend_ids = friend_ids_str.split(",")

    share_data_encoded = request.args.get("share_data")
    steam_id = session.get("steam_id")

    # When share_data is present, friend_ids already contains all users from the share link
    # Add logged in user if they're viewing the shared link and logged in
    if share_data_encoded:
        # Shared link: add current user if logged in and not already in the list
        if steam_id and steam_id not in friend_ids:
            all_user_ids = [steam_id] + friend_ids
        else:
            all_user_ids = friend_ids
    else:
        # Normal flow: add current user to friend selection
        all_user_ids = [steam_id] + friend_ids if steam_id else friend_ids

    try:
        total_users = len(all_user_ids)
        common_games = steam_api.get_common_games(all_user_ids, total_users)
        return str(common_games_list(common_games, total_users, share_data_encoded))
    except Exception as e:
        logging.error("Error fetching common games", extra={"exception": str(e)})
        return str(error_loading_games_warning())


@app.route("/shared/<data>")
def shared_games(data):
    """Display shared games from base64-encoded JSON data."""
    try:
        decoded_bytes = base64.urlsafe_b64decode(data)
        shared_data = json.loads(decoded_bytes)

        friend_ids = shared_data.get("friend_ids", [])
        if not friend_ids:
            logging.error("Error decoding shared link", extra={"data": data})
            return str(base_layout(invalid_share_link_warning()))

        friend_ids_param = ",".join(friend_ids)

        content = h.div[
            h.div(
                id="games-list",
                hx_get=url_for(
                    "load_common_games", friend_ids=friend_ids_param, share_data=data
                ),
                hx_trigger="load",
                hx_swap="innerHTML",
            )[loading_spinner("Finding common games...")],
        ]
        return str(base_layout(content))
    except Exception as _:
        logging.error("Error decoding shared link", extra={"data": data})
        return str(base_layout(invalid_share_link_warning()))


@app.route("/status")
def status():
    return "ok"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
