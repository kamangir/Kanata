import argparse
from abcli.plugins import jobs
from . import *
import abcli.logging
import logging

logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser("Kanata", description="Kanata-{:.2f}".format(VERSION))
parser.add_argument(
    "task",
    type=str,
    default="",
    help="get_version,render,status",
)
parser.add_argument(
    "--cols",
    type=int,
    default=12,
    help="",
)
parser.add_argument(
    "--density",
    type=float,
    default=0.5,
    help="",
)
parser.add_argument(
    "--frame_count",
    type=int,
    default=120,
    help="",
)
parser.add_argument(
    "--image_height",
    type=int,
    default=1600,
    help="",
)
parser.add_argument(
    "--image_width",
    type=int,
    default=2560,
    help="",
)
parser.add_argument(
    "--max_asset_count",
    type=int,
    default=-1,
    help="",
)
parser.add_argument(
    "--min_frame_count",
    type=int,
    default=10,
    help="",
)
parser.add_argument(
    "--occupancy",
    type=float,
    default=0.9,
    help="",
)
parser.add_argument(
    "--rows",
    type=int,
    default=6,
    help="",
)
parser.add_argument(
    "--skew",
    type=float,
    default=0.2,
    help="",
)
parser.add_argument(
    "--smooth",
    type=int,
    default=0,
    help="0/1",
)
args = parser.parse_args()

success = False
if args.task == "get_version":
    success = True
    print(version)
elif args.task == "render":
    success = render(
        {
            "cols": args.cols,
            "density": args.density,
            "frame_count": args.frame_count,
            "image_height": args.image_height,
            "image_width": args.image_width,
            "max_asset_count": args.max_asset_count,
            "min_frame_count": args.min_frame_count,
            "occupancy": args.occupancy,
            "rows": args.rows,
            "skew": args.skew,
            "smooth": args.smooth,
        }
    )
elif args.task == "status":
    print("version: {}".format(version))
    print(
        "video_id: {}".format(
            jobs.flow("Kanata_video_id_{}".format(version), "Kanata_worker", "~html")
        )
    )
    print(
        "slice: {}".format(
            jobs.flow("Kanata_slice_{},work".format(version), "", "~html")
        )
    )
    print(
        "faces: {}".format(
            jobs.state("Kanata_slice_{},face_finder,track".format(version), "~html")
        )
    )

    success = True
else:
    logger.error('Kanata: unknown task "{}".'.format(args.task))

if not success:
    logger.error("Kanata({}): failed.".format(args.task))