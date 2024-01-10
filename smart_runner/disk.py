from datetime import datetime, timedelta
from .test import Test, TestType


class Disk:
    def __init__(self, disk, lastShortTestDate, lastLongTestDate):
        self.disk = disk
        self.lastShortTestDate = lastShortTestDate
        self.lastLongTestDate = lastLongTestDate

    def needsShortTest(self, frequencyDays):
        try:
            if self.lastShortTestDate is None and self.lastLongTestDate is None:
                return True

            if self.lastLongTestDate is None:
                nextShortTestDate = self.lastShortTestDate + timedelta(
                    days=frequencyDays
                )

                return datetime.now() >= nextShortTestDate

            if self.lastShortTestDate is None:
                return True

            nextShortTestDate = max(
                [self.lastShortTestDate, self.lastLongTestDate]
            ) + timedelta(days=frequencyDays)

            return datetime.now() >= nextShortTestDate
        except Exception as e:
            raise Exception("Failed to check if disk needs short test: {}".format(e))

    def needsLongTest(self, frequencyDays):
        try:
            if self.lastLongTestDate is None:
                return True

            nextLongTestDate = self.lastLongTestDate + timedelta(days=frequencyDays)

            return datetime.now() >= nextLongTestDate
        except Exception as e:
            raise Exception("Failed to check if disk needs long test: {}".format(e))

    def needsTest(self, test: Test):
        try:
            if test.testType == TestType.SHORT:
                return self.needsShortTest(test.frequencyDays)

            if test.testType == TestType.LONG:
                return self.needsLongTest(test.frequencyDays)

            return False
        except Exception as e:
            raise Exception("Failed to check if disk needs test: {}".format(e))

    def getLastShortTestDate(self):
        return (
            datetime.strftime(self.lastShortTestDate, "%Y-%m-%d")
            if self.lastShortTestDate is not None
            else self.getLastLongTestDate()
        )

    def getLastLongTestDate(self):
        return (
            datetime.strftime(self.lastLongTestDate, "%Y-%m-%d")
            if self.lastLongTestDate is not None
            else None
        )

    def getLastTestDateForTest(self, test: Test):
        try:
            if test.testType == TestType.SHORT:
                return self.getLastShortTestDate()

            if test.testType == TestType.LONG:
                return self.getLastLongTestDate()

            return None
        except Exception as e:
            raise Exception("Failed to get last test date for disk: {}".format(e))
