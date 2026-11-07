from fcntl import flock, LOCK_EX, LOCK_NB


class Lock:
    def __init__(self, file):
        self.file = file

        # the kernel releases the lock when the process exits, even if it crashes
        self.__handle__ = open(self.file, "w")

        try:
            flock(self.__handle__, LOCK_EX | LOCK_NB)
        except BlockingIOError:
            self.__handle__.close()
            raise RuntimeError("smart-runner is already running")
