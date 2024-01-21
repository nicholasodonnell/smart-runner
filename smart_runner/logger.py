from logging import Formatter, getLogger, handlers, DEBUG, StreamHandler
from sys import stdout


class Logger:
    def __init__(self, logFile, level):
        self.logFile = logFile
        self.level = level.upper()
        self.__logger__ = getLogger()
        self.__setupLogger__()

    def __setupLogger__(self):
        try:
            formatter = Formatter("[%(asctime)s][%(levelname)s] %(message)s")
            fileHander = handlers.RotatingFileHandler(
                self.logFile, maxBytes=1024 * 1024 * 10, backupCount=10
            )
            fileHander.setFormatter(formatter)
            stdoutHandler = StreamHandler(stdout)
            stdoutHandler.setFormatter(formatter)

            self.__logger__.setLevel(self.level)
            self.__logger__.addHandler(fileHander)
            self.__logger__.addHandler(stdoutHandler)
        except Exception as e:
            raise Exception("Failed to setup logger: {}".format(e))

    def __getattr__(self, attr):
        return getattr(self.__logger__, attr)
