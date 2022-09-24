import argparse
import cv2
from matplotlib import cm
import numpy as np
import os
import time
from tqdm import *
from abcli import file
from abcli import path
from abcli import string
from abcli.modules import host
from abcli.modules import objects
from abcli.plugins import graphics
from . import NAME
import abcli.logging
import logging

logger = logging.getLogger(__name__)

abcli_object_root = os.getenv("abcli_object_root", "")


def find(
    source,
    in_object=False,
    filename="",
    sign=True,
    visualize=False,
):

    from mtcnn import MTCNN

    logger.info(
        "{}.find({}{})".format(
            NAME,
            source,
            "/{}".format(frame if str(frame) else ""),
        )
    )

    list_of_images = (
        [
            filename_
            for filename_ in file.list_of(
                os.path.join(abcli_object_root, source, "*.jpg")
            )
            if file.name(filename_) == filename or not filename
        ]
        if in_object
        else [source]
    )

    logger.info(f"{NAME}.find: {len(list_of_images)} image(s)")

    detector = MTCNN()
    error_images = []
    output = []
    for filename_ in tqdm(list_of_images):
        success_, image = file.load_image(filename_)
        if not success_:
            error_images += [filename_]
            output += [{}]
            continue

        elapsed_time = time.time()
        list_of_faces = detector.detect_faces(image)
        elapsed_time = time.time() - elapsed_time

        info = {"elapsed_time": elapsed_time, "faces": list_of_faces}

        file.save_json(
            os.path.join(file.path(filename_), "face_finder.json"),
            info,
        )
        output += [info]

        logger.info(f"{NAME} found {len(list_of_faces)} face(s) in {filename_}.")

        if visualize:
            image = image.copy()
            for face in list_of_faces:
                image = render(image, face)

            if sign:
                image = sign(
                    image,
                    [
                        f"{len(list_of_faces)} face(s)",
                        "took {}".format(
                            string.pretty_duration(
                                elapsed_time,
                                largest=True,
                                include_ms=True,
                                short=True,
                            )
                        ),
                    ],
                    {"frame": path.name(file.path(filename_))},
                )

            file.save_image(
                os.path.join(file.path(filename_), "info.jpg"),
                image,
            )

    if error_images:
        logger.info(
            "{}.find({}): {} error(s): {}".format(
                NAME,
                source,
                len(error_images),
                ",".join(error_images),
            )
        )

    return True, output


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

    cv2.rectangle(image, (x, y), (x + width, y + height), options["color"], 2)
    graphics.add_label(
        image, x + width, y + height, "{:.2f}".format(face["confidence"])
    )

    for location in face["keypoints"].values():
        cv2.circle(image, location, radius=4, color=3 * (0,), thickness=-1)
        cv2.circle(image, location, radius=2, color=options["color"], thickness=-1)

    if face.get("id", -1) != -1:
        graphics.add_label(image, x, y, "#{}".format(face["id"]))

    return image


