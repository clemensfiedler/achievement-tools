"""Collection of tools to analyse steam achievements."""

__author__ = "Clemens Fiedler"
__email__ = "clemens.mb.fiedler@gmail.com"

# imports
import requests
from lxml import html

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