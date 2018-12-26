# Useful FFmpeg commands

This repo contains examples for useful FFmpeg commands extracted from practical needs.

## What is FFmpeg?

If you haven't met with [FFmpeg](https://www.ffmpeg.org/) yet, this page might be of little use to you.

FFmpeg is a free, open-source software and it's the Swiss Army knife of video- and audio-related processing. It can be used to do an unbelievable range of things and it's being utilized by virtually anyone who's doing any form of video processing. It comes as a command-line tool, but many programs ship with a built-in version of FFmpeg in them to be able to process multimedia files. FFmpeg will run on Linux, Windows, OS X and other platforms.

This is my personal collection of FFmpeg commands, recorded here for myself to come back to and check when I need something. I'm making it public because someone else might find some pieces of information here useful.

**License:** Feel free to use the information here in any way you wish, no attribution is needed, but I take no responsibility for the results of your actions.

Some of the commands have been taken verbatim from other sources, others have been heavily modified since. You can find some more commands here:

- <https://trac.ffmpeg.org/wiki/> – the official FFmpeg wiki contains some very good examples.
- <http://www.labnol.org/internet/useful-ffmpeg-commands/28490/>

Contributions are welcome.

## How to read this

Just search the page for the example you need.

The examples below have little to no context and usually do not explain all the different options used. That's what the documentation is for – you can [read it online here in this huge one-page HTML document](https://www.ffmpeg.org/ffmpeg-all.html) or just do `man ffmpeg-all` in your terminal.

The order of the options in an FFmpeg command has some significance, but generally you can use any order you want.

## Extract audio from a video file (e.g. an YouTube clip)

    ffmpeg -i skrillex.mp4 -ab 256k skrillex.mp3

## Slice a 1-minute portion of an audio file starting at 2m30s, convert it to MP3 and add audio fade in and fade out effects

    ffmpeg -i INPUT.mp4 -c:a libmp3lame -b:a 128k -ss 00:02:30 -to 00:03:30 -af 'afade=t=in:st=150:d=3,afade=t=out:st=207:d=3' OUTPUT.mp3

## Slice the first 5 min of a video

    ffmpeg -i 038-Speed-Limit-260.avi -c copy -t 00:05:00 Simone_Origone_Speed_Limit_260.avi

## Slice 5 min starting from 12:30 from a video

    ffmpeg -i 038-Speed-Limit-260.avi -c copy -ss 00:12:30 -t 00:05:00 Simone_Origone_Speed_Limit_260.avi

## Create x264 mp4 videos suitable for online streaming

The x264 codec provides a very good compression ratio and a good output quality. The options below are suitable for online embedding/streaming of a video. You will probably need an `webm` version as well as some browsers can't play the mp4 one (see below). Adjust the size and bitrates accordingly.

    ffmpeg -y -i in.suffix -filter:v scale=640:360,setsar=1/1 -pix_fmt yuv420p -c:v libx264 -preset:v slow -profile:v baseline -x264opts level=3.0:ref=1 -b:v 700k -r:v 25/1 -force_fps -movflags +faststart -c:a libfaac -b:a 80k -pass x out.mp4

## Create webm videos suitable for online streaming (no audio)

Suitable for online streaming. You will probably need an mp4 version as well (see above.) Adjust the bitrates and resolution accordingly.

NB: This example assumes the input has no sound.

    ffmpeg -i bff-teaser-part-1-1000kbps-no-sound.mp4 -filter:v scale=640:360,setsar=1/1 -pix_fmt yuv420p -vpre libvpx-720p -b:v 800k -r:v 25/1 -force_fps -c:a none -pass 2 bff-teaser-part-1-1000kbps-no-sound.webm

## Remove sound from webm videos

    ffmpeg -i bff-teaser-part-1-1000kbps-no-sound.mp4 -pix_fmt yuv420p -vpre libvpx-720p -b:v 800k -r:v 25/1 -force_fps -c:a none -pass 2 bff-teaser-part-1-1000kbps-no-sound.webm

## Replace video's audio with audio from an external audio file

