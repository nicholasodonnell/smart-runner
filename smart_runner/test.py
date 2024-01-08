from .command import Command
from enum import Enum
from datetime import datetime, timedelta
from os import getcwd

SMART_RUNNER_PATH = getcwd() + "/smart.sh"


class TestType(Enum):
    SHORT = "short"
    LONG = "long"


class NotEnabledException(Exception):
    pass


class TestNotRequiredException(Exception):
    pass


class TooManyDisksException(Exception):
    pass


class TooSoonException(Exception):
    pass


class TestFailedException(Exception):
    pass


class Test:
    def __init__(
        self,
        testType,
        enabled=False,
        frequencyDays=1,
        offsetDays=0,
        disksPerRun=1,
        lastTestDate=None,
    ):
        self.testType = testType
        self.enabled = enabled
        self.frequencyDays = frequencyDays
        self.offsetDays = offsetDays
        self.disksPerRun = disksPerRun
        self.lastTestDate = lastTestDate
        self.disks = []

    def longEnoughSinceLastTest(self):
        if self.lastTestDate is None:
            return True

        return self.lastTestDate + timedelta(days=self.offsetDays) <= datetime.now()

    def daysSinceLastRun(self):
        if self.lastTestDate is None:
            return 0

        return (datetime.now() - self.lastTestDate).days

    def runTestForDisk(self, disk, onOutput, onError, onFinished):
        if not self.enabled:
            raise NotEnabledException()

        if not disk.needsTest(self):
            raise TestNotRequiredException()

        if self.disksPerRun != 0 and len(self.disks) >= self.disksPerRun:
            raise TooManyDisksException()

        if not self.longEnoughSinceLastTest():
            raise TooSoonException()

        self.disks.append(disk)

        command = Command(
            cmd=SMART_RUNNER_PATH + " " + self.testType.value + " " + disk.disk,
            stdout=onOutput,
            stderr=onError,
        )
        status = command.exec()

        onFinished()

        if status != 0:
            raise TestFailedException()
