import requests
from typing import List, Dict, Union
from lxml import html
import tomllib


def get_api_key():
    with open("api_settings.toml", "rb") as file:
        api_config = tomllib.load(file)

    return api_config["steam_api"]["api_key"]


def get_app_list() -> List[Dict[str, Union[int, str]]]:
    """Get a list of name and appid of all games on Steam.

    For details see https://partner.steamgames.com/doc/webapi/ISteamApps

    Returns
    -------
    List of games. Each game is a dictionary with keys "appid" and "name".
    """
    api_link = "http://api.steampowered.com"
    application = "ISteamApps/GetAppList/v2"
    link = "/".join([api_link, application, "?format=json"])
    r = requests.get(link)
    app_list = r.json()["applist"]["apps"]
    return app_list


def get_achievement_stats_html(appid: int):
    """Download global achievement statistics for a given game.

    Parameters
    ----------
    appid: steam id of game
    """

    link_global = "https://steamcommunity.com/stats/{}/achievements/"
    r = requests.get(link_global.format(appid))
    doc = html.fromstring(r.text)
    achievements_raw = doc.xpath("//div[@class='achieveRow ']")

    # initialize achievement list
    achievement_list = []

    for ac in achievements_raw:
        # extract title, description and percentage
        title = ac.xpath("div/div/h3")[0].text
        description = ac.xpath("div/div/h5")[0].text
        percentage = float(ac.xpath("div/div[2]")[0].text.strip("%")) / 100

        # append as dictionary to list
        achievement_list.append(
            {
                "title": title,
                "description": description,
                "percentage": percentage,
            }
        )
    return achievement_list


def get_game_schema(appid: int) -> Dict:
    """Get the schema for all games."""
    api_key = get_api_key()
    api_url = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    url = f"{api_url}?key={api_key}&appid={appid}"
    r = requests.get(url)
    schema = r.json()["game"]

    if len(schema) == 0:
        print(f"WARNING: {appid} has no schema defined")

    return schema


def get_achievement_percentages(appid: int) -> Dict:
    api_url = "/".join(
        [
            "https://api.steampowered.com",
            "ISteamUserStats",
            "GetGlobalAchievementPercentagesForApp/v2",
        ]
    )
    link = f"{api_url}/?gameid={appid}&format=json"
    r = requests.get(link)
    percentages = r.json().get("achievementpercentages", {}).get("achievements", [])

    percentages = {entry["name"]: entry["percent"] / 100 for entry in percentages}
    return percentages


def get_achievement_stats(appid: int):
    """Download global achievement statistics for a given game.

    Parameters
    ----------
    appid: steam id of game
    """
    schema = get_game_schema(appid)
    game_stats_schema = schema.get("availableGameStats", {})
    achievements_raw = game_stats_schema.get("achievements", [])
    percentages = get_achievement_percentages(appid)

    assert len(achievements_raw) == len(percentages), (
        f"Mismatch in number of achievements for appid {appid}: "
        f"{len(achievements_raw)} achievements in schema, "
        f"{len(percentages)} percentages found."
    )

    achievements = []

    for entry in achievements_raw:
        achievement = {
            "title": entry["displayName"],
            "hidden": entry["hidden"],
            "description": entry.get("description", "HIDDEN"),
            "icon": entry["icon"],
            "percentage": percentages[entry["name"]],
        }
        achievements.append(achievement)

    return achievements
