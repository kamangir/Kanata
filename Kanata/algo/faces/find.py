import os
import time
from abcli import file, path
from .functions import *
from tqdm import tqdm
import abcli.logging
import logging

logger = logging.getLogger(__name__)


def find(
    source,
    sign=True,
    visualize=False,
):
    from mtcnn import MTCNN

    logger.info(f"{NAME}.find({source})")

    list_of_images = [
        filename for filename in file.list_of(os.path.join(source, "*.jpg"))
    ]

    logger.info(f"{NAME}.find: {len(list_of_images)} image(s)")

    detector = MTCNN()
    error_images = []
    output = []
    for filename in tqdm(list_of_images):
        success_, image = file.load_image(filename)
        if not success_:
            error_images += [filename]
            output += [{}]
            continue

        elapsed_time = time.time()
        list_of_faces = detector.detect_faces(image)
        elapsed_time = time.time() - elapsed_time

        info = {"elapsed_time": elapsed_time, "faces": list_of_faces}

        file.save_json(
            file.set_extension(file.add_postfix(filename, "faces"), "json"),
            info,
        )
        output += [info]

        logger.info(f"{NAME} found {len(list_of_faces)} face(s) in {filename}.")

        if visualize:
            image = image.copy()
            for face in list_of_faces:
                image = render(image, face)

            if sign:
                image = add_signature(
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
                    filename=path.name(file.path(filename)),
                )

            file.save_image(
                os.path.join(file.add_postfix(filename, "faces")),
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
