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
    help="video_to_frames",
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
    "--frame_count",
    type=int,
    default=-1,
)
parser.add_argument(
    "--period",
    type=float,
    default=1.0,
)
parser.add_argument(
    "--start_time",
    type=float,
    default=0.0,
)
args = parser.parse_args()

success = False
if args.task == "video_to_frames":
    success = video_to_frames(
        args.filename,
        args.destination,
        args.frame_count,
        args.period,
        args.start_time,
    )
else:
    logger.error(f"-{NAME}: {args.task}: command not found.")

if not success:
    logger.error(f"-{NAME}: {args.task}: failed.")
