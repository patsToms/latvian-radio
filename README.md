List with Latvian internet radio streams
========================================

### setup
```bash
# build playlists
cd latvian-radio
pip install slugify
./build.py
# host
docker run -it --rm -p 8080:80 --name radio-web -v $PWD/dist:/usr/share/nginx/html -v $PWD/default.conf:/etc/nginx/conf.d/default.conf nginx
```

### Kodi setup

Add network location with URL like `http://something:8080/strm`.