def track(
    source,
    destination,
    crop=False,
    missing_frames=2,
    period=0.1,
    visualize=False,
):
    list_of_frames = objects.list_of_frames(source, "name,str")
    logger.info(
        "{}.track({}->{}): {} frame(s) {}".format(
            NAME,
            source,
            destination,
            len(list_of_frames),
            " ".join(
                (["+crop"] if crop else []) + (["+visualize"] if visualize else [])
            ),
        )
    )

    if not list_of_frames:
        return True

    count = 0
    elapsed_time = 0
    face_count = 0
    output = {"frames": {}}
    face_id = -1
    background = None
    foreground = None
    error_frames = []
    for frame in tqdm(list_of_frames):
        if visualize:
            success_, image = file.load_image(
                os.path.join(abcli_object_root, source, "Data", frame, "camera.jpg")
            )
            if not success_:
                error_frames += [frame]
                continue

        if visualize:
            if background is None:
                background = np.zeros_like(image).astype(np.float32)
                foreground = np.zeros_like(image).astype(np.float32)

            background = background + image.astype(np.float32)

        success_, info = file.load_json(
            os.path.join(abcli_object_root, source, "Data", frame, "face_finder.json")
        )
        if not success_:
            error_frames += [frame]
            continue

        if visualize:
            for face in info["faces"]:
                x, y, width, height = face["box"]
                foreground[y : y + height, x : x + width, :] = image[
                    y : y + height, x : x + width, :
                ]

        logger.info("tracking frame #{}: {} face(s)".format(frame, len(info["faces"])))
        used_face_ids = []
        for index in range(len(info["faces"])):
            face_id_ = -1
            list_of_frames_ = [
                str(frame_)
                for frame_ in range(int(frame) - missing_frames, int(frame))
                if str(frame_) in output["frames"]
            ]
            logger.debug(
                "tracking frame #{}/face #{}: {}".format(
                    frame,
                    index,
                    ",".join(["#{}".format(frame_) for frame_ in list_of_frames_]),
                )
            )

            for frame_ in list_of_frames_:
                for index_, face_ in enumerate(output["frames"][frame_]["faces"]):
                    if (
                        match(info["faces"][index], face_, options)
                        and face_.get("id", -1) not in used_face_ids
                        and face_.get("id", -1) != -1
                    ):
                        face_id_ = face_["id"]
                        used_face_ids += [face_id_]
                        logger.info(
                            "frame #{}/face #{} -{}-> frame #{}/face #{}".format(
                                frame, index, face_id_, frame_, index_
                            )
                        )
                        break

                if face_id_ != -1:
                    break

            if face_id_ == -1:
                face_id += 1
                face_id_ = face_id
                logger.info("trace #{} added.".format(face_id))

            info["faces"][index]["id"] = face_id_

        output["frames"][frame] = info

        face_id_values = ["#{}".format(face["id"]) for face in info["faces"]]
        logger.error(
            "face_finder.track(frame #{}): {}".format(frame, ",".join(face_id_values))
        )
        if len(set(face_id_values)) != len(face_id_values):
            logger.error(
                "face_finder.track(frame #{}): duplicate id found.".format(frame)
            )
            return False

        elapsed_time += info["elapsed_time"]
        face_count += len(info["faces"])
        count += 1

    if count:
        if background is not None:
            background = (background / count).astype(np.uint8)
        elapsed_time = elapsed_time / count

    if error_frames:
        logger.info(
            "face_finder.track({}): {} error(s): {}".format(
                source, len(error_frames), ",".join(error_frames)
            )
        )

    output["last_face_id"] = face_id
    logger.info("{} face(s) -> {} trace(s)".format(face_count, face_id + 1))

    if (visualize or crop) and face_id >= 0:
        colormap = cm.get_cmap("Blues", face_id + 1)

        for frame in output["frames"]:
            if crop:
                success_, image = file.load_image(
                    os.path.join(abcli_object_root, source, "Data", frame, "camera.jpg")
                )
                if not success_:
                    continue

            for face in output["frames"][frame]["faces"]:
                if visualize:
                    foreground = render(
                        foreground,
                        face,
                        {
                            "color": [
                                255 * value
                                for value in colormap(face["id"] / (face_id + 1))[:3]
                            ]
                        },
                    )

                if crop:
                    x, y, width, height = face["box"]
                    file.save_image(
                        os.path.join(
                            abcli_object_root,
                            destination,
                            "Data",
                            str(face["id"] + 1),
                            "face_{:05d}.jpg".format(int(frame)),
                        ),
                        image[y : y + height, x : x + width, :],
                    )

    if visualize:
        logger.info("combining faces")
        for face_id in tqdm(objects.list_of_frames(destination, "name")):
            if not face_id:
                continue

            file.save_image(
                os.path.join(
                    objects.path_of(destination), "Data", str(face_id), "info.jpg"
                ),
                sign(
                    graphics.combine_images(
                        [
                            filename
                            for filename in file.list_of(
                                os.path.join(
                                    objects.path_of(destination),
                                    "Data",
                                    str(face_id),
                                    "*.jpg",
                                )
                            )
                            if file.name(filename).startswith("face_")
                        ]
                    ),
                    [
                        "{} frames(s)".format(len(list_of_frames)),
                        "{} face(s)".format(face_count),
                        "{} trace(s)".format(output["last_face_id"] + 1),
                        "face_id: {}".format(int(face_id) - 1),
                        "took {} / frame".format(
                            string.pretty_duration(
                                elapsed_time,
                                largest=True,
                                include_ms=True,
                                short=True,
                            )
                        ),
                    ],
                    {"frame": face_id},
                ),
            )

    if visualize:
        file.save_image(
            os.path.join(abcli_object_root, destination, "Data", "0", "info.jpg"),
            sign(
                foreground,
                [
                    "{} frames(s)".format(len(list_of_frames)),
                    "{} face(s)".format(face_count),
                    "{} trace(s)".format(output["last_face_id"] + 1),
                    "took {} / frame".format(
                        string.pretty_duration(
                            elapsed_time,
                            largest=True,
                            include_ms=True,
                            short=True,
                        )
                    ),
                ],
            ),
        )

        file.save_image(
            os.path.join(abcli_object_root, destination, "Data", "0", "background.jpg"),
            background,
        )

    output["traces"] = {}
    for face_id in range(output["last_face_id"] + 1):
        first_frame = 9999999
        last_frame = 0
        x0 = 9999999
        y0 = 9999999
        x1 = 0
        y1 = 0
        for frame in output["frames"]:
            for face in output["frames"][frame]["faces"]:
                if face["id"] == face_id:
                    first_frame = min(int(frame), first_frame)
                    last_frame = max(int(frame), last_frame)

                    x, y, width, height = face["box"]
                    x0 = min(x0, x)
                    y0 = min(y0, y)
                    x1 = max(x1, x + width - 1)
                    y1 = max(y1, y + height - 1)

        output["traces"][face_id] = {
            "first_frame": first_frame,
            "start_time": round(first_frame * period, 3),
            "last_frame": last_frame,
            "end_time": round(last_frame * period, 3),
            "frame_count": last_frame - first_frame + 1,
            "duration": round((last_frame - first_frame + 1) * period, 3),
            "box": (x0, y0, x1 - x0 + 1, y1 - y0 + 1),
        }

    file.save_json(
        os.path.join(abcli_object_root, destination, "Data", "0", "face_finder.json"),
        output,
    )

    return True


def sign(image, content=[], options=""):
    options = Options(options).default("frame", None)
    return graphics.add_signature(
        image,
        [
            " | ".join(host.signature()),
            " | ".join(objects.signature(frame)),
        ],
        [
            " | ".join(
                ["face_finder", "MTCNN", string.pretty_size_of_matrix(image)] + content
            )
        ],
    )
