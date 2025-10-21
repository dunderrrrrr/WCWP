```sh
gunicorn -w 4 --bind 127.0.0.1:8009 run:app
```