#! /usr/bin/env bash

function abcli_face() {
    local task=$(abcli_unpack_keyword $1 help)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "abcli face find  <object-name>" \
            "find faces in <object-name>."
        abcli_show_usage "abcli face install" \
            "install face."
        abcli_show_usage "abcli face track <object-name>" \
            "track faces in <object-name>."

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m Kanata.algo.face --help
        fi
        return
    fi

    if [ "$task" == "find" ] ; then
        local object_name=$(abcli_clarify_object $2 .)

        abcli_tag set \
            $object_name \
            face,find

        abcli_download object $object_name

        abcli_log "face: find: $object_name"

        python3 -m Kanata.algo.face \
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
        if [ "$object_name" == ".." ] ; then
            local object_name=$abcli_object_name_prev
        fi
        abcli_download object $object_name

        abcli_relation set $object_name $abcli_object_name produced

        python3 -m Kanata.algo.face \
            track \
            --source $object_name \
            --destination $abcli_object_name \
            ${@:3}

        abcli_tag set . face,track

        return
    fi

    abcli_log_error "-abcli: face: $task: command not found."
}