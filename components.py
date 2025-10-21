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
                href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap",
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
                    h.div(".logo")["WCWP"],
                    h.h1["🎮 What Can We Play"],
                    content,
                ]
            ]
        ],
    ]


def login_page():
    return base_layout(
        h.div[
            h.p(".intro-text")[
                "Sign in with your Steam account to find games you can play with your friends"
            ],
            h.a(".steam-btn", href=url_for("login"))["Sign in through Steam"],
        ],
        container_width="500px",
    )


def loading_spinner(message="Loading..."):
    return h.div(".loading")[
        h.div(".spinner"),
        h.p(".loading-message")[message],
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
                    **{":disabled": "selectedCount === 0"},
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
