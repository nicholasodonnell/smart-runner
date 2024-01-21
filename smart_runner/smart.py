from .command import Command


class TestFailedException(Exception):
    pass


class Smart:
    def __init__(self, testType, disk, smartScriptPath):
        self.testType = testType
        self.disk = disk
        self.smartScriptPath = smartScriptPath

    def run(self, onOutput, onError):
        command = Command(
            cmd=self.smartScriptPath + " " + self.testType + " " + self.disk,
            stdout=onOutput,
            stderr=onError,
        )
        status = command.exec()

        if status != 0:
            raise TestFailedException()
