FROM python:3.9-buster

WORKDIR /localshare

ADD ./ .

RUN bash /localshare/docker/install-nginx-debian.sh

# for ssh
EXPOSE 1022

EXPOSE 80

EXPOSE 443

RUN pip install --no-cache-dir -r requirements.txt

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone


CMD /localshare/docker/start.sh