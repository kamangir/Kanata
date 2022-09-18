#! /usr/bin/env bash

function abcli_graphics_video_to_frames()
{
    python3 -m Kanata.graphics \
        video_to_frames \
        --filename "$1" \
        --destination $abcli_object_root/$(abcli_clarify_object $2 .) \
        ${@:3}
}