#! /usr/bin/env bash

function Kanata_session() {
    local task=$(abcli_unpack_keyword $1 help)

    if [ "$task" == "start" ] ; then
        abcli_log "Kanata: session started."

        local cw_version=$(abcli_Kanata_version)
        local video_id=$(abcli_job find Kanata_worker Kanata_video_id_$cw_version)

        if [ -z "$video_id" ] ; then
            abcli_log "Kanata session found no work."
            return
        fi

        abcli_log "Kanata-worker: $video_id started."

        abcli_job $video_id started Kanata_worker
        abcli_Kanata slice $video_id
        abcli_job $video_id completed Kanata_worker

        abcli_log "Kanata: session ended."
        return
    fi

    abcli_log_error "-Kanata: session: $task: command not found."
}