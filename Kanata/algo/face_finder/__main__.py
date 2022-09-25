import argparse
from . import *
import abcli.logging
import logging

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    default="",
    help="find|track",
)
parser.add_argument(
    "--area_threshold",
    type=float,
    default=0.8,
)
parser.add_argument(
    "--crop",
    type=int,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--destination",
    type=str,
    default="",
)
parser.add_argument(
    "--filename",
    type=str,
    default="",
)
parser.add_argument(
    "--kind",
    type=str,
    default="",
    help="image|object",
)
parser.add_argument(
    "--missing_frames",
    type=int,
    default=2,
)
parser.add_argument(
    "--period",
    type=float,
    default=0.1,
)
parser.add_argument(
    "--position_threshold",
    type=float,
    default=0.8,
)
parser.add_argument(
    "--source",
    type=str,
    default="",
)
parser.add_argument(
    "--visualize",
    type=int,
    default=0,
    help="0|1",
)
args = parser.parse_args()

success = False
if args.task == "find":
    if args.kind not in "object,filename".split(","):
        logger.error(f"-{NAME}: find: {args.kind}: kind not found.")
        success = False
    else:
        success, _ = find(
            args.source,
            in_object=args.kind == "object",
            filename=args.filename,
            visualize=args.visualize,
        )
elif args.task == "track":
    success = track(
        args.source,
        args.destination,
        crop=args.crop,
        missing_frames=args.missing_frames,
        period=args.period,
        visualize=args.visualize,
        # for match()
        area_threshold=args.area_threshold,
        position_threshold=args.position_threshold,
    )
else:
    logger.error(f"-{NAME}: {args.task}: command not found.")

if not success:
    logger.error(f"-{NAME}: {args.task}: failed.")
