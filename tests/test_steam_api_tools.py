import steam_api_tools
import os


def test_fetch_app_list():
    app_list = steam_api_tools.fetch_app_list()
    assert len(app_list) > 200_000, "The app list is too short."

    expected_keys = ["appid", "name"]
    for entry in app_list:
        assert [
            k for k in expected_keys if k not in entry.keys()
        ] == [], "Some entries are missing keys."

    set(["app_id", "name"]) - set(app_list[0].keys())

    game_sample = [
        {"appid": 892970, "name": "Valheim"},
        {"appid": 289070, "name": "Sid Meier's Civilization VI"},
        {"appid": 38400, "name": "Fallout"},
        {"appid": 1601580, "name": "Frostpunk 2"},
    ]

    for game in game_sample:
        assert game in app_list, f"{game} not found in app list."


def test_get_achievement_stats():
    games_with_achievements = [289070, 427520]
    games_without_achievements = [892970, 38400]

    for game in games_without_achievements:
        data = steam_api_tools.get_achievement_stats(game)
        assert (
            data == []
        ), f"Expected an empty list for game appid {game}, but got {data}"

    for game in games_with_achievements:
        data = steam_api_tools.get_achievement_stats(game)
        assert (
            isinstance(data, list) and len(data) > 0
        ), f"Expected non-empty list for game appid {game}, but got {data}"
        for achievement in data:
            percentage = achievement.get("percentage", None)
            assert (
                percentage is not None
            ), f"Missing 'percentage' key in achievement data for game appid {game}"
            assert (
                0 <= percentage <= 1
            ), f"Expected percentage between 0 and 1 for game appid {game}, but got {percentage}"


def test_appid_db():
    folder = "temp"
    os.makedirs(folder, exist_ok=True)

    db = steam_api_tools.appid_db(folder="temp", rebuild=True)
    assert len(db._search_db("civ")) > 10, "civ not found!"
    random_chars = "adsjgutynmvkdslf"
    assert len(db._search_db(random_chars)) == 0, f"{random_chars} was found!"
