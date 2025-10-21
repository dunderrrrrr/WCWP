import htpy as h
from flask import url_for


def base_layout(content, container_width="800px"):
    return h.html(data_theme="dark")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1"),
            h.title["WCWP - What Can We Play"],
            h.link(
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css",
            ),
            h.link(rel="preconnect", href="https://fonts.googleapis.com"),
            h.link(
                rel="preconnect", href="https://fonts.gstatic.com", crossorigin=True
            ),
            h.link(
                href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap",
                rel="stylesheet",
            ),
            h.script(
                defer=True,
                src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js",
            ),
            h.script(src="https://unpkg.com/htmx.org@2.0.3"),
            h.style[
                f"""
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 2rem 1rem;
                }}
                .container {{
                    max-width: {container_width};
                    width: 100%;
                    transition: max-width 0.3s;
                    height: 100%;
                }}
                main {{
                    background: var(--pico-background-color);
                    border-radius: 1rem;
                    padding: 2rem;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                }}
                .logo {{
                    font-family: 'Orbitron', sans-serif;
                    font-size: 2.5rem;
                    font-weight: 700;
                    text-align: center;
                    margin-bottom: 0.5rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                h1 {{
                    text-align: center;
                    margin-bottom: 1.5rem;
                    font-size: 1.5rem;
                }}
                .steam-btn {{
                    background-color: #171a21;
                    width: 100%;
                    padding: 1rem;
                    border: none;
                    border-radius: 0.5rem;
                    font-size: 1rem;
                    cursor: pointer;
                    text-decoration: none;
                    display: block;
                    text-align: center;
                    transition: background-color 0.3s;
                }}
                .steam-btn:hover {{
                    background-color: #2a475e;
                }}
                .friends-list {{
                    max-height: 400px;
                    position:relative;
                    overflow-y: auto;
                    margin: 0;
                }}
                .friend-item {{
                    display: flex;
                    align-items: center;
                    padding: 1rem;
                    background: var(--pico-card-background-color);
                    border-radius: 0.5rem;
                    margin-bottom: 0.75rem;
                    cursor: pointer;
                    transition: all 0.3s;
                    border: 2px solid transparent;
                }}
                .friend-item:hover {{
                    background: var(--pico-secondary-background);
                }}
                .friend-item.selected {{
                    border-color: var(--pico-primary);
                    background: var(--pico-primary-background);
                }}
                .friend-avatar {{
                    width: 48px;
                    height: 48px;
                    border-radius: 0.5rem;
                    margin-right: 1rem;
                }}
                .friend-info {{
                    flex: 1;
                }}
                .friend-name {{
                    font-weight: bold;
                    margin-bottom: 0.25rem;
                }}
                .friend-status {{
                    font-size: 0.875rem;
                    color: var(--pico-muted-color);
                }}
                .checkbox-icon {{
                    width: 24px;
                    height: 24px;
                    border: 2px solid var(--pico-muted-color);
                    border-radius: 0.25rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s;
                }}
                .friend-item.selected .checkbox-icon {{
                    background: var(--pico-primary);
                    border-color: var(--pico-primary);
                }}
                .next-btn {{
                    width: 100%;
                    margin-top: 1rem;
                }}
                .selected-count {{
                    text-align: center;
                    color: var(--pico-muted-color);
                    margin-top: 1rem;
                }}
                .search-bar {{
                    margin-bottom: 1rem;
                    width: 100%;
                    position: relative;
                }}
                .search-bar input {{
                    margin-bottom: 0;
                    padding-right: 3rem;
                }}
                .clear-search-btn {{
                    position: absolute;
                    right: 0.5rem;
                    top: 50%;
                    transform: translateY(-50%);
                    background: transparent;
                    border: none;
                    color: var(--pico-muted-color);
                    cursor: pointer;
                    padding: 0.5rem;
                    font-size: 1.2rem;
                    line-height: 1;
                    transition: color 0.3s;
                }}
                .clear-search-btn:hover {{
                    color: var(--pico-color);
                }}
                .loading {{
                    text-align: center;
                    padding: 2rem;
                }}
                .spinner {{
                    display: inline-block;
                    width: 40px;
                    height: 40px;
                    border: 4px solid rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    border-top-color: var(--pico-primary);
                    animation: spin 1s ease-in-out infinite;
                }}
                @keyframes spin {{
                    to {{ transform: rotate(360deg); }}
                }}
                .htmx-request .htmx-indicator {{
                    display: inline-block;
                }}
                .htmx-indicator {{
                    display: none;
                }}
                .game-item {{
                    transition: all 0.3s;
                    cursor: pointer;
                }}
                .game-item:hover {{
                    background: #2c313c;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }}
                .owner-names {{
                    opacity: 0;
                    max-height: 0;
                    overflow: hidden;
                    transition: all 0.3s ease-in-out;
                }}
                .game-item:hover .owner-names {{
                    opacity: 1 !important;
                    max-height: 100px !important;
                }}
            """
            ],
        ],
        h.body[
            h.div(".container")[
                h.main(id="main-content")[
                    h.div(".logo")["WCWP"],
                    h.h1["🎮 What Can We Play"],
                    content,
                ]
            ]
        ],
    ]


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


