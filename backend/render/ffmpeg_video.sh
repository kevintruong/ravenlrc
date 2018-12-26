#!/usr/bin/env bash
FULLHD=1920x1080
function create_video_from_img_with_time_length(){
    input_img=$1
    length=$2
    output_mp4=$3
    ffmpeg -loop 1 -i $input_img -c:v libx264 -t $length -pix_fmt yuvj422p -vf scale=$FULLHD $output_mp4

}

function add_audito_to_video_using_map(){
    input_vid=$1
    input_aud=$2
    output_mv=$3

    ffmpeg -i ${input_vid} -i $input_aud -map 0:v -map 1:a -c copy -shortest ${output_mv}
}
#font colour format AABBGGRR
function add_subtitle_to_video(){
    input_sub=$1
    input_vid=$2
    input_font=$3
    output_mp4=$4
    font_size=$5
    font_colour_1=$6
    font_colou_opacity=$7
    ffmpeg_sub_cmd="f=$(pwd)/${input_sub}:force_style="
    ffmpeg_font_att="FontName=$input_font,FontSize=$font_size,PrimaryColour=&H${opacity}${font_colour_1},BorderStyle=0"
    ffmpeg_cmd=$(echo ffmpeg -y -i ${input_vid} -vf subtitles='"'${ffmpeg_sub_cmd}"'"${ffmpeg_font_att}"'"'"':original_size=${FULLHD} ${output_mp4})
    echo ${ffmpeg_cmd} | bash
}


function add_title_to_img(){
    input_title=$1
    input_img=$2
    output_img=$3

}
function create_video_from_bgvideo_with_time_length(){
    input_bgVid=$1
    input_length=$2
    output_vid=$3
    ffmpeg -re -stream_loop -1 -i ${input_bgVid} -c copy -y -t ${input_length} ${output_vid}
}


# the function will add and video like an effect to another video
function blending_video_to_video(){
    input_bgvid=$1
    input_blendvid=$2
    output_mp4=$3
    ffmpeg -i ${input_bgvid} -i ${input_blendvid} -filter_complex \
                                 "[1:0]setdar=dar=0,format=rgba[a]; \
                                  [0:0]setdar=dar=0,format=rgba[b]; \
                                  [b][a]blend=all_mode='overlay':all_opacity=0.3" \
                                  -c copy $output_mp4
#[0:v]crop,setdar,format[b];[1:v]setdar,format[a];[a][b]blend crop 0 Video following format of 1 
}

