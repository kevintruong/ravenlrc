# Youtube Creator service (Flask)
## install database 

### Docker run and mount project 
build docker 
```bash
docker build -t backend -f docker/Dockerfile
```
```bash
docker run --rm -it -v D:\Project\ytcreatorservice:/tmp/ytcreator backend bash
```


```json5
{
  "song_url": "https://m.nhaccuatui.com/bai-hat/vi-em-van-hari-won.1iDSDdrDFCCs.html",
  "background": {
    "file": "http://this-is-a-file.png",
    "effect": {
      "file": "Green_Bubble.mov",
      "opacity": 30
    },
  },
  "lyric": {
    "file": "http://url-to-lyric-file",
    "position": {
      "x": 221,
      "y": 900
    },
    "size": {
      "width": 691,
      "height": 43
    },
    "fontname": "SVN-Futura Light",
    "fontcolor": "0x474748",
    "fontsize": 60,
    "effect": {
      "song": {  // effect for the whole song
        "type": "SONG",
        "code": "EFFECT_CODE"
      }
    }
  },
  "buildtype": "preview"
}
```
```json5
{
  "type": "WORD",
  "code": "WORD_EFFECT_CODE",
  "start": {
    "fontSize": 20,
    "fontColor": "0x345678"
  },
  "end": {
    "fontSize": 50,
    "fontColor": "0xffeeff"
  }
}
```
```json5

{
  "type": "SONG",
  "code": "SONG_EFFECT_CODE",
}

```
```json5
{
  "type": "SONG",
  "code": "SENTENCE_EFFECT_CODE",
}
```
