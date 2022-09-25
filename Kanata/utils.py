import os.path
from abcli import file
from abcli import string
from abcli.modules import objects
from abcli.modules import host
from abcli.plugins import graphics
from abcli.plugins.storage import instance as storage
from . import NAME
from .consts import *
from .video import Video
import abcli.logging
import logging

logger = logging.getLogger(__name__)


def render(
    job_id,
    frame_count=120,
    cols=12,
    rows=6,
    image_height=1600,
    image_width=2560,
    **kwargs,
):

    logger.info(
        f"{NAME}.render({objects.abcli_object_name}): {image_height}x{image_width}"
    )

    video = Video(cols, rows, frame_count, **kwargs)

    if not video.ingest():
        return False

    if not video.save_composition(
        os.path.join(
            os.getenv("abcli_object_path", ""),
            "composition.json",
        )
    ):
        return False

    return video.render(image_height, image_width)


def add_signature(
    image,
    job_id,
    content=[],
    filename=None,
):
    return graphics.add_signature(
        image,
        [
            " | ".join(host.signature()),
            " | ".join(objects.signature(file.name(filename))),
        ],
        [
            " | ".join(
                [
                    f"Kanata ({job_id})",
                    string.pretty_shape_of_matrix(image),
                ]
                + content
                + [
                    "{} x {} ".format(
                        string.pretty_duration(
                            KANATA_SLICE,
                            short=True,
                        ),
                        "{:.1f} fps".format(1 / KANATA_PERIOD),
                    ),
                    "MTCNN",
                ]
            )
        ],
    )


def skew_as_string(skew):
    return f"-{skew:.02f}->" if skew > 0 else f"<-{skew:.02f}-" if skew < 0 else ">-<"
