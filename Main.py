import json
import re
import os
import html

from urllib import request as urlrequest
from urllib import error as urlerror

# TODO Change default path to the eqvivalent of C:\Program Files (x86)\Steam\userdata\<ID>\7\remote
# TODO detect path for sharedconfig.vdf
# TODO GUI. 3 Buttons. Import sharedconfig.vdf, Export sharedconfig.vdf, Export readable format.
# TODO remove stupid characters from names. Characters like trademark and copyright and etc
# TODO change to using http://api.steampowered.com/ISteamApps/GetAppList/v0001/
# TDOD Readme.md


DefaultPath = "Test\\sharedconfig.vdf.txt"

WRITE_JSON_FILE = False
WRITE_FAILED_NAME_FETCH_TO_FILE = True


class Tag:
    def __init__(self, name):
        self.name = name
        self.games = []

    def add_game(self, game):
        self.games.append(game)

    def __repr__(self):
        return "<Tag: " + self.name + ">"

    def str_games(self):
        ret = repr(self)
        for game in self.games:
            ret += "\n\t"
            ret += repr(game)
        return ret


class Game:
    def __init__(self, index):
        self.id = index
        self.data = None

    def __repr__(self):
        if self.data is None:
            return "<Game: " + self.id + ">"
        else:
            return "<Game: " + self.data["name"] + ">"

    @staticmethod
    def fetch_game_data_static(app_id):
        req = urlrequest.Request("http://store.steampowered.com/api/appdetails/?appids=" + app_id)

        try:
            json_bytes = urlrequest.urlopen(req).read()
        except urlerror.HTTPError as e:
            if WRITE_FAILED_NAME_FETCH_TO_FILE:
                log(str(e) + "\n\n\n" + str(req.full_url), "HTTPError_")
            return None

        json_text = json_bytes.decode("utf-8")
        try:
            game_info = json.loads(json_text)

            if not game_info[app_id]["success"]:
                return None

            data = game_info[app_id]["data"]
            return data
            # unescaped_data = {}
            # for k, v in data.items(): # TODO fix this. unescape HTML
            #    unescaped_data[k] = html.unescape(v) if v is isinstance(v, str) else v
            # return unescaped_data


        except (json.decoder.JSONDecodeError, KeyError) as e:
            if WRITE_FAILED_NAME_FETCH_TO_FILE:
                log(str(e) + "\n\n\n" + json_text, "ParseError_")
            return None

    def fetch_game_data(self):
        if self.data is None and self.id.isdigit():
            self.data = self.fetch_game_data_static(self.id)
            print((str(self.id) + ": " + self.data["name"]) if self.data is not None else (str(self.id) + ": ???"))


def test():
    tags = tag_obj_from_path(DefaultPath)
    games = [game for tag in tags for game in tag.games]

    for game in games:
        game.fetch_game_data()

    for tag in tags:
        print(tag.str_games())


def tag_obj_from_path(path):
    apps = apps_from_file(path)
    apps = {appID: apps[appID] for appID in apps if ("tags" in apps[appID]) and isinstance(apps[appID]["tags"], dict)}  # remove all the games without categories
    tags = tag_obj_from_str(apps)

    return tags


def tag_obj_from_str(apps):
    tag_names = sorted(set([tag_name for app in apps.values() for tag_name in app["tags"].values()]))  # get all the possible tags from the different apps
    tags = [Tag(tag_name) for tag_name in tag_names]
    games = [Game(game_id) for game_id in apps]
    for tag in tags:
        for game in games:
            if tag.name in apps[game.id]["tags"].values():
                tag.add_game(game)
    return tags


def apps_from_file(path):
    with open(path) as file:
        file_string = file.read()
        file_string = json_from_valve(file_string)
        if WRITE_JSON_FILE:
            with open(path + ".json", "w") as out:
                out.write(file_string)

        parsed = json.loads(file_string)
        return parsed["UserRoamingConfigStore"]["Software"]["Valve"]["Steam"]["apps"]


def json_from_valve(file_string):
    file_string = "{\n" + file_string + "}"
    # "txt" -> "txt":
    file_string = re.sub(r"(\n[^\n\"]*\"[^\n\"]*\")\n", r"\1:\n", file_string)
    # "txt" "bob" -> "txt": "bob",
    file_string = re.sub(r"([^\"\n]*\"[^\"\n]*\")([^\"\n]*)([^\"\n]*\"[^\"\n]*\")", r"\1:\2\3,", file_string)
    # } -> },
    file_string = file_string.replace("}", "},")
    # },} -> }}
    file_string = re.sub(r",([\t|\n]*)\}", r"\1}", file_string)[0:-1]

    return file_string


def log(msg, prefix="Error_", filename=None):
    if not os.path.exists("Log"):
        os.mkdir("Log")

    if filename is None:
        import datetime
        filename = prefix + str(datetime.datetime.now().strftime("%Y-%m-%d;%H-%M-%S;%f")) + ".txt"

    with open("Log/" + filename, "w") as file:
        file.write(msg)


test()
