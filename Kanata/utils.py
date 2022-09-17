import numpy as np
import os.path
from tqdm import *

from abcli import assets
from abcli import graphics
from abcli import host
from abcli import string
from abcli.options import Options

from . import version
from .consts import *
from .video import Video

import abcli.logging
import logging

logger = logging.getLogger(__name__)


def render(options=""):
    from abcli.storage import instance as storage

    options = (
        Options(options)
        .default("frame_count", 120)
        .default("cols", 12)
        .default("rows", 6)
        .default("image_height", 1600)
        .default("image_width", 2560)
    )

    logger.info(
        "Kanata.render({}): {}x{}".format(
            assets.abcli_asset_name, options["image_height"], options["image_width"]
        )
    )

    video = Video(options["cols"], options["rows"], options["frame_count"], options)

    if not video.ingest():
        return False

    if not video.save_composition(
        os.path.join(assets.abcli_asset_folder, "composition.json")
    ):
        return False

    return video.render(options["image_height"], options["image_width"])


def sign(image, content=[], options=""):
    options = Options(options).default("frame", None)
    return graphics.add_signature(
        image,
        [
            " | ".join(host.signature()),
            " | ".join(assets.signature(options["frame"])),
        ],
        [
            " | ".join(
                [
                    "Kanata ({})".format(version),
                    string.pretty_size_of_matrix(image),
                ]
                + content
                + [
                    "{} x {} ".format(
                        string.pretty_duration(
                            Kanata_plan_video_slice_in_seconds,
                            short=True,
                        ),
                        "{:.1f} fps".format(1 / Kanata_period),
                    ),
                    "MTCNN",
                ]
            )
        ],
    )


def skew_as_string(skew):
    return f"-{skew:.02f}->" if skew > 0 else f"<-{skew:.02f}-" if skew < 0 else ">-<"
