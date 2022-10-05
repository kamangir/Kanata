#! /usr/bin/env bash

function abcli_faces() {
    local task=$(abcli_unpack_keyword $1 help)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "abcli faces find  <object-name>" \
            "find faces in <object-name>."
        abcli_show_usage "abcli faces install" \
            "install faces."
        abcli_show_usage "abcli faces track <object-name>" \
            "track faces in <object-name>."

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m Kanata.algo.faces --help
        fi
        return
    fi

    if [ "$task" == "find" ] ; then
        local object_name=$(abcli_clarify_object $2 .)

        abcli_tag set \
            $object_name \
            faces,find

        abcli_download object $object_name

        abcli_log "finding faces in $object_name"

        python3 -m Kanata.algo.faces \
            find \
            --source $abcli_object_root/$object_name \
            ${@:3}

        return
    fi

    if [ "$task" == "install" ] ; then
        # https://github.com/ipazc/mtcnn
        pip install mtcnn
        return
    fi

    if [ "$task" == "track" ] ; then
        local object_name=$(abcli_clarify_object $2 .)

        abcli_download object $object_name

        abcli_relation set \
            $object_name \
            $abcli_object_name \
            produced

        abcli_log "tracking faces in $object_name"

        echo python3 -m Kanata.algo.faces \
            track \
            --source $object_name \
            --destination $abcli_object_name \
            ${@:3}

        abcli_tag set \
            $abcli_object_name\
            faces,track

        return
    fi

    abcli_log_error "-abcli: faces: $task: command not found."
}