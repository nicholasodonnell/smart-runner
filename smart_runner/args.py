from argparse import ArgumentParser


class Args:
    def __init__(self):
        self.__args__ = self.__getArgs__()

    def __getArgs__(self):
        try:
            parser = ArgumentParser()
            parser.add_argument(
                "-c", "--conf", required=True, help="Path to config file"
            )
            parser.add_argument(
                "-t",
                "--test",
                choices=["short", "long"],
                help="Run this test once on --disk now, ignoring the schedule",
            )
            parser.add_argument(
                "-d",
                "--disk",
                help="Disk or mount from the [disks] config section to test with --test",
            )
            args = parser.parse_args()

            if (args.test is None) != (args.disk is None):
                parser.error("--test and --disk must be used together")

            return {
                "config": args.conf,
                "test": args.test,
                "disk": args.disk,
            }
        except Exception as e:
            raise Exception("Failed to parse arguments: {}".format(e))

    def __getattr__(self, attr):
        return self.__args__.get(attr)
