#! /usr/bin/env bash

function abcli_youtube() {
    local task=$(abcli_unpack_keyword $1 help)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "abcli youtube browse$ABCUL<video-id>" \
            "browse youtube/?v=<video-id>."
        abcli_show_usage "abcli youtube cat$ABCUL<video-id>" \
            "cat info re youtube/?v=<video-id>."
        abcli_show_usage "abcli youtube download$ABCUL<video-id>" \
            "download youtube/?v=<video-id>."
        abcli_show_usage "abcli youtube duration$ABCUL<video-id>" \
            "print duration of youtube/?v=<video-id>."
        abcli_show_usage "abcli youtube install" \
            "install youtube."
        abcli_show_usage "abcli youtube is_CC$ABCUL<video-id-1,video-id-2>" \
            "<True|False,True|False>."
        abcli_show_usage "abcli youtube search$ABCUL<keyword>" \
            "search in youtube for <keyword>."
        abcli_show_usage "abcli youtube upload$ABCUL<path/filename.mp4>" \
            "upload path/filename.mp4 to youtube and read metadata from path/filename.json."
        abcli_show_usage "abcli youtube validate" \
            "validate youtube."

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m Kanata.youtube --help
        fi
        return
    fi

    if [ "$task" == "browse" ] ; then
        local video_id=$2
        local url="https://www.youtube.com/watch?v=$video_id"
        abcli_browse_url $url
        return
    fi

    if [ "$task" == "is_CC" ] ; then
        python3 -m Kanata.youtube \
            is_CC \
            --video_id "$2" \
            ${@:3}
        return
    fi

    if [ "$(abcli_list_in $task cat,download,duration)" == "True" ] ; then
        local video_id=$2

        abcli_log "youtube.$task: $video_id"

        python3 -m Kanata.youtube \
            $task \
            --video_id "$video_id" \
            ${@:3}

        if [ "$task" == "download" ] ; then
            abcli_tag set \
                $abcli_object_name \
                youtube_download

            abcli_relation set \
                $video_id \
                $abcli_object_name \
                is-downloaded-in
        fi

        return
    fi

    if [ "$task" == "search" ] ; then
        python3 -m Kanata.youtube \
            search \
            --keyword "$2" \
            ${@:3}
        return
    fi

    if [ "$task" == "install" ] ; then
        # https://medium.com/daily-python/python-script-to-search-content-using-youtube-data-api-daily-python-8-1084776a6578
        pip install google-api-python-client

        # https://medium.com/@sonawaneajinks/python-script-to-download-youtube-videos-daily-python-6-c3788be5b6b1
        pip install pytube

        # https://stackoverflow.com/a/16743442/17619982
        pip install isodate

        return
    fi

    if [ "$task" == "upload" ] ; then
        python3 -m Kanata.youtube \
            upload \
            --filename "$2" \
            ${@:3}
        return
    fi

    if [ "$task" == "validate" ] ; then
        python3 -m Kanata.youtube \
            validate \
            ${@:2}
        return
    fi

    abcli_log_error "-Kanata: youtube: $task: command not found."
}