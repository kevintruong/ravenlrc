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

