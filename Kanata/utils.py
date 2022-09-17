import numpy as np
import os.path
from tqdm import *

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


# https://stackoverflow.com/a/47632941/17619982
def video_to_frames(
    filename,
    destination,
    frame_count=-1,
    period=1.0,
    start_time=0.0,
):
    vidcap = cv2.VideoCapture(filename)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    total_frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frame_count / fps

    frame_count = (
        frame_count if frame_count != -1 else int((duration - start_time) / period)
    )

    logger.info(
        "graphics.video_to_frames({}:{}) -{}-@ {}-{} frame(s)-> {}".format(
            filename,
            string.pretty_time(duration, "short"),
            string.pretty_time(start_time),
            string.pretty_frequency(1.0 / period),
            frame_count,
            destination,
        )
    )

    vidcap.read()
    for frame in tqdm(range(frame_count)):
        vidcap.set(
            cv2.CAP_PROP_POS_MSEC,
            (start_time + frame * period) * 1000,
        )
        success, image = vidcap.read()
        if not success:
            break

        file.save_image(
            os.path.join(destination, "Data", str(frame), "camera.jpg"),
            np.flip(image, axis=2),
        )

    return True
