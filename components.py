import htpy as h
from flask import url_for


def base_layout(content, container_width="800px"):
    container_class = (
        "container" if container_width == "800px" else "container container--narrow"
    )

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
                href="https://fonts.googleapis.com/css2?family=Outfit:wght@700;800&family=Inter:wght@600;700;800&display=swap",
                rel="stylesheet",
            ),
            h.link(rel="stylesheet", href=url_for("static", filename="styles.css")),
            h.script(
                defer=True,
                src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js",
            ),
            h.script(src="https://unpkg.com/htmx.org@2.0.3"),
        ],
        h.body[
            h.div(class_=container_class)[
                h.main(id="main-content")[
                    h.div(".header-container")[
                        h.div(".logo")["WCWP"],
                        h.div(".slogan")["what can we play"],
                    ],
                    content,
                ]
            ]
        ],
    ]


def login_page():
    return base_layout(
        h.div[
            h.p(".intro-text")[
                "Sign in with your Steam account to find games you can play with your friends."
            ],
            h.a(
                ".steam-btn",
                href=url_for("login"),
                **{
                    "onmousemove": """
                        const rect = this.getBoundingClientRect();
                        const x = ((event.clientX - rect.left) / rect.width) * 100;
                        const y = ((event.clientY - rect.top) / rect.height) * 100;
                        this.style.setProperty('--mouse-x', x + '%');
                        this.style.setProperty('--mouse-y', y + '%');
                    """,
                    "onmouseleave": """
                        this.style.setProperty('--mouse-x', '50%');
                        this.style.setProperty('--mouse-y', '50%');
                    """,
                },
            )[
                h.svg(
                    ".steam-icon",
                    xmlns="http://www.w3.org/2000/svg",
                    viewBox="0 0 24 24",
                    fill="currentColor",
                )[
                    h.path(
                        d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"
                    )
                ],
                h.span["Sign in through Steam"],
            ],
        ],
        container_width="500px",
    )


def loading_spinner(message="Loading..."):
    return h.div(".loading")[
        h.div(".spinner"),
        h.p(".loading-message")[message],
    ]


