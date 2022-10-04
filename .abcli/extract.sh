#! /usr/bin/env bash

function abcli_Kanata_extract_faces() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata extract_faces$ABCUL<video_id>$ABCUL[frame_count=<42>,start_time=<0.0>,stream,visualize]" \
            "extract faces from <video_id>."
        return
    fi

    local video_id=$1

    local options=$2
    local do_stream=$(abcli_option_int "$options" stream 1)
    local do_visualize=$(abcli_option_int "$options" visualize 0)
    local frame_count=$(abcli_option_int "$options" frame_count -1)
    local start_time=$(abcli_option $options start_time 0.0)

    abcli_Kanata \
        ingest \
        $video_id \
        $start_time \
        $options \
        --frame_count $frame_count

    abcli_faces \
        find \
        $abcli_object_name \
        --visualize $do_visualize

    abcli_faces \
        track \
        $abcli_object_name \
        --visualize $do_visualize

    abcli_cache write $abcli_object_name.video_id $video_id
    abcli_cache write $abcli_object_name.start_time $start_time

    if [ "$do_stream" == "1" ] ; then
        abcli_upload open
        abcli_message stream $abcli_object_name
    fi
}