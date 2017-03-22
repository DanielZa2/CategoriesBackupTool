import json
import os
import datetime
import string
import vdf  # Source https://github.com/ValvePython/vdf
import collections
import logging


from urllib import request as urlrequest
from urllib import error as urlerror


logging.basicConfig(filename="log.log")


class ParseException(Exception):
    pass


class Category:
    """Describe a single steam category."""

    def __init__(self, name):
        self.name = name
        self.games = []

    def __repr__(self):
        return "<Category: " + self.name + ">"

    def __str__(self):
        return "Category: " + self.name

    def app_string(self):
        """Return human-redable string formated to contain the category and all the apps that belong to it."""
        ret = str(self)
        for game in self.games:
            ret += "\n\t"
            ret += str(game)
        return ret


class Categories:
    """Describe a group of categories. Mainly the result of processing the user library."""

    def __init__(self):
        self.lst = []

    def name_apps(self, applist):
        """Gives a name for all the apps in all the tags based on the names stored in the applist"""
        gamelist = [game for tag in self.lst for game in tag.games]
        applist.name_apps(gamelist)

    def apps_string(self, filter_symbols=False):
        """Return human-redable string formated to contain all the categories and all the apps that belong to them. Can filter © and ™ symbols from the names."""
        ret = ""
        for tag in self.lst:
            ret += tag.app_string()
            ret += "\n"
        if filter_symbols:
            f = lambda s: s != "©" and s != "™" and s != "®"
            return "".join(filter(f, ret))
        else:
            return ret

    @staticmethod
    def factory(path):
        """Read all the apps the user has from sharedconfig.vdf. Return fitting valid Categories obj"""
        apps = Categories.__apps_from_file__(path)
        apps = {appID: apps[appID] for appID in apps if ("tags" in apps[appID]) and isinstance(apps[appID]["tags"], dict)}  # remove all the games without categories
        tag_names = sorted(set([tag_name for app in apps.values() for tag_name in app["tags"].values()]))  # get all the possible tags from the different apps

        ret = Categories()
        ret.lst = [Category(tag_name) for tag_name in tag_names]
        games = [SteamApp(game_id) for game_id in sorted(apps.keys())]

        for tag in ret.lst:
            for game in games:
                if tag.name in apps[game.id]["tags"].values():
                    tag.games.append(game)

        return ret

    @staticmethod
    def __apps_from_file__(path):
        """Read all the apps the user has from sharedconfig.vdf. Returns a dict. Intermidiate function."""
        with open(path, encoding='UTF-8') as file:
            file_string = file.read()
            parsed = vdf.loads(file_string)
            return parsed["UserRoamingConfigStore"]["Software"]["Valve"]["Steam"]["apps"]


class SteamApp:
    """Describe a single steam app. That is, more often than not, a game."""

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
            return "<SteamApp: AppID_" + self.id + ">"
        else:
            return "<SteamApp: " + self.name + ">"

    def get_name(self, applist):
        """Lookup your own name in the supplied list of names."""
        if self.id.isdigit():
            self.name = applist.id_lookup.get(int(self.id), None)  # default=None


