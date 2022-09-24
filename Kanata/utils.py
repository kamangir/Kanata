import os.path
from abcli import file
from abcli import string
from abcli.modules import objects
from abcli.modules import host
from abcli.plugins import graphics
from abcli.plugins.storage import instance as storage
from . import version, NAME
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
        f"{NAME}.render({objects.abcli_object_name}): {image_height}x{image_width}"
    )

    video = Video(cols, rows, frame_count)

    if not video.ingest():
        return False

    if not video.save_composition(
        os.path.join(objects.abcli_object_folder, "composition.json")
    ):
        return False

    return video.render(image_height, image_width)


def add_signature(image, content=[], filename=None):
    return graphics.add_signature(
        image,
        [
            " | ".join(host.signature()),
            " | ".join(objects.signature(file.name(filename))),
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
