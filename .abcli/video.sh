#! /usr/bin/env bash

export ABCLI_VIDEO_DEFAULT_SIZE="1280x1024"

function abcli_create_video() {
    local options=$1

    if [ $(abcli_option_int "$options" help 0) == 1 ]; then
        # https://esahubble.org/press/video_formats/
        local options="dryrun,jpg|png,fps=<10>,filename=<video>,gif,prefix=<prefix>,rm_frames,resize_to=<$ABCLI_VIDEO_DEFAULT_SIZE>,scale=<1>"
        abcli_show_usage "abcli create_video$ABCUL[$options]$ABCUL[.|<object-name>]" \
            "<object-name>/frames -> <filename>.mp4."
        return
    fi

    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local fps=$(abcli_option "$options" fps 10)
    local filename=$(abcli_option "$options" filename video)
    local prefix=$(abcli_option "$options" prefix)
    local rm_frames=$(abcli_option_int "$options" rm_frames 0)
    local resize_to=$(abcli_option "$options" resize_to)
    local scale=$(abcli_option "$options" scale 1)
    local extension=$(abcli_option_choice "$options" jpg,png jpg)
    local generate_gif=$(abcli_option_int "$options" gif 0)

    local object_name=$(abcli_clarify_object $2 .)
    local object_path=$abcli_object_root/$object_name

    local video_filename=$object_path/$filename.mp4
    [[ -f "$video_filename" ]] &&
        rm -v $video_filename

    abcli_log "📼 create-video: $object_name/$extension -[$options]-> $video_filename"

    local temp_path=$object_path/$(abcli_string_random)
    mkdir -p $temp_path

    local frame_filename
    local index=0
    local size=""
    for frame_filename in $object_path/$prefix*.$extension; do
        abcli_log "🖼️  $frame_filename"
        local temp_filename=$temp_path/$index.$extension

        cp -v \
            $frame_filename \
            $temp_filename

        [[ ! -z "$resize_to" ]] &&
            python3 -m abcli.plugins.video \
                resize \
                --filename $temp_filename \
                --size $resize_to

        [[ -z "$size" ]] &&
            local size=$(python3 -m abcli.plugins.video size_of \
                --filename $temp_filename \
                --scale $scale)

        ((index++))
    done

    abcli_log "$object_name/$extension -> $video_filename - $size - $fps fps - 1/$scale"

    abcli_eval dryrun=$do_dryrun ffmpeg \
        -f image2 \
        -r $fps \
        -i $temp_path/%d.$extension \
        -s $size \
        -vcodec h264 \
        $video_filename

    [[ "$generate_gif" == 1 ]] &&
        abcli_eval dryrun=$do_dryrun \
            ffmpeg -i \
            $video_filename \
            $object_path/$filename.gif

    if [ "$rm_frames" == 1 ]; then
        cp -v \
            $temp_path/0.$extension \
            $object_path/screenshot.$extension
        rm -v $object_path/*.$extension
    fi

    python3 -m abcli.plugins.metadata \
        update \
        --keyword fps \
        --content $fps \
        --object_path $object_path
    python3 -m abcli.plugins.metadata \
        update \
        --keyword size \
        --content $size \
        --object_path $object_path

    rm -rfv $temp_path

    abcli_tag set $object_name video
}
