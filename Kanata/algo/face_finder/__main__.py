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
    "--area_score",
    type=float,
    default=0.8,
)
parser.add_argument(
    "--crop",
    type=int,
    default=0,
    help="0/1",
)
parser.add_argument(
    "--destination",
    type=str,
    default="",
)
parser.add_argument(
    "--frame",
    type=str,
    default="",
)
parser.add_argument(
    "--kind",
    type=str,
    default="",
    help="image/asset",
)
parser.add_argument(
    "--missing_frames",
    type=int,
    default=2,
    help="",
)
parser.add_argument(
    "--period",
    type=float,
    default=0.1,
)
parser.add_argument(
    "--position_score",
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
    help="0/1",
)
args = parser.parse_args()

success = False
if args.task == "find":
    if args.kind not in "asset,filename".split(","):
        logger.error('face_finder.find(): unknown kind: "{}".'.format(args.kind))
        success = False
    else:
        success, _ = find(
            args.source,
            {
                "asset": args.kind == "asset",
                "frame": args.frame,
                "visualize": args.visualize,
            },
        )
elif args.task == "track":
    success = track(
        args.source,
        args.destination,
        {
            "area_score": args.area_score,
            "crop": args.crop,
            "missing_frames": args.missing_frames,
            "period": args.period,
            "position_score": args.position_score,
            "visualize": args.visualize,
        },
    )
else:
    logger.error('face_finder: unknown task "{}".'.format(args.task))

if not success:
    logger.error("face_finder({}): failed.".format(args.task))
