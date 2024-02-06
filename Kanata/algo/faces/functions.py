import cv2
import os
from abcli import string
from abcli.modules import host
from abcli.modules import objects
from abcli.plugins import graphics
from . import NAME
import abcli.logging
import logging

logger = logging.getLogger(__name__)


def match(
    face_1,
    face_2,
    area_threshold=0.8,
    position_threshold=0.8,
):
    x_1, y_1, width_1, height_1 = face_1["box"]
    x_2, y_2, width_2, height_2 = face_2["box"]

    area_score = (width_1 * height_1 / width_2 / height_2) ** 0.5
    if area_score > 1.0:
        area_score = 1 / area_score

    window_size = (width_1 * height_1 * width_2 * height_2) ** 0.25
    position_score = 1.0 - ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** 0.5 / window_size

    output = area_score >= area_threshold and position_score >= position_threshold

    logger.debug(
        "{}.match: area_score={:.2f}, position_score={:.2f} -> {}".format(
            NAME,
            area_score,
            position_score,
            string.pretty_logical(output),
        )
    )

    return output


def render(image, face, color=3 * (127,)):
    x, y, width, height = face["box"]

    cv2.rectangle(image, (x, y), (x + width, y + height), color, 2)
    graphics.add_label(
        image, x + width, y + height, "{:.2f}".format(face["confidence"])
    )

    for location in face["keypoints"].values():
        cv2.circle(image, location, radius=4, color=3 * (0,), thickness=-1)
        cv2.circle(image, location, radius=2, color=color, thickness=-1)

    if face.get("id", -1) != -1:
        graphics.add_label(image, x, y, "#{}".format(face["id"]))

    return image


def add_signature(image, content=[], filename=None):
    return graphics.add_signature(
        image,
        [
            " | ".join(host.signature()),
            " | ".join(objects.signature(filename)),
        ],
        [
            " | ".join(
                [
                    NAME,
                    "MTCNN",
                    string.pretty_shape_of_matrix(image),
                ]
                + content
            ),
        ],
    )
