from configparser import ConfigParser
from os import path


class ConfigDict:
    def __init__(self, value):
        self.__value__ = value

    def __getattr__(self, attr):
        return self.__value__.get(attr)


class Config:
    def __init__(self, configFile):
        self.configFile = configFile
        self.__config__ = self.__getConfig__()

    def __getConfig__(self):
        try:
            if not path.exists(self.configFile):
                raise Exception(self.configFile + " does not exist")

            config = ConfigParser(allow_no_value=True)
            config.read(self.configFile)

            return {
                "disks": config.options("disks")
                if config.has_section("disks")
                else list(),
                "database": ConfigDict(
                    {
                        "file": config.get(
                            "database", "file", fallback="/var/lib/smart-runner/smart-runner.json"
                        ),
                    }
                ),
                "short": ConfigDict(
                    {
                        "enabled": config.getboolean(
                            "short", "enabled", fallback=False
                        ),
                        "frequency_days": max(
                            config.getint("short", "frequency_days", fallback=7), 1
                        ),
                        "disks_per_run": max(
                            config.getint("short", "disks_per_run", fallback=1), 1
                        ),
                        "offset_days": max(
                            config.getint("short", "offset_days", fallback=0), 0
                        ),
                    }
                ),
                "long": ConfigDict(
                    {
                        "enabled": config.getboolean("long", "enabled", fallback=False),
                        "frequency_days": max(
                            config.getint("long", "frequency_days", fallback=30), 1
                        ),
                        "disks_per_run": max(
                            config.getint("long", "disks_per_run", fallback=1), 1
                        ),
                        "offset_days": max(
                            config.getint("long", "offset_days", fallback=0), 0
                        ),
                    }
                ),
                "log": ConfigDict(
                    {
                        "file": config.get(
                            "log", "file", fallback="/var/log/smart-runner.log"
                        ),
                        "level": config.get("log", "level", fallback="INFO"),
                    }
                ),
                "email": ConfigDict(
                    {
                        "enabled": config.getboolean(
                            "email", "enabled", fallback=False
                        ),
                        "from_email": config.get("email", "from_email", fallback=None),
                        "to_email": config.get("email", "to_email", fallback=None),
                    }
                ),
                "smtp": ConfigDict(
                    {
                        "host": config.get("smtp", "host", fallback=None),
                        "port": config.get("smtp", "port", fallback=587),
                        "ssl": config.getboolean("smtp", "ssl", fallback=False),
                        "tls": config.getboolean("smtp", "tls", fallback=False),
                        "user": config.get("smtp", "user", fallback=None),
                        "password": config.get("smtp", "password", fallback=None),
                    }
                ),
            }
        except Exception as e:
            raise Exception("Failed to read config file: {}".format(e))

    def __getattr__(self, attr):
        return self.__config__.get(attr)