def loading_spinner(message="Loading..."):
    """Loading spinner component"""
    return h.div(".loading")[
        h.div(".spinner"),
        h.p(style="margin-top: 1rem;")[message],
    ]


def friends_list_page(friends):
    friend_items = [
        h.div(
            ".friend-item",
            **{
                ":class": f"{{'selected': selectedFriends.includes('{friend['player']['steamid']}')}}"
            },
            **{
                "x-show": f"'{friend['player']['personaname'].lower()}'.includes(searchQuery.toLowerCase())"
            },
            **{
                "@click": f"""
                (() => {{
                    const steamid = '{friend["player"]["steamid"]}';
                    const index = selectedFriends.indexOf(steamid);
                    const checkbox = document.getElementById('checkbox-{friend["player"]["steamid"]}');
                    if (index === -1) {{
                        selectedFriends.push(steamid);
                        if (checkbox) checkbox.checked = true;
                    }} else {{
                        selectedFriends.splice(index, 1);
                        if (checkbox) checkbox.checked = false;
                    }}
                }})()
            """
            },
        )[
            h.input(
                type="checkbox",
                name="selected_friends",
                id=f"checkbox-{friend['player']['steamid']}",
                value=friend["player"]["steamid"],
                style="position: absolute; opacity: 0; width: 0; height: 0;",
            ),
            h.img(
                ".friend-avatar",
                src=friend["player"]["avatar"],
                alt=friend["player"]["personaname"],
            ),
            h.div(".friend-info")[
                h.div(".friend-name")[friend["player"]["personaname"]],
            ],
            h.div(".checkbox-icon")[
                h.span(
                    **{
                        "x-show": f"selectedFriends.includes('{friend['player']['steamid']}')"
                    }
                )["✓"]
            ],
        ]
        for friend in sorted(friends, key=lambda x: x["player"]["personaname"])
    ]

    content = h.div[
        h.div(
            **{
                "x-data": "{ selectedFriends: [], searchQuery: '', get selectedCount() { return this.selectedFriends.length; } }"
            }
        )[
            h.h3["Select Friends to Play With"],
            h.p(style="color: var(--pico-muted-color); margin-bottom: 1rem;")[
                "Choose the friends you want to find common games with"
            ],
            h.div(".search-bar")[
                h.input(
                    type="text",
                    placeholder="Search friends...",
                    **{"x-model": "searchQuery"},
                ),
                h.button(
                    ".clear-search-btn",
                    type="button",
                    **{"@click": "searchQuery = ''", "x-show": "searchQuery !== ''"},
                )["×"],
            ],
            h.form(
                id="friends-form",
                method="POST",
                action=url_for("select_games"),
                **{
                    "hx-post": url_for("select_games"),
                    "hx-swap": "innerHTML",
                    "hx-target": "#main-content",
                    "hx-indicator": "#submit-spinner",
                },
            )[
                h.div(".friends-list")[friend_items],
                h.div(".selected-count")[
                    h.span(
                        **{
                            "x-text": "selectedCount === 0 ? 'No friends selected' : selectedCount === 1 ? '1 friend selected' : selectedCount + ' friends selected'"
                        }
                    )
                ],
                h.button(
                    ".next-btn",
                    type="submit",
                    **{":disabled": "selectedCount === 0"},
                )[
                    h.span["Next: Find Common Games →"],
                    h.span(
                        ".htmx-indicator",
                        id="submit-spinner",
                        style="margin-left: 0.5rem;",
                    )[h.div(".spinner", style="width: 20px; height: 20px;")],
                ],
            ],
        ],
        h.a(
            ".secondary",
            href=url_for("logout"),
            role="button",
            style="margin-top: 1rem; width: 100%;",
        )["Logout"],
    ]

    return content


def games_page(friend_steam_ids: list[str]) -> h.Element:
    friend_ids_param = ",".join(friend_steam_ids)

    content = h.div("#content-area")[
        h.div(
            id="games-list",
            **{
                "hx-get": url_for("load_common_games", friend_ids=friend_ids_param),
                "hx-trigger": "load",
                "hx-swap": "innerHTML",
            },
        )[loading_spinner("Finding common games...")],
        h.a(
            href=url_for("index"),
            role="button",
            style="margin-top: 2rem; width: 100%;",
            **{
                "hx-get": url_for("load_friends"),
                "hx-target": "#main-content",
            },
        )["← Back to Friends"],
    ]
    return content


