#! /usr/bin/env bash

function abcli_Kanata_render() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata render$ABCUL[<video_length>]" \
            "render a video."
        return
    fi

    local video_length=$(abcli_arg_clarify $1 1)
    let "frame_count = $KANATA_FPS * $video_length" 

    local options=$(abcli_unpack_keyword $2)
    local do_validate=$(abcli_option_int "$options" validate 0)

    local extra_args=""
    if [ "$do_validate" == "1" ] ; then
        local extra_args="--occupancy -1"
    fi

    abcli_log "Kanata.render($video_length s): $frame_count frame(s) - validate:$do_validate"

    abcli_select

    python3 -m Kanata \
        render \
        --frame_count $frame_count \
        $extra_args \
        ${@:4}

    if [ "$do_validate" == "0" ] ; then
        abcli_tag set \
            $abcli_object_name \
            Kanata_render
    fi

    abcli_create_video \
        info.jpg \
        info \
        fps=$KANATA_FPS

    abcli_upload open

    abcli_publish \
        $abcli_object_name \
        info.mp4
}