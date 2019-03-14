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
  "song": {
      "file" : "http://url-to-audio-file", 
      "singer": "Hari Won",    // need db to store/access info of singer 
      "title" : "Vì em vẫn",
      "lyric" : "https://url-to-plain-text-of-song-lyrics"
  },
  "background": {
      "file": "http://this-is-a-file.png",
      "effect": { // Optional 
        "file": "Green_Bubble.mov",
        "opacity": 30
      },
      "title": { //Optional 
          "file": "http://url-to-title-file",
          "position": {  //reference from top left
            "x" : 100, 
            "y" : 100
          },
      }, 
      "watermask": { //optional 
          "file": "http://url-to-logo-file",
          "position": {  //reference from top left
            "x" : 100, 
            "y" : 100
          },
      }, 
  },
  "spectrum": {
      "template": "Template_code",
      "position": {
          "x": 221,
          "y": 900
      },
      "size": {
         "width": 691,
         "height": 43
      }
  },
  "lyric": {
    "file": "http://url-to-lyric-file", // Can be None if crawler can get lrc from `song_url` 
    "position": {
      "x": 221,
      "y": 900
    },
    "size": {
      "width": 691,
      "height": 43
    },
    "font": {
        "name": "SVN-Futura Light",
        "color": "0x474748",
        "size": 60,
    },
    "effect": { //Optional , default effect is smart faded etc... 
        "song": {  // effect for the whole song
            "type": "SONG",
            "code": "EFFECT_CODE"
          },
        "word": {
              "type": "WORD",
              "code": "WORD_EFFECT_CODE",
              "words": ["this","is","example","I am example" ],
              "font": {
                    "name": "SVN-Futura Light",
                    "color": "0x474748",
                    "size": 60,
              },
              "start": { // animate font size, font color from start 20,0x345678 zoom in to 50, color 0xffeeff  
                "fontSize": 20,
                "fontColor": "0x345678"
              },
              "end": {
                "fontSize": 50,
                "fontColor": "0xffeeff"
              }
        }
    }
  },
  "buildtype": {
    "type" : "preview", // preview or release 
    "configure": {  //Optional , defaul 90 seconds, 1280x720 
       "duration" : 90, // seconds  
       "resolution": {
          "w" : 640, 
          "h" : 480,
       }
    },
  }
}
```
```json5
{
  "type": "WORD",
  "code": "WORD_EFFECT_CODE",
  "words": ["this","is","example","I am example" ],
  "font": {
        "name": "SVN-Futura Light",
        "color": "0x474748",
        "size": 60,
    },
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

### API return STATUS 
#### Success 
#### Errror
