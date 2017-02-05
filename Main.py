import json
import re
import urllib.parse
import urllib.request

# from urllib.parse import urlencode
# from urllib.request import Request, urlopen

DefaultPath = "Test\\sharedconfig.vdf.txt"  # TODO Change default path to the eqvivalent of C:\Program Files (x86)\Steam\userdata\<ID>\7\remote
WRITE_JSON_FILE = False
WRITE_FAILED_NAME_FETCH_HTTP = False


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
            with open(path + ".json", 'w') as out:
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


def fetch_name(app_id):
    html_string = str(urllib.request.urlopen("http://store.steampowered.com/app/" + app_id).read())

    name_start = html_string.find("<div class=\"apphub_AppName\">")

    if name_start == -1 and html_string.find("agecheck"):
        #Does not work
        '''
        params = {
            "ageDay": "1",
            "ageMonth": "January",
            "ageYear": "1986",
            "snr": "1_agecheck_agecheck__age-gate"
        }

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            #"Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.8,he;q=0.6",
            "Content-type": "application/x-www-form-urlencoded",
            # cookie
            "DNT": "1",
            "Origin": "http://store.steampowered.com",

            "Referer": ("http://store.steampowered.com/agecheck/app/" + app_id + "/"),
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
        }

        request = urllib.request.Request("http://store.steampowered.com/agecheck/app/" + app_id + "/", urllib.parse.urlencode(params).encode(), headers)

        html_string = str(urllib.request.urlopen(request).read())
        name_start = html_string.find("<div class=\"apphub_AppName\">")
        '''

    if name_start == -1:
        if WRITE_FAILED_NAME_FETCH_HTTP:
            with open("Log/fetch_error.html.txt", 'w') as out:
                out.write(html_string.replace("\\r", "\r").replace("\\t", "\t").replace("\\n", "\n"))
        return None  # //Can't fetch the name

    name_end = html_string.find("</div>", name_start + len("<div class=\"apphub_AppName\">"))
    name = html_string[name_start + len("<div class=\"apphub_AppName\">"): name_end]

    return name


# main()
print(fetch_name("448510"))
