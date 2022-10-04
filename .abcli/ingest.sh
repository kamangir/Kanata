#! /usr/bin/env bash

function abcli_Kanata_ingest() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata ingest$ABCUL<video_id>$ABCUL[<options>]$ABCUL[--frame_count 42]$ABCUL[--start_time 2.0]" \
            "ingest <video_id>."
        return
    fi

    local video_id=$1

    local options=$2
    local start_time=$(abcli_option $options start_time 0.0)

    abcli_select
    abcli_youtube download $video_id

    abcli_select
    abcli_graphics \
        video_to_frames \
        $abcli_object_root/$abcli_object_name_prev/video.mp4 \
        $abcli_object_name \
        --period $KANATA_PERIOD \
        ${@:3}
}