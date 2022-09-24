import cv2
import numpy as np
from tqdm import *
import os
from abcli import file
from abcli import string
from . import NAME
import abcli.logging
import logging

logger = logging.getLogger(__name__)

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
        "{}.video_to_frames({}:{}) -{}-@ {}-{} frame(s)-> {}".format(
            NAME,
            filename,
            string.pretty_duration(duration, short=True),
            string.pretty_duration(start_time),
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
            os.path.join(destination, f"{frame:010d}.jpg"),
            np.flip(image, axis=2),
        )

    return True
