#! /usr/bin/env bash

function abcli_Kanata_extract_faces() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata extract_faces$ABCUL<video_id>$ABCUL[stream,visualize]$ABCUL[--frame_count 42]$ABCUL[--start_time 2.0]" \
            "extract faces from <video_id>."
        return
    fi

    local video_id=$1

    local options=$2
    local do_stream=$(abcli_option_int "$options" stream 1)
    local do_visualize=$(abcli_option_int "$options" visualize 0)

    abcli_Kanata \
        ingest \
        $video_id \
        $options \
        ${@:3}

    abcli_faces \
        find \
        $abcli_object_name \
        --visualize $do_visualize

    return

    abcli_faces \
        track \
        $abcli_object_name \
        --visualize $do_visualize

    abcli_cache write $abcli_object_name.video_id $video_id

    if [ "$do_stream" == "1" ] ; then
        abcli_upload open
        abcli_message stream $abcli_object_name
    fi
}