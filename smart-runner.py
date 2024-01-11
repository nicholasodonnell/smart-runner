#!/usr/bin/env python3

__version__ = "1.1.3"

from smart_runner import (
    Args,
    Config,
    Database,
    Disk,
    Email,
    Lock,
    Logger,
    Message,
    NotEnabledException,
    SMTP,
    Test,
    TestFailedException,
    TestNotRequiredException,
    TestType,
    TooManyDisksException,
    TooSoonException,
)
from sys import exit
from os import path


SMART_SCRIPT_PATH = path.realpath(path.dirname(__file__)) + "/smart.sh"
LOCK_FILE_PATH = path.realpath(path.dirname(__file__)) + "/.smart-runner.lock"


def sendTestFailureEmail(config, logger, test, disk):
    if not config.email.enabled:
        logger.info("Test failure email notifications are not enabled, skipping...")
        return

    try:
        Email.send(
            message=Message(
                subject="SMART test failed on {}".format(disk.disk),
                body="A {} SMART test has failed on {}. Please see server logs located at {} for more details.".format(
                    test.testType.value, disk.disk, config.log.file
                ),
                fromEmail=config.email.from_email,
                toEmail=config.email.to_email,
            ),
            smtp=SMTP(
                host=config.smtp.host,
                port=config.smtp.port,
                ssl=config.smtp.ssl,
                tls=config.smtp.tls,
                user=config.smtp.user,
                password=config.smtp.password,
            ),
        )

        logger.info("Sent test failure email to {}".format(config.email.to_email))
    except Exception as e:
        logger.warning("Error sending test failure email: {}".format(e))


def main():
    try:
        Lock(LOCK_FILE_PATH)
        args = Args()
        config = Config(configFile=args.config)
        db = Database(dbFile=config.database.file)
        logger = Logger(logFile=config.log.file)
        disks = [
            Disk(
                disk=disk,
                lastShortTestDate=db.getLastTestDateForDisk(
                    disk=disk,
                    testType=TestType.SHORT.value,
                ),
                lastLongTestDate=db.getLastTestDateForDisk(
                    disk=disk,
                    testType=TestType.LONG.value,
                ),
            )
            for disk in config.disks
        ]
        shortTest = Test(
            testType=TestType.SHORT,
            smartScriptPath=SMART_SCRIPT_PATH,
            enabled=config.short.enabled,
            frequencyDays=config.short.frequency_days,
            offsetDays=config.short.offset_days,
            disksPerRun=config.short.disks_per_run,
            lastTestDate=db.getLastTestDateForTest(TestType.SHORT.value),
        )
        longTest = Test(
            testType=TestType.LONG,
            smartScriptPath=SMART_SCRIPT_PATH,
            enabled=config.long.enabled,
            frequencyDays=config.long.frequency_days,
            offsetDays=config.long.offset_days,
            disksPerRun=config.long.disks_per_run,
            lastTestDate=db.getLastTestDateForTest(TestType.LONG.value),
        )

        logger.info("=" * 60)
        logger.info("smart-runner v{} started".format(__version__))
        logger.info("=" * 60)

        for disk in disks:
            for test in [longTest, shortTest]:
                logger.info(
                    "Checking {} SMART test for {}...".format(
                        test.testType.value,
                        disk.disk,
                    )
                )

                try:
                    test.runTestForDisk(
                        disk=disk,
                        onOutput=logger.info,
                        onError=logger.error,
                        onFinished=lambda: db.updateTestDateForDisk(
                            disk=disk.disk,
                            testType=test.testType.value,
                        ),
                    )

                    logger.info(
                        "Finished {} SMART test for {}".format(
                            test.testType.value, disk.disk
                        )
                    )

                    break
                except NotEnabledException as e:
                    logger.info(
                        "{} SMART test not enabled, skipping...".format(
                            test.testType.value
                        )
                    )

                    continue
                except TestNotRequiredException as e:
                    logger.info(
                        "{} SMART test not required for {} last test was ran on {}, skipping...".format(
                            test.testType.value,
                            disk.disk,
                            disk.getLastTestDateForTest(test),
                        )
                    )

                    continue
                except TooManyDisksException as e:
                    logger.warning(
                        "Can't run {} SMART test for {} {} disk(s) have already been tested, skipping...".format(
                            test.testType.value,
                            disk.disk,
                            test.disksPerRun,
                        )
                    )

                    continue
                except TooSoonException as e:
                    logger.warning(
                        "Can't run {} SMART test for {} a {} test was last ran {} day(s) ago, skipping...".format(
                            test.testType.value,
                            disk.disk,
                            test.testType.value,
                            test.daysSinceLastRun(),
                        )
                    )

                    continue
                except TestFailedException as e:
                    logger.error(
                        "Failed {} SMART test for {}".format(
                            test.testType.value, disk.disk
                        )
                    )

                    sendTestFailureEmail(
                        config=config, logger=logger, test=test, disk=disk
                    )

                    break
                finally:
                    logger.info("*" * 60)

    except Exception as e:
        print("Error: {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
