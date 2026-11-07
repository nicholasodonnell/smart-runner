from .command import Command


class TestFailedException(Exception):
    pass


class Smart:
    def __init__(self, testType, disk, smartScriptPath):
        self.testType = testType
        self.disk = disk
        self.smartScriptPath = smartScriptPath

    def run(self, onOutput, onError):
        errors = []

        def handleError(line):
            errors.append(line)
            onError(line)

        command = Command(
            args=[self.smartScriptPath, self.testType, self.disk],
            stdout=onOutput,
            stderr=handleError,
        )
        status = command.exec()

        if status != 0:
            raise TestFailedException(
                "\n".join(errors) or "smart.sh exited with status {}".format(status)
            )
