import copy
import os
import os.path
from abcli import file
from abcli import logging
import logging

logger = logging.getLogger(__name__)

NAME = "Kanata.metadata"


def update_metadata(keyword, content):
    filename = os.path.join(os.getenv("abcli_object_path", ""), "metadata.json")

    _, metadata = file.load_json(filename, civilized=True)

    metadata[keyword] = copy.deepcopy(content)

    logger.info(f"{NAME}.update_metadata({keyword}: {content})")

    return file.save_json(filename, metadata)
