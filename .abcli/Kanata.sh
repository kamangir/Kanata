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
        abcli_show_usage "Kanata config <keyword> <value>" \
            "config Kanata: <keyword>=<value>."
        abcli_show_usage "Kanata extract_faces [<video_id>] [<start_time>] [validate,frame_count=<n>]" \
            "[vaidate] extract faces  [from <video_id>]."
        abcli_show_usage "Kanata ingest        [<video_id>] [<start_time>] [validate]" \
            "[validate] ingest        [<video_id>]."
        abcli_show_usage "Kanata register       <video_id_1,video_id_2>" \
            "register                 <video_id_1,video_id_2>."
        abcli_show_usage "Kanata render [<video_length>] [validate]" \
            "[validate] render a video."
        abcli_show_usage "Kanata slice [<video_id>] [validate]" \
            "[validate] slice         [<video_id>]."
        abcli_show_usage "Kanata status" \
            "show status of Kanata."
        abcli_show_usage "Kanata validate" \
            "validate Kanata."

        if [ "$(abcli_keyword_is $2 verbose)" == true ] ; then
            python3 -m Kanata --help
        fi
        return
    fi

    if [ "$task" == "config" ] ; then
        local keyword=$2
        local value=$3

        abcli_cache write Kanata.$keyword "$value"
        return
    fi

    if [ "$task" == "extract_faces" ] ; then
        local video_id=$2

        local start_time=$(abcli_clarify_input $3 0.0)

        local options="$4"
        local do_stream=$(abcli_option_int "$options" stream 1)
        local do_validate=$(abcli_option_int "$options" validate 0)
        local frame_count=-1
        if [ "$do_validate" == "1" ] ; then
            local frame_count="25"
        fi
        local frame_count=$(abcli_option_int "$options" frame_count $frame_count)

        abcli_Kanata \
            ingest \
            $video_id \
            $start_time \
            $options \
            --frame_count $frame_count

        abcli_faces \
            find \
            $abcli_object_name \
            --visualize $do_validate

        abcli_faces \
            track \
            $abcli_object_name \
            --visualize $do_validate

        return 

        abcli_cache write $abcli_object_name.video_id $video_id
        abcli_cache write $abcli_object_name.start_time $start_time

        if [ "$do_stream" == "1" ] ; then
            abcli_upload open
            abcli_message stream $abcli_object_name
        fi

        return
    fi

    if [ "$task" == "ingest" ] ; then
        local video_id=$(abcli_clarify_input $2 $Kanata_validation_video_id)
        local start_time=$(abcli_clarify_input $3 0.0)

        local options="$4"
        local do_validate=$(abcli_option_int "$options" validate 0)

        abcli_select
        local video_object_name=$abcli_object_name
        abcli_youtube download $video_id

        local extra_args=""
        if [ "$do_validate" == "1" ] ; then
            local extra_args="--frame_count 25"
        fi

        abcli_select
        abcli_graphics \
            video_to_frames \
            $abcli_object_root/$video_object_name/video.mp4 \
            $abcli_object_name \
            --period $KANATA_PERIOD \
            --start_time $start_time \
            $extra_args \
            ${@:5}

        return
    fi

    if [ "$task" == "register" ] ; then
        local list_of_video_id=$2
        local list_of_video_id=$(echo "$list_of_video_id" | tr , " ")

        local cw_version=$(abcli_Kanata_version)

        local video_id
        for video_id in $list_of_video_id ; do
            abcli_log "Kanata.register($video_id)"
            local check=$(abcli_youtube is_CC $video_id)
            if [ "$check" != "True" ] ; then
                abcli_log_error "youtube/$video_id is not licensed under Creative Commons - will not register."
                return
            fi
            abcli_log "validated that youtube/$video_id is licensed under Creative Commons."

            abcli_tag set \
                $video_id \
                Kanata_video_id_$cw_version,youtube_video_id \
                ${@:3}
        done

        return
    fi

    if [ "$task" == "render" ] ; then
        local video_length=$(abcli_arg_clarify $2 1)
        let "frame_count = $KANATA_FPS * $video_length" 

        local options=$(abcli_unpack_keyword $3)
        local do_validate=$(abcli_option_int "$options" validate 0)

        local extra_args=""
        if [ "$do_validate" == "1" ] ; then
            local extra_args="--occupancy -1"
        fi

        abcli_log "Kanata.render($video_length s): $frame_count frame(s) - validate:$do_validate"

        abcli_select

        python3 -m Kanata \
            render \
            --frame_count $frame_count \
            $extra_args \
            ${@:4}

        if [ "$do_validate" == "0" ] ; then
            local cw_version=$(abcli_Kanata_version)
            abcli_tag set \
                $abcli_object_name \
                Kanata_render_$cw_version
        fi

        abcli_create_video info.jpg info fps=$KANATA_FPS

        abcli_upload open
        abcli_publish $abcli_object_name info.mp4

        return
    fi

    if [ "$task" == "slice" ] ; then
        local video_id=$2
        if [ "$video_id" == "-" ] ; then
            local video_id=""
        fi
        if [ -z "$video_id" ] ; then
            local video_id=$Kanata_validation_video_id
        fi

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

        local cw_version=$(abcli_Kanata_version)
        for (( slice=0; slice<=$last_slice; slice++ ))
        do
            abcli_log "Kanata.slice($video_id:$slice/$last_slice)"

            let "start_time = $slice * $KANATA_SLICE"
            abcli_work Kanata_slice_$cw_version "abcli_Kanata extract_faces $video_id $start_time $options"
        done

        return
    fi

    if [ "$task" == "status" ] ; then
        python3 -m Kanata \
            status \
            ${@:2}
        return
    fi

    if [ "$task" == "validate" ] ; then
        abcli_Kanata extract_faces - - stream,validate
        return
    fi

    abcli_log_error "-Kanata: $task: command not found."
}

function abcli_Kanata_version() {
    python3 -m Kanata get_version
}