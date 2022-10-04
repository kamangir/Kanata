#! /usr/bin/env bash

function abcli_Kanata_validate() {
    local task=$(abcli_unpack_keyword $1 all)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "Kanata validate$ABCUL[all|extract_faces|ingest|register|render|slice]" \
            "validate Kanata."
        return
    fi

    if [ "$task" == "all" ] ; then
        abcli_Kanata_validate extract_faces
        abcli_Kanata_validate ingest
        abcli_Kanata_validate render
        abcli_Kanata_validate slice
        return
    fi

    if [ "$task" == "extract_faces" ] ; then
        Kanata extract_faces \
            7AKXh0CrNXo \
            frame_count=42,start_time=2.0,visualize
        return
    fi

    if [ "$task" == "ingest" ] ; then
        Kanata_ingest \
            7AKXh0CrNXo \
            - \
            --frame_count 42 \
            --start_time 2.0
        return
    fi

    if [ "$task" == "register" ] ; then
        Kanata register \
            7AKXh0CrNXo
        return
    fi

    if [ "$task" == "render" ] ; then
        # ...
        return
    fi

    if [ "$task" == "slice" ] ; then
        # ...
        return
    fi

    abcli_log_error "-Kanata: validate: $task: command not found."
}