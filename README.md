### Docker run and mount project 
build docker 
```bash
docker build -t rav-backend -f docker/Dockerfile
docker run --rm -it -v `pwd`:/tmp/ytcreator -p 8000:8000 rav-backend bash
```


### Heroku deploy 
```
heroku config:set LANG=en_US.UTF-8
```


## Multibackground support 

```json5
{
  "song_url": "https://www.nhaccuatui.com/bai-hat/rat-muon-quay-dau-nhin-em-dinh-uyen.Ms7eW7BK4oXX.html",
  "backgrounds": [
    {
      "timing": {
        "start": "0",
        "duration": "5000"
      },
      "file": "NeuMaiNay_DuongHoangYen_v3.png",
      "effect": {
        "file": "Faded_Sphere",
        "opacity": 30
      },
      "lyric": {
        "position": {
          "x": 52,
          "y": 750
        },
        "size": {
          "width": 1400,
          "height": 232
        },
        "font": {
          "name": "UTM Dai Co Viet",
          "color": "0xf1f020",
          "size": 60
        }
      }
    }
  ],
  "renderType": {
    "type": "preview"
  },
  "song_effect": {
    "type": "SONG",
    "name": "Trans_Eff_019"
  }
}
```
FrontEnd: 
- "timming" : dictionary 
  - start: start time (miliseconds unit, elapse from the sing begin)of the background (the background could be image/video
  - duration: duration of the backround caculated from start time (in miliseconds unit)
Backend: 
ffmpeg: 

`-ss [time]` => convert `timing.start` => `hh:mm:ss.xxx` => string with flag -ss

`-t [duration]` => convert `timming.duration` => `hh:mm:ss.mmm` to express 
duration of background. mean `duration` = `timing.start` + `timming.duration` => convert to 
`hh:mm:ss.xxx`

