"""Get a list of app_ids to search for names.

Example:
db = appid_db()
res = db.search_db('Humankind')
db.format_list(res)
"""

FOLDER_TEMP = "temp"
LINK_API = "http://api.steampowered.com"

# imports
import requests
from lxml import html
import json
import os
from datetime import datetime as dt

class appid_db:

    def __init__(self):
        """Prepare database for search.

        Prepare the database by either loading a previously
        downloaded file or downloading a new one.
        """
        self.app_list_file = '/'.join([FOLDER_TEMP, 'applist.json'])
        self.link = '/'.join([
            LINK_API,
            "ISteamApps/GetAppList/v0002",
            "?format=json"])

        if not os.path.exists(self.app_list_file):
            self.update_db()

        with open(self.app_list_file, 'r') as fp:
            self.app_list = json.load(fp)

        print(f"Loaded appid list downloaded {self.app_list['time']}")


    def update_db(self):
        # download app list and convert to json
        r = requests.get(self.link)
        app_list = r.json()

        # attach date of download
        app_list['time'] = dt.utcnow().isoformat()

        # save to disk
        with open(self.app_list_file, 'w') as fp:
            json.dump(app_list, fp)


    def search_db(self, query):
        """Search for a specific game."""
        query = query.lower()
        results = []

        for entry in self.app_list['applist']['apps']:
            if entry['name'].lower().startswith(query):
                results.append(entry)

        return results

    def format_list(self, app_list):
        """Formats an app list nicely."""
        table = '\n'.join([
            " appid        name",
            '\n'.join(["{appid}: {name}".format(**r) for r in res])
            ])
        print(table)



