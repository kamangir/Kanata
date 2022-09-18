#! /usr/bin/env bash

function abcli_graphics_video_to_frames()
{
    local filename=$1
    local destination=$(abcli_clarify_object $2)
    local options=$3
    local frame_count=$(abcli_option "$options" open -1)
    local period=$(abcli_option "$options" open 1.0)
    local start_time=$(abcli_option "$options" open 0.0)

    python3 -m Kanata.graphics \
        video_to_frames \
        TBA \
        ${@:4}
}