def friends_list_page(friends, user_name=None):
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
                ".hidden-checkbox",
                type="checkbox",
                name="selected_friends",
                id=f"checkbox-{friend['player']['steamid']}",
                value=friend["player"]["steamid"],
            ),
            h.img(
                ".friend-avatar",
                src=friend["player"]["avatar"],
                alt=friend["player"]["personaname"],
            ),
            h.div(".friend-info")[
                h.div(".friend-name")[friend["player"]["personaname"]],
            ],
        ]
        for friend in sorted(friends, key=lambda x: x["player"]["personaname"])
    ]

    content = h.div[
        h.div(
            **{
                "x-data": """{
                    selectedFriends: [],
                    searchQuery: '',
                    groups: JSON.parse(localStorage.getItem('friendGroups') || '[]'),
                    showSaveForm: false,
                    newGroupName: '',
                    selectedGroupIndex: '',
                    loadedGroupFriends: [],
                    get selectedCount() { return this.selectedFriends.length; },
                    get hasChangesFromGroup() {
                        if (this.selectedGroupIndex === '' || this.loadedGroupFriends.length === 0) return true;
                        if (this.selectedFriends.length !== this.loadedGroupFriends.length) return true;
                        const sortedSelected = [...this.selectedFriends].sort();
                        const sortedLoaded = [...this.loadedGroupFriends].sort();
                        return !sortedSelected.every((id, i) => id === sortedLoaded[i]);
                    },
                    saveGroup() {
                        if (this.newGroupName.trim() && this.selectedFriends.length > 0) {
                            this.groups.push({
                                name: this.newGroupName.trim(),
                                steamIds: [...this.selectedFriends]
                            });
                            localStorage.setItem('friendGroups', JSON.stringify(this.groups));
                            this.newGroupName = '';
                            this.showSaveForm = false;
                        }
                    },
                    loadGroup() {
                        if (this.selectedGroupIndex !== '') {
                            const steamIds = this.groups[this.selectedGroupIndex].steamIds;
                            this.selectedFriends = [...steamIds];
                            this.loadedGroupFriends = [...steamIds];
                            this.selectedFriends.forEach(steamid => {
                                const checkbox = document.getElementById('checkbox-' + steamid);
                                if (checkbox) checkbox.checked = true;
                            });
                        }
                    },
                    deleteGroup() {
                        if (this.selectedGroupIndex !== '') {
                            this.groups.splice(this.selectedGroupIndex, 1);
                            localStorage.setItem('friendGroups', JSON.stringify(this.groups));
                            this.selectedGroupIndex = '';
                        }
                    }
                }"""
            }
        )[
            h.div(".groups-section", **{"x-show": "groups.length > 0 || showSaveForm"})[
                h.div(".group-select-container", **{"x-show": "groups.length > 0"})[
                    h.select(
                        **{
                            "x-model": "selectedGroupIndex",
                            "@change": "loadGroup()",
                        }
                    )[
                        h.option(value="", selected=True)["Select a group..."],
                        h.template(
                            **{"x-for": "(group, index) in groups", ":key": "index"}
                        )[
                            h.option(
                                **{
                                    ":value": "index",
                                    "x-text": "group.name + ' (' + group.steamIds.length + ' friends)'",
                                }
                            ),
                        ],
                    ],
                    h.button(
                        type="button",
                        **{
                            "@click": "deleteGroup()",
                            ":disabled": "selectedGroupIndex === ''",
                            "title": "Delete selected group",
                        },
                    )["Delete"],
                ],
                # Save group form
                h.div(**{"x-show": "showSaveForm"})[
                    h.div(".save-group-form")[
                        h.input(
                            type="text",
                            placeholder="Group name...",
                            **{
                                "x-model": "newGroupName",
                                "@keyup.enter": "saveGroup()",
                            },
                        ),
                        h.button(
                            type="button",
                            **{"@click": "saveGroup()"},
                        )["Save"],
                        h.button(
                            ".secondary",
                            type="button",
                            **{"@click": "showSaveForm = false; newGroupName = ''"},
                        )["Cancel"],
                    ]
                ],
            ],
            # Search bar with Save button
            h.div(".search-save-container")[
                h.div(".search-bar")[
                    h.input(
                        type="text",
                        placeholder="Search friends...",
                        **{"x-model": "searchQuery"},
                    ),
                    h.button(
                        ".clear-search-btn",
                        type="button",
                        **{
                            "@click": "searchQuery = ''",
                            "x-show": "searchQuery !== ''",
                        },
                    )["×"],
                ],
                # Save group button (shown when friends are selected)
                h.button(
                    ".save-group-btn",
                    type="button",
                    **{
                        "x-show": "selectedCount > 0 && !showSaveForm && hasChangesFromGroup",
                        "@click": "showSaveForm = true",
                    },
                )["Save as group"],
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
                    ),
                    h.span(
                        ".selected-count-link",
                        **{"x-show": "selectedCount > 0"},
                    )[
                        h.a(
                            ".clear-selection-link",
                            href="#",
                            **{
                                "@click.prevent": """selectedFriends = [];
                                document.querySelectorAll('input[name=selected_friends]').forEach(cb => cb.checked = false);"""
                            },
                        )["Clear selection"]
                    ],
                ],
                h.button(
                    ".next-btn",
                    type="submit",
                    **{
                        ":disabled": "selectedCount === 0",
                        "onmousemove": """
                            const rect = this.getBoundingClientRect();
                            const x = ((event.clientX - rect.left) / rect.width) * 100;
                            const y = ((event.clientY - rect.top) / rect.height) * 100;
                            this.style.setProperty('--mouse-x', x + '%');
                            this.style.setProperty('--mouse-y', y + '%');
                        """,
                        "onmouseleave": """
                            this.style.setProperty('--mouse-x', '50%');
                            this.style.setProperty('--mouse-y', '50%');
                        """,
                    },
                )[
                    h.span["Find games →"],
                    h.span(
                        ".htmx-indicator.spinner-container",
                        id="submit-spinner",
                    )[h.div(".spinner.spinner--small")],
                ],
            ],
        ],
        h.a(
            ".secondary.logout-button",
            href=url_for("logout"),
            role="button",
        )[f"Logout{f' ({user_name})' if user_name else ''}"],
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
            ".back-button",
            href=url_for("index"),
            role="button",
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
        return h.div(".no-games-message")[
            h.p["No common games found. 😢"],
            h.p(".no-games-subtitle")["Try selecting different friends!"],
        ]

    game_items = [
        h.div(".game-list")[
            (
                h.img(
                    ".game-icon",
                    src=f"https://media.steampowered.com/steamcommunity/public/images/apps/{game.get('appid')}/{game.get('img_icon_url')}.jpg",
                    alt=game.get("name", "Unknown"),
                )
                if game.get("img_icon_url")
                else h.div(".game-icon.game-icon--placeholder")
            ),
            h.div(".game-info")[
                h.div(".game-name")[game.get("name", "Unknown Game"),],
                h.div(".game-owner-count")[
                    f"{game['owner_count']}/{total_users} people own this"
                ],
                h.div(".owner-badges")[
                    (h.span(".owner-badge")[name] for name in game["owner_names"])
                ],
            ],
            h.div(
                f".game-percentage.game-percentage--{'full' if game['owner_count'] == total_users else 'partial'}"
            )[f"{int(game['owner_count'] / total_users * 100)}%"],
        ]
        for game in games_with_counts
    ]

    return h.div[
        h.h3(".games-header")[
            f"Found {len(games_with_counts)} game{'' if len(games_with_counts) == 1 else 's'}! 🎮"
        ],
        h.p(".games-description")[
            "Games ranked by how many people own them (hover to see who)"
        ],
        h.div(".games-container")[game_items],
    ]


def private_profile_message() -> h.Element:
    """Message shown when user's profile is private"""
    return h.div(".private-profile-container")[
        h.div(".private-profile-icon")["🔒"],
        h.h2(".private-profile-title")["Your Profile is Private"],
        h.p(".private-profile-description")[
            "To use this app, you need to set your Steam profile to public so we can see your friends list and games."
        ],
        h.div(".private-profile-instructions")[
            h.h3["How to make your profile public:"],
            h.ol(".private-profile-list")[
                h.li[
                    "Go to your ",
                    h.a(
                        ".private-profile-link",
                        href="https://steamcommunity.com/my/edit/settings",
                        target="_blank",
                    )["Steam Privacy Settings"],
                ],
                h.li['Set "My profile" to ', h.strong["Public"]],
                h.li['Set "Game details" to ', h.strong["Public"]],
                h.li['Set "Friends list" to ', h.strong["Public"]],
                h.li["Click 'Save' and reload this page"],
            ],
        ],
        h.button(
            ".retry-button",
            onclick="window.location.reload();",
        )["Try again"],
        h.a(
            ".secondary.logout-button--secondary",
            href=url_for("logout"),
            role="button",
        )["Logout"],
    ]
