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
# TODO Readme.md


DefaultPath = "Test\\sharedconfig.vdf.txt"

OUTPUT__SHAREDCONFIG_VDF_JSON = False
LOG_ERROR___FETCH_APPLIST = True


class Tag:
    def __init__(self, name):
        self.name = name
        self.games = []

    def add_game(self, game):
        self.games.append(game)

    def __repr__(self):
        return "<Tag: " + self.name + ">"

    def __str__(self):
        return "Tag: " + self.name

    def str_games(self):
        ret = str(self)
        for game in self.games:
            ret += "\n\t"
            ret += str(game)
        return ret


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
            return "<AppID: " + self.id + ">"
        else:
            return "<Game: " + self.name + ">"

    def fetch_game_data(self, applist):

        if self.id.isdigit():
            self.name = applist.id_lookup.get(int(self.id), None)


class AppList:
    def __init__(self, filename="Applist.txt", on_demend_refetch=True, remove_trademark_symbols=True):
        self.filename = filename
        self.remove_trademark_symbols = remove_trademark_symbols
        self.data = None
        self.id_lookup = None
        # self.name_lookup = None
        self.on_demend_refetch = on_demend_refetch

    @staticmethod
    def filter_trademark(string):
        return string != "©" and string != "™"

    @staticmethod
    def fetch_data_from_net():
        req = urlrequest.Request("http://api.steampowered.com/ISteamApps/GetAppList/v0001/")
        try:
            json_bytes = urlrequest.urlopen(req).read()
        except urlerror.HTTPError as e:
            if LOG_ERROR___FETCH_APPLIST:
                log(str(e) + "\n\n\n" + str(req.full_url), "HTTPError_")
            return None

        return json_bytes.decode("utf-8")

    def fetch_data_from_disk(self):
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

    def write_data_to_disk(self, data):
        with open(self.filename, "w", encoding='UTF-8') as file:
            file.write(data)

    def get_applist(self):
        if self.data is not None:
            return self

        if not self.on_demend_refetch and os.path.exists(self.filename):
            self.data = AppList.json_to_obj(self.fetch_data_from_disk())
        else:
            json_text = AppList.fetch_data_from_net()
            self.data = AppList.json_to_obj(json_text)
            self.write_data_to_disk(json_text)

        if self.remove_trademark_symbols:
            self.id_lookup = {pair["appid"]: "".join(filter(AppList.filter_trademark, pair["name"])) for pair in self.data}
        else:
            self.id_lookup = {pair["appid"]: pair["name"] for pair in self.data}
            # self.name_lookup = {pair["name"]: pair["appid"] for pair in self.data}

        return self





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
    with open(path, encoding='UTF-8') as file:
        file_string = file.read()
        file_string = json_from_valve(file_string)
        if OUTPUT__SHAREDCONFIG_VDF_JSON:
            with open(path + ".json", "w", encoding='UTF-8') as out:
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

    with open("Log/" + filename, "w", encoding='UTF-8') as file:
        file.write(msg)



def main(): # on_demend_refetch=False
    applist = AppList().get_applist()
    tags = tag_obj_from_path(DefaultPath)
    games = [game for tag in tags for game in tag.games]

    for game in games:
        game.fetch_game_data(applist)

    for tag in tags:
        print(tag.str_games())


main()