Based on [this StackOverflow answer](http://superuser.com/questions/800234/how-to-replace-an-audio-stream-in-a-video-file-with-multiple-audio-streams).

    ffmpeg -i VIDEO -i AUDIO -map 0:v -map 1:a -codec copy -shortest RESULT

## Concatenate files with different encodings (but the same resolution)

A more detailed explanation can be found in [this FFmpeg wiki page](https://trac.ffmpeg.org/wiki/Concatenate).

    ffmpeg -threads 2 -i INPUT1 -i INPUT2 -filter_complex '[0:0] [0:1] [1:0] [1:1] concat=n=2:v=1:a=1 [v] [a]' -map '[v]' -map '[a]' -c:v mpeg4 -preset:v slow -filter:v scale=768:576,setsar=1/1 -pix_fmt yuv420p -b:v 1900 -r:v 25 -force_fps -c:a mp3 -b:a 256 -s:a 48000 flying2.avi

## Create an mpeg4 video with mp3 sound

This is suitable for playback on a wide range of slower devices. The quality options here are relatively good.

    ffmpeg -threads 2 -i input.avi -qmin 1 -qmax 3 -c:v mpeg4 -filter:v scale=768:576,setsar=1/1 -pix_fmt yuv420p -b:v 2400k -r:v 25 -force_fps -c:a mp3 -b:a 256k -s:a 48000 encoded.avi

## Create an mpeg4 video with mp3 sound and resize to 720p

Used for processing videos for [Bansko Film Fest](http://banskofilmfest.com/en/).

    ffmpeg -i original.mp4 -threads 8 -c:v mpeg4 -c:a mp3 -vf scale=-2:720 -qmin 1 -qmax 4 encoded.avi

## Create a 5-second 720p video from an image

    ffmpeg -loop 1 -i INPUT.png -t 5 -c:v mpeg4 -vf scale=-2:720 -qmin 1 -qmax 3 OUTPUT-5s.avi

The `-2` tells FFMpeg to calculate the output width so that the original aspect ratio is preserved but also to make sure the output width is divisible by 2 as some codecs require even numbers for video width and height. [Read more about scaling here](https://ffmpeg.org/ffmpeg-filters.html#Options-1).

## Rip a DVD to an mpeg4+mp3 AVI

This assumes a PAL DVD.

To rip a DVD with FFmpeg, you just need the `*.VOB` files in the `VIDEO_TS` folder. Read more about [ripping DVDs with FFmpeg here](http://www.commandlinefu.com/commands/view/6585/dvd-ripping-with-ffmpeg).

    cat VIDEO_TS/VTS_01_*VOB | ffmpeg -i - -s 720x576 -c:v mpeg4 -c:a mp3 -qmin 1 -qmax 3 -b:a 256k -b:v 4000k -y encoded.avi

## Rendering videos with subtitles (burn-in subtitles)

This is tricky. A more detailed explanation can be found on [the FFmpeg wiki](https://trac.ffmpeg.org/wiki/HowToBurnSubtitlesIntoVideo).

The examples below assume you have subtitles in a SRT format, encoded in UTF-8.

### Add (render) subtitles to an already encoded video

    ffmpeg -i INPUT.avi -vf subtitles=SUBTITLES.srt -qmin 1 -qmax 3 OUTPUT-WITH-SUBS.avi

### Render subtitles at the top with a semi-transparent background

This will embed the subtitles at the top of the video instead of at the bottom as usual. It will also render a semi-transparent black rectangle underneath the subtitle font.

    ffmpeg -i INPUT.avi -vf subtitles="f=SUBTITLES.srt:force_style='FontName=Arial,FontSize=16,OutlineColour=&H55000000,BorderStyle=3,Alignment=6'" ENCODED-WITH-SUBS.avi

The syntax and options for customizing how subtitles are rendered are somewhat unintuitive. Read below to learn more.

### Render mp4 video (x264 + AAC) with embedded subtitles with a background

This is similar to the command above and will render a video with embedded subtitles on a semi-transparent background and a bigger Arial font but in a mp4 container:

    ffmpeg -threads 0 -i INPUT.avi -c:v libx264 -c:a aac -b:a 196k \
        -vf "subtitles=SUBTITLES.srt:force_style='FontName=Arial,FontSize=22,OutlineColour=&H22000000,BorderStyle=3'" \
        -f mp4 -preset slow -profile:v baseline -x264opts level=3.0:ref=1 -b:v 2800k \
        -y OUTPUT_WITH_SUBTITLES.mp4

The background color is in a HEX format. The alpha channel is represented by the first two digits, `22`. The minimum is `00` (opaque) and the maximum is `FF` (fully transparent). The next three digit-pairs represent the red, green and blue channels, respectively.

### Add (render) subtitles with different font, colors, etc.

Customizing the font, color, size, background color, etc. of the subtitles can be hard. The options for customizations are actually option names from the ASS subtitles spec ("Advanced SubStation Alpha"). This is what FFmpeg uses internally (via `libass`). These can be applied both with the `ass` and `subtitles` filters. When using the `subtitles` video filter, FFmpeg converts the subtitles internally to ASS.

To see the available subtitle styling options, download this [Word doc file](http://moodub.free.fr/video/ass-specs.doc) (yes, indeed). I've also included [a PDF version of the Advanced SubStation Alpha (ASS) standard here](../Docs/ass-specs.pdf). Use this to learn the meaning of the the different fields and their values present in the `force_style` setting from the example above.

The example below prepares a video for burning on a video DVD. The subtitles have a semi-opaque rectangular back background. The `original_size` differs from the resize option because the input is assumed to be 16:9, even though it's stored in a physical resolution of 720x576 (if this confuses you, you're not alone; Google for "SAR" and "DAR").

    ffmpeg -i INPUT.avi -target pal-dvd -s 720x576 -vf subtitles="f=SUBTITLES.srt:force_style='FontName=Arial,FontSize=22,OutlineColour=&H66000000,BorderStyle=3':original_size=720x405" -y ENCODED-WITH-SUBS.mpg

### Rip a DVD, burn-in subtitles and prepare for burning back to a DVD

The subtitle styling is as in the previous example. See more about ripping DVDs above. More info [here](http://ffmpeg.gusari.org/viewtopic.php?f=25&t=1235).

This is for a widescreen (16:9) PAL DVD input and prepares the video for burning it back to a DVD.

    cat VIDEO_TS/VTS_01_*.VOB | ffmpeg -i - -target pal-dvd -s 720x576 -vf subtitles="f=SUBTITLES.srt:force_style='FontName=Arial,FontSize=22,OutlineColour=&H66000000,BorderStyle=3':original_size=720x405" -y ENCODED-WITH-SUBS.mpg

### Render .ASS subtitles in a DVD video

Steps: **Rip the DVD** → **add subs** → **mpg file for ripping back to a DVD**

    cat VIDEO_TS/VTS_01_[123456789].VOB | ffmpeg -i - -target pal-dvd -s 720x576 -vf ass=SUBTITLES.ass -y ENCODED-WITH-SUBS.mpg

### Convert SRT subtitles to ASS

    ffmpeg -i subtitles.srt subtitles.ass

You can now edit the plaintext `.ass` file and change the styling accordingly. For documentation on the meaning of options and possible values, read above.

Here is an excerpt of an `.ass` file for subtitles with a semi-transparent rectangular black background and a white Arial text.

    [V4+ Styles]
    Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
    Style: Default,Arial,28,&Hffffff,&Hffffff,&H44000000,&H0,0,0,0,0,100,100,0,0,3,2,0,2,10,10,10,0

### Render .ASS subtitles in a video

    ffmpeg -i INPUT.avi -vf ass=SUBTITLES.ass -qmin 1 -qmax 3 OUTPUT-WITH-SUBS.avi

## Output to a PAL DVD with top and bottom black bars padding and subtitles

This is adjusted for a `720:304` video.

    ffmpeg -i INPUT.avi -target pal-dvd -vf 'scale=720:304, pad=720:576:0:136, ass=subtitles.ass' -y OUTPUT-WITH-SUBS.mpg

## Prepare a video for burning on a PAL DVD

    ffmpeg -i input.avi -f:v scale=720:576 -target pal-dvd output.mpg

To burn the DVD itself, on Linux you will have to use `dvdauthor` and `genisoimage`:

    export FOLDER_NAME="YOUR_MOVIE"
    export VIDEO_FORMAT=PAL
    dvdauthor --title -o $FOLDER_NAME -f out.mpg && dvdauthor -T -o $FOLDER_NAME
    genisoimage -dvd-video -o MOVIE.iso $FOLDER_NAME

On OS X you can use [Burn](http://burn-osx.sourceforge.net/Pages/English/home.html) - it does the DVD video authoring and burning for you. It also has an embedded ffmpeg in it and can convert videos to the proper format if needed.

## How to Add a Watermark to Video

[FFMPEG filters](https://www.ffmpeg.org/ffmpeg-filters.html) provide a powerful way to programmatically enhance or alter videos, and itâ€™s fairly simple to add a watermark to a video using the overlay filter. The easiest way to install ffmpeg is to [download](https://www.ffmpeg.org/download.html) a pre-built binary for your specific platform. Then you donâ€™t have to worry about including and installing all the right dependencies and codecs you will be using.

Once you have ffmpeg installed, adding a watermark is as easy as passing your existing source through an overlay filter like so:

<pre>ffmpeg -i test.mp4 -i watermark.png -filter_complex "overlay=10:10" test1.mp4</pre>

Basically, weâ€™re passing in the original video, and an overlay image as inputs, then passing it through the filter, and saving the output as test1.mp4.

We specify a specific position of the overlay in pixels â€“ **10:10** puts the video 10 pixels from the top and 10 pixels from the right. (x:y coordinates)

In some cases you might not know the exact dimensions of the videos youâ€™ll be watermarking. Fortunately, there are variables you can use to better position your watermark depending on the size of the video. These variables include:

*   **main_h** â€“ the videoâ€™s height
*   **main_w** â€“ the videoâ€™s width
*   **overlay_h** â€“ the overlayâ€™s height
*   **overlay_w** â€“ the overlayâ€™s width

Using these variable we can position the watermark right in the center of the video like so:

<pre>ffmpeg -i test.mp4 -i watermark.png \
-filter_complex "overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2" test2.mp4</pre>

If we wanted to add branding or a watermark to the clip but not cover the existing video, we can use the [pad filter](https://www.ffmpeg.org/ffmpeg-filters.html#pad) to add some padding to our clip, and then position our watermark over the padding like so:

<pre>ffmpeg -i test.mp4 -i watermark2.png \
-filter_complex "pad=height=ih+40:color=#71cbf4,overlay=(main_w-overlay_w)/2:main_h-overlay_h" \
test3.mp4</pre>

Once you start getting the hang of this, you can even animate your overlays!

<pre>ffmpeg -i test.mp4 -i watermark.png \
-filter_complex "overlay='if(gte(t,1), -w+(t-1)*200, NAN)':(main_h-overlay_h)/2" test4.mp4</pre>


# overlay image to another image 
```shell 
ffmpeg -i ttt.jpg -vf "movie=fix2.png [fix]; [in] setsar=sar=1,format=rgba [inf]; [inf][fix] blend=all_mode=overlay:all_opacity=1,format=yuva422p10le [out]" -q:v 1 -y xxx.jpg
```
```bash
ffmpeg -i short.mp4 -filter_complex "[0:v]split=2[v0][v1]; [v0]crop=200:200:60:30,boxblur=10[fg]; [v1][fg]overlay=60:30[v]" -map "[v]" -map 0:a -c:v libx264 -c:a copy -movflags +faststart filtered.mp4
# [0:v]split=2[v0][v1]; [v0]crop=200:200:60:30,boxblur=10[fg]; [v1][fg]overlay=60:30[v]
#[0:v]split=2[v0][v1]  : video input 0 => use filter split -> 2 video channel v0,v1 
#input channel v0 -> crop 200,200 at (x,y)(60,30), bloxblur=10 -> output fg
#inut v1,fg => overlay at (x,y)(60,30) -> output v
#using map => map output total channel => video output v , audio from 0:a 
```


