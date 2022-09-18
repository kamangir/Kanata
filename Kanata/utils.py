import os.path
from abcli import assets
from abcli import graphics
from abcli import host
from abcli import string
from abcli.plugins.storage import instance as storage
from . import version
from .consts import *
from .video import Video
import abcli.logging
import logging

logger = logging.getLogger(__name__)


def render(
    frame_count=120,
    cols=12,
    rows=6,
    image_height=1600,
    image_width=2560,
):

    logger.info(
        "Kanata.render({}): {}x{}".format(
            assets.abcli_asset_name, image_height, image_width
        )
    )

    video = Video(cols, rows, frame_count)

    if not video.ingest():
        return False

    if not video.save_composition(
        os.path.join(assets.abcli_asset_folder, "composition.json")
    ):
        return False

    return video.render(image_height, image_width)


def sign(image, content=[], frame=None):
    return graphics.add_signature(
        image,
        [
            " | ".join(host.signature()),
            " | ".join(assets.signature(frame)),
        ],
        [
            " | ".join(
                [
                    f"Kanata ({version})",
                    string.pretty_shape_of_matrix(image),
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