def common_games_list(games_with_counts, total_users):
    """Display the list of games ranked by how many people own them"""
    if not games_with_counts:
        return h.div(style="text-align: center; padding: 2rem;")[
            h.p["No common games found. 😢"],
            h.p(style="color: var(--pico-muted-color); margin-top: 0.5rem;")[
                "Try selecting different friends!"
            ],
        ]

    game_items = [
        h.div(
            ".game-item",
            style="display: flex; align-items: center; padding: 1rem; background: var(--pico-card-background-color); border-radius: 0.5rem; margin-bottom: 0.75rem; transition: all 0.3s; cursor: pointer;",
        )[
            (
                h.img(
                    src=f"https://media.steampowered.com/steamcommunity/public/images/apps/{game.get('appid')}/{game.get('img_icon_url')}.jpg",
                    alt=game.get("name", "Unknown"),
                    style="width: 48px; height: 48px; border-radius: 0.25rem; margin-right: 1rem; flex-shrink: 0;",
                )
                if game.get("img_icon_url")
                else h.div(
                    style="width: 48px; height: 48px; border-radius: 0.25rem; margin-right: 1rem; background: var(--pico-muted-color); flex-shrink: 0;"
                )
            ),
            h.div(style="flex: 1; min-width: 0;")[
                h.div(style="font-weight: bold; margin-bottom: 0.25rem;")[
                    game.get("name", "Unknown Game"),
                ],
                h.div(
                    style="font-size: 0.875rem; color: var(--pico-muted-color); margin-bottom: 0.5rem;"
                )[f"{game['owner_count']}/{total_users} people own this"],
                h.div(
                    ".owner-names",
                    style="display: flex; gap: 0.375rem; flex-wrap: wrap; opacity: 0; max-height: 0; overflow: hidden; transition: all 0.3s ease-in-out;",
                )[
                    (
                        h.span(
                            style="font-size: 0.7rem; padding: 0.25rem 0.625rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%); border: 1px solid rgba(102, 126, 234, 0.5); border-radius: 1rem; color: rgba(255, 255, 255, 0.9); white-space: nowrap;"
                        )[name]
                        for name in game["owner_names"]
                    )
                ],
            ],
            h.div(
                style=f"""
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    background: {"linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if game["owner_count"] == total_users else "rgba(255, 255, 255, 0.1)"};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 0.875rem;
                    color: {"white" if game["owner_count"] == total_users else "rgba(255, 255, 255, 0.6)"};
                    flex-shrink: 0;
                """
            )[f"{int(game['owner_count'] / total_users * 100)}%"],
        ]
        for game in games_with_counts
    ]

    return h.div[
        h.h3(style="margin-top: 2rem;")[
            f"Found {len(games_with_counts)} game{'' if len(games_with_counts) == 1 else 's'}! 🎮"
        ],
        h.p(style="color: var(--pico-muted-color); margin-bottom: 1rem;")[
            "Games ranked by how many people own them (hover to see who)"
        ],
        h.div(style="max-height: 400px; overflow-y: auto; margin-top: 1rem;")[
            game_items
        ],
    ]


def private_profile_message() -> h.Element:
    """Message shown when user's profile is private"""
    return h.div(style="text-align: center; padding: 3rem 2rem;")[
        h.div(style="font-size: 4rem; margin-bottom: 1rem;")["🔒"],
        h.h2(style="margin-bottom: 1rem;")["Your Profile is Private"],
        h.p(
            style="color: var(--pico-muted-color); margin-bottom: 2rem; max-width: 500px; margin-left: auto; margin-right: auto;"
        )[
            "To use this app, you need to set your Steam profile to public so we can see your friends list and games."
        ],
        h.div(
            style="background: var(--pico-card-background-color); padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 2rem;"
        )[
            h.h3(style="font-size: 1rem; margin-bottom: 1rem;")[
                "How to make your profile public:"
            ],
            h.ol(
                style="text-align: left; padding-left: 1.5rem; color: var(--pico-muted-color);"
            )[
                h.li(style="margin-bottom: 0.5rem;")[
                    "Go to your ",
                    h.a(
                        href="https://steamcommunity.com/my/edit/settings",
                        target="_blank",
                        style="color: var(--pico-primary);",
                    )["Steam Privacy Settings"],
                ],
                h.li(style="margin-bottom: 0.5rem;")[
                    'Set "My profile" to ', h.strong["Public"]
                ],
                h.li(style="margin-bottom: 0.5rem;")[
                    'Set "Game details" to ', h.strong["Public"]
                ],
                h.li(style="margin-bottom: 0.5rem;")[
                    'Set "Friends list" to ', h.strong["Public"]
                ],
                h.li["Click 'Save' and reload this page"],
            ],
        ],
        h.button(
            onclick="window.location.reload();",
            style="margin-top: 1rem; margin-right: 1rem;",
        )["Try again"],
        h.a(
            ".secondary",
            href=url_for("logout"),
            role="button",
            style="margin-top: 1rem;",
        )["Logout"],
    ]
