import json
import re
import os
import datetime

from urllib import request as urlrequest
from urllib import error as urlerror

# TODO Change default path to the eqvivalent of C:\Program Files (x86)\Steam\userdata\<ID>\7\remote
# TODO detect path for sharedconfig.vdf
# TODO GUI. 3 Buttons. Import sharedconfig.vdf, Export sharedconfig.vdf, Export readable format.
# TODO Readme.md




OUTPUT__SHAREDCONFIG_VDF_JSON = False
LOG_ERROR___FETCH_APPLIST = True


class Tag:
    def __init__(self, name):
        self.name = name
        self.games = []

    def __repr__(self):
        return "<Tag: " + self.name + ">"

    def __str__(self):
        return "Tag: " + self.name

    def game_string(self):
        ret = str(self)
        for game in self.games:
            ret += "\n\t"
            ret += str(game)
        return ret


class Tags:
    def __init__(self):
        self.lst = []

    def name_games(self, applist):
        gamelist = [game for tag in self.lst for game in tag.games]
        applist.name_games(gamelist)

    def games_string(self, filter_symbols=False):
        ret = ""
        for tag in self.lst:
            ret += tag.game_string()
            ret += "\n"
        if filter_symbols:
            f = lambda string: string != "©" and string != "™"
            return "".join(filter(f, ret))
        else:
            return ret

    def save_games_string(self, filename=None, filter_symbols=False):
        if filename is None:
            filename = "Steam Categories " + str(datetime.datetime.now().strftime("%Y-%m-%d;%H_%M")) + ".txt"

        with open(filename, "w", encoding='UTF-8') as file:
            file.write(self.games_string(filter_symbols))

    @staticmethod
    def apps_from_file(path):
        with open(path, encoding='UTF-8') as file:
            file_string = file.read()
            file_string = Tags.json_from_valve(file_string)
            if OUTPUT__SHAREDCONFIG_VDF_JSON:
                with open(path + ".json", "w", encoding='UTF-8') as out:
                    out.write(file_string)

            parsed = json.loads(file_string)
            return parsed["UserRoamingConfigStore"]["Software"]["Valve"]["Steam"]["apps"]

    @staticmethod
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

    @staticmethod
    def obj_list_from_path(path):
        apps = Tags.apps_from_file(path)
        apps = {appID: apps[appID] for appID in apps if ("tags" in apps[appID]) and isinstance(apps[appID]["tags"], dict)}  # remove all the games without categories

        return Tags.obj_list_from_str(apps)

    @staticmethod
    def obj_list_from_str(apps):
        tag_names = sorted(set([tag_name for app in apps.values() for tag_name in app["tags"].values()]))  # get all the possible tags from the different apps

        tags = Tags()
        tags.lst = [Tag(tag_name) for tag_name in tag_names]
        games = [Game(game_id) for game_id in apps]

        for tag in tags.lst:
            for game in games:
                if tag.name in apps[game.id]["tags"].values():
                    tag.games.append(game)
        return tags


class Game:
    def __init__(self, index):
        self.id = index
        self.name = None

    def __str__(self):
        if self.name is None:
            return "(AppID: " + self.id + ")"
        else:
            return self.name

    def __repr__(self):
        if self.name is None:
            return "<Game: AppID_" + self.id + ">"
        else:
            return "<Game: " + self.name + ">"

    def get_name(self, applist):
        if self.id.isdigit():
            self.name = applist.id_lookup.get(int(self.id), None)


class AppList:
    def __init__(self, filename="Applist.txt", remove_trademark_symbols=True):
        self.filename = filename
        self.remove_trademark_symbols = remove_trademark_symbols
        self.data = None
        self.id_lookup = None
        # self.name_lookup = None

    @staticmethod
    def fetch_from_net():
        req = urlrequest.Request("http://api.steampowered.com/ISteamApps/GetAppList/v0001/")
        try:
            json_bytes = urlrequest.urlopen(req).read()
        except urlerror.HTTPError as e:
            if LOG_ERROR___FETCH_APPLIST:
                log(str(e) + "\n\n\n" + str(req.full_url), "HTTPError_")
            return None

        return json_bytes.decode("utf-8")

    def fetch_from_disk(self):
        with open(self.filename, encoding='UTF-8') as file:
            return file.read()

    @staticmethod
    def json_to_obj(json_text):
        try:
            game_info = json.loads(json_text)

            data = game_info["applist"]["apps"]["app"]
            return data


        except (json.decoder.JSONDecodeError, KeyError) as e:
            if LOG_ERROR___FETCH_APPLIST:
                log(str(e) + "\n\n\n" + json_text, "ParseError_")
            return None

    def write_apps_to_disk(self, data):
        with open(self.filename, "w", encoding='UTF-8') as file:
            file.write(data)

    def name_games(self, gamelist):
        for game in gamelist:
            game.get_name(self)

    def fetch(self, fetch_from_net=False):
        if self.data is not None:
            return self

        if not fetch_from_net and not os.path.exists(self.filename):
            print("Can't locate file")
            return None

        if not fetch_from_net:  # and os.path.exists(self.filename)
            self.data = AppList.json_to_obj(self.fetch_from_disk())

        if fetch_from_net or not os.path.exists(self.filename):
            json_text = AppList.fetch_from_net()
            self.data = AppList.json_to_obj(json_text)
            self.write_apps_to_disk(json_text)

        self.id_lookup = {pair["appid"]: pair["name"] for pair in self.data}
        # self.name_lookup = {pair["name"]: pair["appid"] for pair in self.data}

        return self


def log(msg, prefix="Error_", filename=None):
    if not os.path.exists("Log"):
        os.mkdir("Log")

    if filename is None:
        filename = prefix + str(datetime.datetime.now().strftime("%Y-%m-%d;%H_%M_%S;%f")) + ".txt"

    with open("Log/" + filename, "w", encoding='UTF-8') as file:
        file.write(msg)


def main():
    default_path = "Test\\sharedconfig.vdf.txt"

    applist = AppList().fetch()
    tags = Tags.obj_list_from_path(default_path)
    tags.name_games(applist)

    print(tags.games_string(True))
    tags.save_games_string(filter_symbols=True)


main()
