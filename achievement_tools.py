"""Collection of tools to analyse steam achievements."""

__author__ = "Clemens Fiedler"
__email__ = "clemens.mb.fiedler@gmail.com"

# imports
import requests
from lxml import html
import json
import os

from datetime import datetime as dt

# internal imports
from app_id_db import appid_db


def get_appid(game_name):
    """Get the appid of a game.

    args
    ----
    query: name of game
    """
    # initialize database
    db = appid_db()

    # search for game
    res = db.search_db(game_name)

    # if no results return None
    if len(res) == 0:
        print(f"No results for '{query}'")
        return None

    # if multiple results print them and return None
    if len(res) > 1:
        print(f"Multiple results for '{query}':")
        for r in res:
            print(f"- {r['name']}")
        return None

    # if exactly one result return appid
    return res[0]['appid']


get_appid("Baldur")

def get_achievement_stats(appid):
    """Download global achievement statistics for a given game.

    args
    ----
    appid: steam id of game
    """
    # if appid is None return empty list instead
    # used for compatibility reasons
    if not appid:
        print("No appid supplied.")
        return []

    # download html containing achievement statistics
    link_global = "https://steamcommunity.com/stats/{}/achievements/"
    r = requests.get(link_global.format(appid))
    doc = html.fromstring(r.text)
    achievements_raw = doc.xpath("//div[@class='achieveRow ']")

    # initialize achievement list
    achievement_list = []

    for ac in achievements_raw:
        # extract title, description and percentage
        title = ac.xpath('div/div/h3')[0].text
        description = ac.xpath('div/div/h5')[0].text
        percentage = float(ac.xpath('div/div[2]')[0].text.strip('%'))/100

        # append as dictionary to list
        achievement_list.append(
            {
                'title': title,
                'description': description,
                'percentage': percentage,
                }
        )
    return achievement_list


def format_achievement_list(achievement_list):
    """Format a game's list of achievements nicely."""
    out_string = '\n'.join(
        [
            f"- {ac['description']} ({ac['title']})"
                for ac in achievement_list
            ]
        )
    print(out_string)
