from atexit import register
from os import remove


class Lock:
    def __init__(self, file):
        self.file = file

        if self.isLocked():
            raise RuntimeError("smart-runner is already running")

        self.createLock()

        # Register the removeLock function to be called on exit
        register(self.removeLock)

    def createLock(self):
        with open(self.file, "w") as lockFile:
            lockFile.write("")

    def removeLock(self):
        try:
            remove(self.file)
        except FileNotFoundError:
            pass  # If the file is already removed or doesn't exist, ignore the error

    def isLocked(self):
        try:
            with open(self.file, "r") as lockFile:
                return True
        except FileNotFoundError:
            return False
