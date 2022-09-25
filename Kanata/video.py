import numpy as np
import os.path
import random
from abcli import file
from abcli.modules import objects
from abcli.plugins.storage import instance as storage
from abcli.plugins import relations
from abcli.plugins import tags
from . import *
from .utils import *
import abcli.logging
import logging

logger = logging.getLogger(__name__)


class Video(object):
    def __init__(
        self,
        job_id,
        cols,
        rows,
        frame_count,
        density=0.5,
        log=False,
        max_object_count=-1,
        min_frame_count=10,
        occupancy=0.9,
        skew=0.0,
        smooth=0,
    ):
        logger.info(f"{NAME}.Video({job_id}): {frame_count}x{rows}x{cols}")

        self.job_id = job_id
        self.density = density
        self.log = log
        self.max_object_count = max_object_count
        self.min_frame_count = min_frame_count
        self.occupancy = occupancy
        self.skew = skew
        self.smooth = smooth

        self.composition = [
            [[None for _ in range(cols)] for _ in range(rows)]
            for _ in range(frame_count)
        ]

        self.object_count = 0

    @property
    def cols(self):
        return len(self.composition[0][0])

    @property
    def frame_count(self):
        return len(self.composition)

    def ingest(self):
        logger.info(
            "video.ingest: {}{}{}".format(
                "<={} object(s) ".format(self.max_object_count)
                if self.max_object_count != -1
                else "",
                ">{:.2f} ".format(self.occupancy) if self.occupancy != -1 else "",
                skew_as_string(self.skew),
            )
        )

        complete = False
        self.object_count = 0
        ran_out = False
        while not complete:
            if (
                self.max_object_count != -1
                and self.object_count >= self.max_object_count
            ):
                logger.info(
                    "video.ingest() max object count {} reached.".format(
                        self.object_count
                    )
                )
                ran_out = True
                break

            object = tags.search(
                [
                    "~used_for_{}".format(objects.abcli_object_name),
                    "Kanata_slice_{}".format(job_id),
                    "face_finder",
                    "track",
                ],
                "count=1",
            )
            if not object:
                logger.info("video.ingest() ran out of slices.")
                ran_out = True
                break
            self.object_count += 1

            if not storage.download_file(
                storage.bucket_name,
                "abcli/{}/Data/0/face_finder.json".format(object),
                "object",
                "~errordump",
            ):
                continue

            relations.set_(objects.abcli_object_name, object, "used")
            tags.set_(object, "used_for_{}".format(objects.abcli_object_name))

            success, info = file.load_json(
                os.path.join(
                    objects.abcli_object_root_folder, object, "Data/0/face_finder.json"
                )
            )
            if not success:
                continue
            logger.info("{}: {} face(s) found.".format(object, len(info["traces"])))

            for face_id in info["traces"]:
                if info["traces"][face_id]["frame_count"] < self.min_frame_count:
                    continue

                found_None = False
                for frame in range(self.frame_count):
                    for row in range(self.rows):
                        for col in range(self.cols):
                            if self.composition[frame][row][col] is None:
                                if random.random() >= self.density:
                                    self.composition[frame][row][col] = "skip"
                                    if self.log:
                                        logger.info(
                                            "video.render({},{},{}): skip".format(
                                                frame, row, col
                                            )
                                        )
                                    continue

                                frame_ = frame
                                row_ = row
                                col_ = col
                                found_None = True
                                break
                        if found_None:
                            break
                    if found_None:
                        break

                if not found_None:
                    logger.info("composition is complete")
                    complete = True
                    break
                if self.log:
                    logger.info("video.ingest({},{},{})".format(frame_, row_, col_))

                index = info["traces"][face_id]["first_frame"]
                skew_counter = 0
                while True:
                    if self.log:
                        logger.info(
                            "video.ingest[{},{},{}]: {}/face_id={}/{}".format(
                                frame_,
                                row_,
                                col_,
                                object,
                                face_id,
                                index,
                            )
                        )
                    self.composition[frame_][row_][col_] = (
                        object,
                        face_id,
                        index,
                    )

                    index += 1
                    frame_ += 1

                    if index > info["traces"][face_id]["last_frame"]:
                        if self.skew == 0:
                            break
                        index = info["traces"][face_id]["first_frame"]
                    if frame_ >= self.frame_count:
                        break

                    skew_counter += 1
                    if abs(skew_counter * self.skew) >= 1:
                        if self.skew < 0:
                            col_ -= 1
                            if col_ < 0:
                                break
                        if self.skew > 0:
                            col_ += 1
                            if col_ >= self.cols:
                                break
                        skew_counter = 0

        if ran_out:
            logger.info("video.ingest(): cropping composition.")
            frame = self.frame_count - 1
            while True:
                occupancy = float(
                    np.mean(
                        np.array(
                            [
                                float(
                                    np.mean(
                                        np.array(
                                            [
                                                int(
                                                    self.composition[frame][row][col]
                                                    is not None
                                                )
                                                for col in range(self.cols)
                                            ]
                                        )
                                    )
                                )
                                for row in range(self.rows)
                            ]
                        )
                    )
                )
                if occupancy >= self.occupancy:
                    break

                frame -= 1
                if frame < 0:
                    break

            logger.info(
                "video.render(occupancy={:.02f}) cropping at {}/{} - {:.02f}.".format(
                    self.occupancy, frame + 1, self.frame_count, occupancy
                )
            )
            self.frame_count = frame + 1
            self.composition = [
                self.composition[frame] for frame in range(self.frame_count)
            ]

        return True

    def render(self, image_height, image_width):
        from abcli.storage import instance as storage

        face_height = int(math.floor(image_height / self.rows))
        face_width = int(math.floor(image_width / self.cols))

        logger.info(
            "video.render: {}x{} -> {}x{}x{}{}".format(
                face_height,
                face_width,
                self.frame_count,
                image_height,
                image_width,
                " smooth" if self.smooth else "",
            )
        )

        for frame in tqdm(range(self.frame_count)):
            if self.log:
                logger.info("video.render({}/{})".format(frame, self.frame_count))

            image = np.zeros((image_height, image_width, 3), dtype=np.uint8)

            for col in range(self.cols):
                for row in range(self.rows):
                    if self.composition[frame][row][col] not in [None, "skip"]:
                        object, face_id, index = self.composition[frame][row][col]

                        if not storage.download_file(
                            storage.bucket_name,
                            "abcli/{}/Data/{}/face_{:05d}.jpg".format(
                                object, int(face_id) + 1, index
                            ),
                            "object",
                            "~errordump,~log",
                        ):
                            continue

                        success_, image_ = file.load_image(
                            os.path.join(
                                objects.abcli_object_root_folder,
                                "{}/Data/{}/face_{:05d}.jpg".format(
                                    object, int(face_id) + 1, index
                                ),
                            )
                        )
                        if not success_:
                            continue

                        factor = min(
                            face_height / image_.shape[0],
                            face_width / image_.shape[1],
                        )
                        image_ = cv2.resize(
                            image_,
                            dsize=(
                                int(factor * image_.shape[1]),
                                int(factor * image_.shape[0]),
                            ),
                            interpolation=cv2.INTER_AREA,
                        )

                        dy = int((face_height - image_.shape[0]) / 2)
                        dx = int((face_width - image_.shape[1]) / 2)

                        image__ = np.zeros(
                            (face_height, face_width, 3),
                            dtype=np.uint8,
                        )
                        image__[
                            dy : dy + image_.shape[0], dx : dx + image_.shape[1], :
                        ] = image_

                        image[
                            row * face_height : (row + 1) * face_height,
                            col * face_width : (col + 1) * face_width,
                            :,
                        ] = image__

            file.save_image(
                os.path.join(
                    os.getenv("abcli_object_path", ""),
                    "info.jpg",
                ),
                add_signature(
                    image,
                    [
                        string.pretty_duration(self.frame_count / KANATA_FPS),
                        "{} object(s)".format(self.object_count),
                        "{}x{} x {}x{}".format(
                            self.rows, self.cols, face_height, face_width
                        ),
                        "{:.0f} %".format(self.density * 100),
                        skew_as_string(self.skew),
                    ]
                    + (["smooth"] if self.smooth else []),
                    filename=filename,
                ),
            )

    @property
    def rows(self):
        return len(self.composition[0])

    def save_composition(self, filename):
        return file.save_json(filename, self.composition)
