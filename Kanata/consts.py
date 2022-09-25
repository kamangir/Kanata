import os

KANATA_PERIOD = float(os.getenv("KANATA_PERIOD", "0.1"))
KANATA_FPS = int(os.getenv("KANATA_FPS", "10"))
KANATA_SLICE = int(os.getenv("KANATA_SLICE", "60"))
