#! /usr/bin/env bash

function abcli_graphics_video_to_frames()
{
    local task=$(abcli_unpack_keyword $1 help)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "abcli graphics video_to_frames <path/video.mp4> <object-name> [<args>]" \
            "convert <path/video.mp4> to frames in <object-name>."

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m Kanata.graphics --help
        fi

        return
    fi

    python3 -m Kanata.graphics \
        video_to_frames \
        --filename "$1" \
        --destination $abcli_object_root/$(abcli_clarify_object $2 .) \
        ${@:3}
}