import copy
import os
import os.path
from abcli import file
from . import NAME
from abcli import logging
import logging

logger = logging.getLogger(__name__)


def update_metadata(
    keyword,
    content,
    object_path="",
):
    if not object_path:
        object_path = os.getenv("abcli_object_path", "")

    filename = os.path.join(object_path, "metadata.json")

    _, metadata = file.load_json(filename, civilized=True)

    metadata[keyword] = copy.deepcopy(content)

    logger.info(f"{NAME}.update_metadata[{filename}]: {keyword}={content})")

    return file.save_json(filename, metadata)
