# localshare
Expose your local http service to public network with ssh tunnel

## Quickstart

```bash
ssh -R /:localhost:80 -p 1022 app.pywebio.online
```

This command will give you an entrypoint, which you can use to access your `http://localhost:80` in public network.


## Build your own tunnel service

```bash
docker build -t localshare .
docker run --restart=always --name localshare -d -p 1022:1022 -p 80:80 localshare
```

