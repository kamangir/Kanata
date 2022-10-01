import argparse
import json
from . import *
import abcli.logging
import logging

logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    default="",
    help="update",
)
parser.add_argument(
    "--content",
    type=str,
)
parser.add_argument(
    "--is_json",
    type=int,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--object_path",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "update":
    if args.is_json:
        success = update_metadata(
            args.keyword,
            json.loads(args.content) if args.is_json else args.content,
            args.object_path,
        )
else:
    logger.error(f"-{NAME}: {args.task}: command not found.")

if not success:
    logger.error(f"-{NAME}: {args.task}: failed.")