class SteamAppList:
    """Describe a list of appIDs and app names. Used to find the name of the app based on the id."""
    FETCH_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v0001/"
    FETCH_LOCAL_PATH = "Applist.txt"

    def __init__(self):
        self.__data__ = None
        self.id_lookup = None
        # self.name_lookup = None

    @staticmethod
    def fetch_from_net(url=FETCH_URL):
        """Fetch new AppList from the web. See: http://api.steampowered.com/ISteamApps/GetAppList/v0001/ """
        req = urlrequest.Request(url)
        try:
            json_bytes = urlrequest.urlopen(req).read()
        except urlerror.HTTPError:
            logging.exception("Failed to fetch applist from net")
            return None

        return json_bytes.decode("utf-8")

    @staticmethod
    def fetch_from_disk(path=FETCH_LOCAL_PATH):
        """Fetch AppList from the disk where it was previously saved."""
        with open(path, encoding='UTF-8') as file:
            return file.read()

    @staticmethod
    def write_apps_to_disk(data, path=FETCH_LOCAL_PATH):
        """Write ApplList to the disk. Probably because a new one was fetched from the internet."""
        with open(path, "w", encoding='UTF-8') as file:
            file.write(data)

    @staticmethod
    def json_to_list(json_text):
        """Parse the json data and turn it into a list of id-name pairs"""
        try:
            game_info = json.loads(json_text)
            return game_info["applist"]["apps"]["app"]

        except (json.decoder.JSONDecodeError, KeyError):
            logging.exception("Failed to parse fetched applist")
            return None

    def name_apps(self, lst):
        """Give names to all the apps in the list,"""
        for game in lst:
            game.get_name(self)

    def fetch(self, fetch_from_net=False):
        """Fill the object with data about app names. get the data either from a local file or from the internet. Automaticlly access the net if the file is missing."""
        if self.__data__ is not None:
            return self

        if fetch_from_net or not os.path.exists(SteamAppList.FETCH_LOCAL_PATH):
            json_text = SteamAppList.fetch_from_net()
            self.__data__ = SteamAppList.json_to_list(json_text)
            SteamAppList.write_apps_to_disk(json_text)
        else:
            self.__data__ = SteamAppList.json_to_list(SteamAppList.fetch_from_disk())

        self.id_lookup = {pair["appid"]: pair["name"] for pair in self.__data__}
        # self.name_lookup = {pair["name"]: pair["appid"] for pair in self.data}
        return self




class SteamLocator:
    """Collection of methods used to locate steam on a given machine. Not a real class and shouldn't be instanced."""

    @staticmethod
    def locate_steam():
        """Find the installation directory on steam and return all the possible locations of sharedconfig.vdf"""

        if os.path.exists("SteamLocation.txt"):
            with open("SteamLocation.txt", encoding='UTF-8') as file:
                file_string = file.read()
                locations = json.loads(file_string)
                f = lambda pair: os.path.exists(pair[1])
                locations = list(filter(f, locations))
                if locations:
                    return locations

        if os.name == "nt":
            locations = SteamLocator.locate_steam_windows()
        elif os.name == "posix":
            locations = SteamLocator.locate_steam_posix()
        else:
            class UnsupportedOSException(Exception):
                pass

            raise UnsupportedOSException("Unsupported OS. Can't search for steam.")

        with open("SteamLocation.txt", "w", encoding='UTF-8') as file:
            file.write(json.dumps(locations))
        return locations

    @staticmethod
    def locate_steam_windows():
        """Find the location of the steam directory and sharedconfig.vdf on windows."""
        results = []
        popular_locations = {"C:/Program Files (x86)/Steam", "C:/Program Files/Steam", "D:/Program Files (x86)/Steam", "D:/Program Files/Steam"}

        for dirpath in popular_locations:
            if os.path.exists(dirpath + "/Steam.exe") and os.path.exists(dirpath + "/userdata/"):
                f = lambda s: (s, dirpath + "/userdata/" + s + "/7/remote/sharedconfig.vdf")
                results.extend(map(f, os.listdir(dirpath + "/userdata/")))

        f = lambda pair: os.path.exists(pair[1])
        results = list(filter(f, results))
        if results:
            return results

        # location haven't been found in the common places. Look farther.


        # Source: http://stackoverflow.com/a/34187346/2842452
        available_drives = ['%s:/' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]

        for drive in available_drives:
            for dirpath, _, filenames in os.walk(drive):
                if "Steam.exe" in filenames and os.path.exists(dirpath + "/userdata/"):
                    f = lambda s: (s, dirpath.replace("\\", "/") + "/userdata/" + s + "/7/remote/sharedconfig.vdf")
                    results.extend(map(f, os.listdir(dirpath + "/userdata/")))

        f = lambda pair: os.path.exists(pair[1])
        results = list(filter(f, results))
        return results

    @staticmethod
    def locate_steam_posix():
        """Find the location of the steam directory and sharedconfig.vdf on mac / linux. !!!Untested!!!"""
        results = []
        popular_locations = {"~/.local/share/Steam", "~/Steam", "~/.steam"}  # Found those on the web. Might be wrong. Not sure where it is actually installed.

        for dirpath in popular_locations:
            if os.path.exists(dirpath + "/Steam.exe") and os.path.exists(dirpath + "/userdata/"):
                f = lambda s: (s, dirpath + "/userdata/" + s + "/7/remote/sharedconfig.vdf")
                results.extend(map(f, os.listdir(dirpath + "/userdata/")))

        f = lambda pair: os.path.exists(pair[1])
        results = list(filter(f, results))
        if results:
            return results

        # location haven't been found in the common places. Look farther.

        for dirpath, _, filenames in os.walk("/"):
            if "Steam.exe" in filenames and os.path.exists(dirpath + "/userdata/"):
                f = lambda s: (s, dirpath + "/userdata/" + s + "/7/remote/sharedconfig.vdf")
                results.extend(map(f, os.listdir(dirpath + "/userdata/")))

        f = lambda pair: os.path.exists(pair[1])
        results = list(filter(f, results))
        return results


