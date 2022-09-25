import argparse
from blue_worker import jobs
from . import *
from .consts import *
import abcli.logging
import logging

logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(NAME, description=f"{NAME}-{VERSION:.2f}")
parser.add_argument(
    "task",
    type=str,
    default="",
    help="render|status",
)
parser.add_argument(
    "--cols",
    type=int,
    default=12,
)
parser.add_argument(
    "--density",
    type=float,
    default=0.5,
)
parser.add_argument(
    "--frame_count",
    type=int,
    default=120,
)
parser.add_argument(
    "--image_height",
    type=int,
    default=1600,
)
parser.add_argument(
    "--image_width",
    type=int,
    default=2560,
)
parser.add_argument(
    "--job_id",
    type=str,
    default="Kanata",
)
parser.add_argument(
    "--max_asset_count",
    type=int,
    default=-1,
)
parser.add_argument(
    "--min_frame_count",
    type=int,
    default=10,
)
parser.add_argument(
    "--occupancy",
    type=float,
    default=0.9,
)
parser.add_argument(
    "--rows",
    type=int,
    default=6,
)
parser.add_argument(
    "--skew",
    type=float,
    default=0.2,
)
parser.add_argument(
    "--smooth",
    type=int,
    default=0,
    help="0|1",
)
args = parser.parse_args()

success = False
if args.task == "render":
    success = render(
        job_id=args.job_id,
        cols=args.cols,
        density=args.density,
        frame_count=args.frame_count,
        image_height=args.image_height,
        image_width=args.image_width,
        max_asset_count=args.max_asset_count,
        min_frame_count=args.min_frame_count,
        occupancy=args.occupancy,
        rows=args.rows,
        skew=args.skew,
        smooth=args.smooth,
    )
elif args.task == "status":
    print(
        "video_id: {}".format(
            jobs.flow(
                "Kanata_video_id_{}".format(args.job_id),
                "Kanata_worker",
                html=False,
            )
        )
    )
    print(
        "slice: {}".format(
            jobs.flow(
                "Kanata_slice_{},work".format(args.job_id),
                "",
                html=False,
            )
        )
    )
    print(
        "faces: {}".format(
            jobs.state(
                "Kanata_slice_{},face_finder,track".format(args.job_id),
                html=False,
            )
        )
    )

    success = True
else:
    logger.error(f"-{NAME}: {args.task}: command not found.")

if not success:
    logger.error(f"-{NAME}: {args.task}: failed.")
