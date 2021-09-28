# Build your own tunnel service

### 1. Some files to prepare
You need prepare a dir to provide the files required by localshare, the files generated by localshare will also be saved in this dir.

```bash
mkdir ~/localshare_config
```
localshare need a ssh host key to run underlying ssh server, if you don't have one, localshare will create one in this dir before the first running.
Otherwise, you put need rename your ssh host key to `ssh_host_key` and copy it to the dir.

If you want to enable https, you need to provide the cert files in this dir. The cert file and cert key need to be named as `cert.pem` and `cert.key`.

### 2. DNS setting

Add a DNS record to bind a wildcard subdomain for your service. 

### 3. Run server

```bash
docker build -t localshare .

docker run -v ~/localshare_config:/config \
           -e APP_SERVER_NAME=app.pywebio.online \
           --restart=always --name localshare -p 1022:1022 -p 80:80 -p 443:443 -d localshare
```
Remember to replace the `~/localshare_config` and `app.pywebio.online` with yours.