#! /usr/bin/env bash

function abcli_face_finder() {
    local task=$(abcli_unpack_keyword $1 help)

    if [ "$task" == "help" ] ; then
        abcli_show_usage "face_finder find object   <object-name> [<filename.jpg>]" \
            "find faces in <object-name>[/<filename.jpg>]"
        abcli_show_usage "face_finder find filename <filename.jpg>" \
            "find faces in <filename.jpg>."
        abcli_show_usage "face_finder install" \
            "install face_finder."
        abcli_show_usage "face_finder track <object-name>" \
            "track faces in <object-name>."

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m Kanata.algo.face_finder --help
        fi
        return
    fi

    if [ "$task" == "find" ] ; then
        local source=$(abcli_clarify_object $3 .)
        local filename=$(abcli_clarify_input $4)

        local kind=$2
        if [ "$kind" == "object" ] ; then
            abcli_tag set $source face_finder,find,info
            abcli_download object $source
        fi

        abcli_log "face_finder: $kind:$source:$filename"

        python3 -m Kanata.algo.face_finder \
            find \
            --kind "$kind" \
            --source "$source" \
            --filename "$filename" \
            ${@:5}

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

        python3 -m Kanata.algo.face_finder \
            track \
            --source $object_name \
            --destination $abcli_object_name \
            ${@:3}

        abcli_tag set . face_finder,track,info

        return
    fi

    abcli_log_error "unknown task: face_finder '$task'."
}