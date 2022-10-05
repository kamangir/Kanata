from matplotlib import cm
import numpy as np
from tqdm import tqdm
from .functions import *
from abcli import file, path
from abcli.modules import objects
import abcli.logging
import logging

logger = logging.getLogger(__name__)


def track(
    source,
    destination,
    crop=False,
    missing_frames=2,
    period=0.1,
    visualize=False,
    **kwargs,
):
    import ipdb

    ipdb.set_trace()
    list_of_files = objects.list_of_files(source)
    logger.info(
        "{}.track({}->{}): {} frame(s) {}".format(
            NAME,
            source,
            destination,
            len(list_of_files),
            " ".join(
                (["+crop"] if crop else []) + (["+visualize"] if visualize else [])
            ),
        )
    )

    if not list_of_files:
        return True

    count = 0
    elapsed_time = 0
    face_count = 0
    output = {"frames": {}}
    face_id = -1
    background = None
    foreground = None
    error_frames = []
    for frame in tqdm(list_of_files):
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
            os.path.join(abcli_object_root, source, frame, "faces.json")
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
            list_of_files_ = [
                str(frame_)
                for frame_ in range(int(frame) - missing_frames, int(frame))
                if str(frame_) in output["frames"]
            ]
            logger.debug(
                "tracking frame #{}/face #{}: {}".format(
                    frame,
                    index,
                    ",".join(["#{}".format(frame_) for frame_ in list_of_files_]),
                )
            )

            for frame_ in list_of_files_:
                for index_, face_ in enumerate(output["frames"][frame_]["faces"]):
                    if (
                        match(info["faces"][index], face_, **kwargs)
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
            "{}.track(frame #{}): {}".format(NAME, frame, ",".join(face_id_values))
        )
        if len(set(face_id_values)) != len(face_id_values):
            logger.error(f"{NAME}.track(frame #{frame}): duplicate id found.")
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
            ".track({}): {} error(s): {}".format(
                NAME, source, len(error_frames), ",".join(error_frames)
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
        for face_id in tqdm(objects.list_of_files(destination, "name")):
            if not face_id:
                continue

            file.save_image(
                os.path.join(
                    objects.path_of(destination), "Data", str(face_id), "info.jpg"
                ),
                add_signature(
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
                        "{} file(s)".format(len(list_of_files)),
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
            os.path.join(abcli_object_root, destination, "info.jpg"),
            add_signature(
                foreground,
                [
                    "{} file(s)".format(len(list_of_files)),
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
            os.path.join(abcli_object_root, destination, "background.jpg"),
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
        os.path.join(abcli_object_root, destination, f"{NAME}.json"),
        output,
    )

    return True
