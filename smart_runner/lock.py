from atexit import register
from os import getcwd, remove

LOCK_FILE_PATH = getcwd() + "/.smart-runner.lock"


class Lock:
    def __init__(self):
        if self.isLocked():
            raise RuntimeError("smart-runner is already running")

        self.createLock()

        # Register the removeLock function to be called on exit
        register(self.removeLock)

    def createLock(self):
        with open(LOCK_FILE_PATH, "w") as lockFile:
            lockFile.write("")

    def removeLock(self):
        try:
            remove(LOCK_FILE_PATH)
        except FileNotFoundError:
            pass  # If the file is already removed or doesn't exist, ignore the error

    def isLocked(self):
        try:
            with open(LOCK_FILE_PATH, "r") as lockFile:
                return True
        except FileNotFoundError:
            return False
