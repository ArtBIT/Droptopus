import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--debug",
    help="Print lots of debugging statements",
    action="store_const",
    dest="loglevel",
    const=logging.DEBUG,
    default=logging.WARNING,
)
parser.add_argument(
    "-v",
    "--verbose",
    help="Be verbose",
    action="store_const",
    dest="loglevel",
    const=logging.INFO,
)
args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s | %(message)s", filename="debug.log", level=args.loglevel
)
