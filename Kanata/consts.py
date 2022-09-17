import os

version = "v14"
Kanata_period = float(os.getenv("Kanata_period", "0.1"))
Kanata_output_fps = int(os.getenv("Kanata_output_fps", "10"))
Kanata_plan_video_slice_in_seconds = int(
    os.getenv("Kanata_plan_video_slice_in_seconds", "60")
)
