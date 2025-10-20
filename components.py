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
                    overflow-y: auto;
                    margin: 1.5rem 0;
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


def _friend_status_emoji(state):
    if state == 1:
        return "🟢 Online"
    elif state == 3:
        return "🟠 Away"
    else:
        return "⚫ Offline"


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
                ":class": f"{{'selected': selectedFriends.includes('{friend["player"]['steamid']}')}}"
            },
            **{
                "@click": f"""
                (() => {{
                    const steamid = '{friend["player"]['steamid']}';
                    const index = selectedFriends.indexOf(steamid);
                    const checkbox = $el.querySelector('input[value="' + steamid + '"]');
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
            h.img(
                ".friend-avatar",
                src=friend["player"]["avatar"],
                alt=friend["player"]["personaname"],
            ),
            h.div(".friend-info")[
                h.div(".friend-name")[friend["player"]["personaname"]],
                h.div(".friend-status")[
                    _friend_status_emoji(friend.get("personastate", 0))
                ],
            ],
            h.div(".checkbox-icon")[
                h.span(
                    **{
                        "x-show": f"selectedFriends.includes('{friend["player"]['steamid']}')"
                    }
                )["✓"]
            ],
            h.input_(
                type="checkbox",
                name="selected_friends",
                value=friend["player"]["steamid"],
                style="display: none;",
            ),
        ]
        for friend in friends
    ]

    content = h.div[
        h.div(
            **{
                "x-data": "{ selectedFriends: [], get selectedCount() { return this.selectedFriends.length; } }"
            }
        )[
            h.h3["Select Friends to Play With"],
            h.p(style="color: var(--pico-muted-color); margin-bottom: 1rem;")[
                "Choose the friends you want to find common games with"
            ],
            h.form(
                method="POST",
                action=url_for("select_games"),
                **{
                    "hx-post": url_for("select_games"),
                    "hx-target": "#content-area",
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


def friends_list_wrapper(friends):
    """Wrapper that returns full page layout"""
    return base_layout(friends_list_page(friends))


def games_page(count):
    content = h.div[
        h.p(style="text-align: center;")[f"You selected {count} friend(s)!"],
        h.p(
            style="text-align: center; color: var(--pico-muted-color); margin-top: 1rem;"
        )["This is where we'll show the games you all have in common."],
        h.a(
            href=url_for("index"),
            role="button",
            style="margin-top: 2rem; width: 100%;",
            **{
                "hx-get": url_for("load_friends"),
                "hx-target": "#content-area",
            },
        )["← Back to Friends"],
    ]
    return content
