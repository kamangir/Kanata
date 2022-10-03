#! /usr/bin/env bash

function abcli_Kanata_validate() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata validate [all|extract_faces|ingest|...]" \
            "validate Kanata"
        return
    fi

    if [ "$task" == "all" ] ; then
        abcli_Kanata_validate extract_faces
        abcli_Kanata_validate ingest
        # ...
        return
    fi

    if [ "$task" == "extract_faces" ] ; then
        abcli_Kanata extract_faces \
            7AKXh0CrNXo \
            frame_count=25
        return
    fi

    if [ "$task" == "ingest" ] ; then
        # ...
        return
    fi

    abcli_log_error "-Kanata: validate: $task: command not found."
}