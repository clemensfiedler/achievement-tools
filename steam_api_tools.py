import requests
from typing import List, Dict, Union, Tuple
from lxml import html
import tomllib
import polars as pl
import csv
import os


def get_api_key():
    with open("api_settings.toml", "rb") as file:
        api_config = tomllib.load(file)

    return api_config["steam_api"]["api_key"]


def fetch_app_list() -> List[Dict[str, Union[int, str]]]:
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


class appid_db:
    """Get a list of appids to with a matching game name.

    Example:
    ```
    db = appid_db()
    db.find_game("civ")
    ```
    """

    def __init__(self, rebuild: bool = False, folder: str = "temp"):
        self.appid_file = f"{folder}/app_list.csv"

        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        if not os.path.exists(self.appid_file) or rebuild:
            self.update_db()

        appid_list = self._read_appid_file()

        self.appid_to_game = self._prepare_appid_lookup(appid_list)
        self.game_to_appid = {v.lower(): (v, k) for k, v in self.appid_to_game.items()}

    def _read_appid_file(self) -> List[Tuple[str, str]]:
        with open(self.appid_file, mode="r") as f:
            csv_reader = csv.reader(f)
            col_names = next(csv_reader)
            assert col_names == [
                "appid",
                "name",
            ], f"Wrong column names. Expected appid and names, got {col_names}"

            return list(csv_reader)

    def _prepare_appid_lookup(
        self, appid_list: List[Tuple[str, str]]
    ) -> Dict[int, str]:
        appid_to_game = {}
        for row in appid_list:
            appid = int(row[0])
            game_name = row[1]

            appid_to_game[appid] = game_name

        return appid_to_game

    def _search_db(self, query):
        """Search for a specific game."""
        query = query.lower()
        results = []

        for k, entry in self.game_to_appid.items():
            if k.startswith(query):
                results.append(entry)

        return results

    def find_game(self, query):
        results = self._search_db(query)
        if len(results) == 0:
            print(f"No results for '{query}'")
            return

        results_sorted = sorted(results, key=lambda x: x[0])

        max_chars = 60
        longest_title = max([len(r[0]) for r in results_sorted])
        longest_title = min(longest_title, max_chars)

        results_padded = [
            f"{r[0][:max_chars].ljust(longest_title)}   {r[1]}".replace("\t", " ")
            for r in results_sorted
        ]

        title = "Game".center(longest_title) + "   " + " AppID"
        print(title, *results_padded, sep="\n")

    def update_db(self):
        app_list = fetch_app_list()

        df_app_list = pl.DataFrame(app_list)
        df_app_list.filter(pl.col("name") != "").write_csv(self.appid_file)


def format_achievement_list(achievement_list):
    """Format a game's list of achievements nicely."""
    out_string = "\n".join(
        [f"- {ac['description']} ({ac['title']})" for ac in achievement_list]
    )
    print(out_string)
