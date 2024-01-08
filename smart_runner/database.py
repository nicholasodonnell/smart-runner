from datetime import datetime
from json import dump, load
from pathlib import Path


class Database:
    def __init__(self, dbFile):
        self.dbFile = dbFile
        self.__db__ = self.__readDbFile__()

    def __readDbFile__(self):
        try:
            if Path(self.dbFile).exists():
                with open(self.dbFile, "r") as file:
                    return load(file)
            else:
                return {}
        except Exception as e:
            raise Exception("Failed to read db file: {}".format(e))

    def __writeDbFile__(self):
        try:
            with open(self.dbFile, "w") as file:
                dump(self.__db__, file, indent=4, sort_keys=True)
        except Exception as e:
            raise Exception("Failed to write db file: {}".format(e))

    def getLastTestDateForDisk(self, disk, testType):
        try:
            if disk not in self.__db__:
                return None

            return (
                datetime.strptime(
                    self.__db__[disk]["last_" + testType + "_test_date"],
                    "%Y-%m-%d",
                )
                if self.__db__[disk]["last_" + testType + "_test_date"] is not None
                else None
            )
        except Exception as e:
            raise Exception("Failed to get db: {}".format(e))

    def getLastTestDateForTest(self, testType):
        try:
            if not self.__db__:
                return None

            values = [
                datetime.strptime(
                    self.__db__[disk]["last_" + testType + "_test_date"],
                    "%Y-%m-%d",
                )
                for disk in self.__db__
                if self.__db__[disk]["last_" + testType + "_test_date"] is not None
            ]

            if not values:
                return None

            return max(values)
        except Exception as e:
            raise Exception("Failed to get db: {}".format(e))

    def updateTestDateForDisk(self, disk, testType):
        try:
            if disk not in self.__db__:
                self.__db__[disk] = {
                    "last_short_test_date": None,
                    "last_long_test_date": None,
                }

            self.__db__[disk][
                "last_" + testType + "_test_date"
            ] = datetime.now().strftime("%Y-%m-%d")

            self.__writeDbFile__()
        except Exception as e:
            raise Exception("Failed to update db: {}".format(e))
