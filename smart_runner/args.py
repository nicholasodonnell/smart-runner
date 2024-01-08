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
            args = parser.parse_args()

            return {
                "config": args.conf,
            }
        except Exception as e:
            raise Exception("Failed to parse arguments: {}".format(e))

    def __getattr__(self, attr):
        return self.__args__.get(attr)
