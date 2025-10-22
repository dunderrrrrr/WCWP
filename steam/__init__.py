import os
import re

import httpx
from dotenv import load_dotenv
from flask import request, url_for
from steam_web_api import Steam  # type: ignore[import-untyped]

load_dotenv()

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
STEAM_API_URL = "http://api.steampowered.com/ISteamUser"
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
steam = Steam(STEAM_API_KEY)


class SteamProfileNotPublic(Exception): ...


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


def get_steam_friends_from_api(steam_id: str) -> list[dict]:
    response = httpx.get(
        f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&relationship=friend"
    )

    data = response.json()

    if "friendslist" not in data:
        if response.status_code == 401 or (
            isinstance(data, dict) and data.get("error")
        ):
            raise SteamProfileNotPublic
        return []  # Empty friends list

    friend_ids = [friend["steamid"] for friend in data["friendslist"]["friends"]]

    return [steam.users.get_user_details(friend_id) for friend_id in friend_ids]


def get_user_details(steam_id: str) -> dict:
    return steam.users.get_user_details(steam_id)


def get_owned_games(user_id: str) -> dict:
    return steam.users.get_owned_games(user_id)


def get_common_games(all_user_ids, total_users):
    user_details = {}
    for user_id in all_user_ids:
        try:
            details = get_user_details(user_id)
            user_details[user_id] = details["player"]["personaname"]
        except Exception:
            user_details[user_id] = "Unknown User"

    user_games = {}
    all_games = {}
    game_owners = {}

    for user_id in all_user_ids:
        games = get_owned_games(user_id)
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
            game_info["owner_names"] = [user_details[uid] for uid in game_owners[appid]]
            common_games.append(game_info)

    return sorted(
        common_games, key=lambda x: (-x["owner_count"], x.get("name", "").lower())
    )
