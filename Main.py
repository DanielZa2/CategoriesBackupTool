import json
import re
import os
import html

from urllib import request as urlrequest

# TODO Change default path to the eqvivalent of C:\Program Files (x86)\Steam\userdata\<ID>\7\remote
# TODO detect path for sharedconfig.vdf


DefaultPath = "Test\\sharedconfig.vdf.txt"

WRITE_JSON_FILE = False
WRITE_FAILED_NAME_FETCH_TO_FILE = False


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
        self.name = ""

    def __repr__(self):
        if self.name is "":
            return "<Game: " + self.id + ">"
        else:
            return "<Game: " + self.name + ">"


def main(path=DefaultPath):
    apps = apps_from_file(path)
    apps = {appID: apps[appID] for appID in apps if ("tags" in apps[appID]) and isinstance(apps[appID]["tags"], dict)}  # remove all the games without categories
    tags = tag_obj_from_str(apps)

    for tag in tags:
        print(tag.str_games())


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


def fetch_game_data(app_id):
    req = urlrequest.Request("http://store.steampowered.com/api/appdetails/?appids=" + app_id)
    try:
        json_bytes = urlrequest.urlopen(req).read()
        json_text = html.unescape(json_bytes.decode("utf-8"))
        game_info = json.loads(json_text)
        name = game_info[app_id]["data"]

        return name


    except Exception as e:
        if WRITE_FAILED_NAME_FETCH_TO_FILE:
            print(str(e), file=sys.stderr)
            with open("Log/fetch_error.html.txt", 'w') as out:
                out.write(str(e) + "\n\n\n")
                out.write(game_info)
        return None  # //Can't fetch the name



def log(msg, prefix="Error- ", filename=None):
    if not os.path.exists("Log"):
        os.mkdir("Log")

    if filename is None:
        import datetime
        filename = prefix + str(datetime.datetime.now().isoformat())

    with open("Log/"+filename, "w") as file:
        file.write(msg)


main()
