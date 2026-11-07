#!/usr/bin/env python3

__version__ = "1.4.1"

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
    Smart,
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


def sendTestFailureEmail(config, logger, test, disk, reason):
    if not config.email.enabled:
        logger.info("Test failure email notifications are not enabled, skipping...")
        return

    try:
        Email.send(
            message=Message(
                subject="SMART test failed on {}".format(disk.disk),
                body="A {} SMART test has failed on {}.\n\n{}\n\nPlease see server logs located at {} for more details.".format(
                    test.testType.value, disk.disk, reason, config.log.file
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


def runTest(config, db, logger, test, disk):
    try:
        logger.info(
            "Running {} SMART test for {}".format(test.testType.value, disk.disk)
        )

        Smart(
            testType=test.testType.value,
            disk=disk.disk,
            smartScriptPath=SMART_SCRIPT_PATH,
        ).run(
            onOutput=logger.info,
            onError=logger.error,
        )

        logger.info("Passed {} SMART test for {}".format(test.testType.value, disk.disk))
    except TestFailedException as e:
        logger.error("Failed {} SMART test for {}".format(test.testType.value, disk.disk))

        sendTestFailureEmail(
            config=config, logger=logger, test=test, disk=disk, reason=e
        )
    except Exception as e:
        logger.error(
            "Error running {} SMART test for {}: {}".format(
                test.testType.value, disk.disk, e
            )
        )

        sendTestFailureEmail(
            config=config, logger=logger, test=test, disk=disk, reason=e
        )
    finally:
        db.updateTestDateForDisk(
            disk=disk.disk,
            testType=test.testType.value,
        )
        disk.updateLastTestDateForTest(test=test)

        logger.info("*" * 60)


def enqueueTest(logger, test, disks):
    for disk in disks:
        logger.debug(
            "Checking {} SMART test for {}...".format(test.testType.value, disk.disk)
        )

        try:
            test.enqueueForDisk(disk=disk)

            logger.debug(
                "Enqueued {} SMART test for {}".format(test.testType.value, disk.disk)
            )
        except NotEnabledException:
            logger.debug(
                "{} SMART test not enabled, skipping...".format(test.testType.value)
            )
        except TestNotRequiredException:
            logger.debug(
                "{} SMART test not required for {} last test was ran on {}, skipping...".format(
                    test.testType.value,
                    disk.disk,
                    disk.getLastTestDateForTest(test),
                )
            )
        except TooManyDisksException:
            logger.debug(
                "Can't run {} SMART test for {} {} disk(s) have already been enqueued, skipping...".format(
                    test.testType.value,
                    disk.disk,
                    test.disksPerRun,
                )
            )
        except TooSoonException:
            logger.debug(
                "Can't run {} SMART test for {} a {} test was last ran {} day(s) ago, skipping...".format(
                    test.testType.value,
                    disk.disk,
                    test.testType.value,
                    test.daysSinceLastRun(),
                )
            )


def runScheduledTests(config, db, logger, disks):
    tests = [
        Test(
            testType=testType,
            enabled=testConfig.enabled,
            frequencyDays=testConfig.frequency_days,
            offsetDays=testConfig.offset_days,
            disksPerRun=testConfig.disks_per_run,
            lastTestDate=db.getLastTestDateForTest(testType.value),
        )
        for testType, testConfig in [
            (TestType.LONG, config.long),
            (TestType.SHORT, config.short),
        ]
    ]

    for test in tests:
        enqueueTest(logger=logger, test=test, disks=disks)

        for disk in test.enqueuedDisks():
            runTest(config=config, db=db, logger=logger, test=test, disk=disk)


def runOneOffTest(config, db, logger, disks, testType, diskName):
    disk = next((disk for disk in disks if disk.disk == diskName), None)

    if disk is None:
        raise Exception(
            "{} is not listed in the [disks] section of the config".format(diskName)
        )

    runTest(
        config=config,
        db=db,
        logger=logger,
        test=Test(testType=TestType(testType)),
        disk=disk,
    )


def main():
    try:
        # held until the process exits
        lock = Lock(LOCK_FILE_PATH)
        args = Args()
        config = Config(configFile=args.config)
        db = Database(dbFile=config.database.file)
        logger = Logger(logFile=config.log.file, level=config.log.level)
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

        logger.info("=" * 60)
        logger.info("smart-runner v{} started".format(__version__))
        logger.info("=" * 60)

        if args.test:
            runOneOffTest(
                config=config,
                db=db,
                logger=logger,
                disks=disks,
                testType=args.test,
                diskName=args.disk,
            )
        else:
            runScheduledTests(config=config, db=db, logger=logger, disks=disks)
    except Exception as e:
        print("Error: {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
