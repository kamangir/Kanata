#! /usr/bin/env bash

function abcli_Kanata_register() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata register$ABCUL<video_id_1,video_id_2>" \
            "register <video_id_1,video_id_2>."
        return
    fi

    local list_of_video_id=$(echo "$1" | tr , " ")

    local video_id
    for video_id in $list_of_video_id ; do
        abcli_log "Kanata.register($video_id)"

        local check=$(abcli_youtube is_CC $video_id)
        if [ "$check" != "True" ] ; then
            abcli_log_error "❗ youtube/$video_id is not licensed under Creative Commons - will not register."
            continue
        fi
        abcli_log "✅ youtube/$video_id is licensed under Creative Commons."

        abcli_tag set \
            $video_id \
            youtube_video_id \
            ${@:2}
    done
}