#! /usr/bin/env bash

export KANATA_PERIOD=0.1
export KANATA_FPS=10
export KANATA_SLICE=60
export Kanata_validation_video_id="7AKXh0CrNXo"

function Kanata() {
    abcli_Kanata $@
}

function abcli_Kanata() {
    local task=$(abcli_unpack_keyword $1 help)

    if [ "$task" == "help" ] ; then
        abcli_Kanata_extract_faces $@
        abcli_Kanata_ingest $@
        abcli_Kanata_register $@
        abcli_Kanata_render $@
        abcli_Kanata_slice $@

        abcli_show_usage "Kanata status" \
            "show status of Kanata."

        abcli_Kanata_validate $@

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m Kanata --help
        fi
        return
    fi

    local function="abcli_Kanata_$task"
    if [[ $(type -t $function) == "function" ]] ; then
        $function "${@:2}"
        return
    fi

    if [ "$task" == "status" ] ; then
        python3 -m Kanata \
            status \
            ${@:2}
        return
    fi

    abcli_log_error "-Kanata: $task: command not found."
}