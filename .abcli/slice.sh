#! /usr/bin/env bash

function abcli_Kanata_slice() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata slice$ABCUL[<video_id>]" \
            "slice <video_id>."
        return
    fi

    local video_id=$2

    local options="$3"
    local do_validate=$(abcli_option_int "$options" validate 0)

    abcli_select
    abcli_youtube download $video_id

    local duration=$(abcli_graphics duration_of_video --filename $abcli_object_path/video.mp4)
    let "last_slice = $duration / $KANATA_SLICE"
    if [ "$do_validate" == "1" ] ; then
        local last_slice="2"
    fi
    local frame_count=$(python -c "print(int($KANATA_SLICE/$KANATA_PERIOD))")
    abcli_log "Kanata.slice($video_id:$duration/$KANATA_SLICE): 0..$last_slice - $frame_count frame(s)"

    local options="$options,frame_count=$frame_count"

    for (( slice=0; slice<=$last_slice; slice++ ))
    do
        abcli_log "Kanata.slice($video_id:$slice/$last_slice)"

        let "start_time = $slice * $KANATA_SLICE"
        abcli_work Kanata_slice \
            "abcli_Kanata extract_faces $video_id $start_time $options"
    done
}