class BackupAndRestore:
    """Collection of methods to backup and restore steam categories. Not a real class and shouldn't be instanced."""

    @staticmethod
    def backup_config_whole_file(src, dst):
        """Backup the file by coping the src to the dst. The old backup method."""
        try:
            with open(src, encoding='UTF-8') as input_file:
                with open(dst, "w", encoding='UTF-8') as output_file:
                    output_file.write(input_file.read())
        except UnicodeDecodeError:
            raise ParseException("Can't open source file to backup")
        except (FileExistsError, IOError):
            raise ParseException("Can't open target file to backup")

    @staticmethod
    def restore_config_whole_file(src, dst):
        """Restore the backup from src to dst. if dst exists, rename it. The old restore method."""
        try:
            if os.path.exists(dst):
                new_name = dst + " " + str(datetime.datetime.now().strftime("%Y-%m-%d %H;%M;%S %f")) + ".bak"
                os.rename(dst, new_name)
            with open(dst, "w", encoding='UTF-8') as output_file:
                with open(src, encoding='UTF-8') as input_file:
                    output_file.write(input_file.read())
        except UnicodeDecodeError:
            raise ParseException("Can't open source file to restore")
        except (FileExistsError, IOError):
            raise ParseException("Can't open target file to restore")

    @staticmethod
    def backup_config(src, dst):
        """Backup the config file by copying only the categories to and external file. The new method. """
        with open(src, encoding='UTF-8') as valves_file:
            content = vdf.loads(valves_file.read(), mapper=collections.OrderedDict)
            target_categories = content["UserRoamingConfigStore"]["Software"]["Valve"]["Steam"]["apps"]
            filtered_target = {x: target_categories[x].get("tags", None) for x in target_categories.keys()}
            filtered_target = {x: y for x, y in filtered_target.items() if y is not None and y is not ""}

            with open(dst, "w", encoding='UTF-8') as backup_file:
                json.dump(filtered_target, backup_file, indent="\t")

    @staticmethod
    def restore_config(src, dst):
        """Restore the backup. if dst exists, rename it. The new method."""
        try:
            with open(src, encoding='UTF-8') as backup_file:
                backedup_categories = json.loads(backup_file.read(), object_pairs_hook=collections.OrderedDict)

            with open(dst, encoding='UTF-8') as valves_file:
                content = vdf.loads(valves_file.read(), mapper=collections.OrderedDict)
                target_categories = content["UserRoamingConfigStore"]["Software"]["Valve"]["Steam"]["apps"]

                content["UserRoamingConfigStore"]["Software"]["Valve"]["Steam"]["apps"] = BackupAndRestore.__insert_categories__(target_categories, backedup_categories)

            new_name = dst + " " + str(datetime.datetime.now().strftime("%Y-%m-%d %H;%M;%S %f")) + ".bak"
            os.rename(dst, new_name)
            with open(dst, "w", encoding='UTF-8') as output_file:
                vdf.dump(content, output_file, pretty=True)


        except UnicodeDecodeError:
            raise ParseException("Can't open source file to restore")
        except (FileExistsError, IOError):
            raise ParseException("Can't open target file to restore")

    @staticmethod
    def __insert_categories__(target, src):
        for app_id, tags in src.items():
            if app_id in target:
                target[app_id]["tags"] = tags

        return target




def main():
    # backup_better("Test/sharedconfig.vdf", "Test/123.txt")
    # BackupAndRestore.restore_better("Test/123.txt", "Test/sharedconfig.vdf")
    pass

if __name__ == "__main__":
    main()


