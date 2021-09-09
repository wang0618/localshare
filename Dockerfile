FROM python:3.9-buster

WORKDIR /localshare

ADD ./ .

RUN bash /localshare/install-nginx-debian.sh

RUN cp /localshare/nginx.conf /etc/nginx/conf.d/

# for ssh
EXPOSE 1022

EXPOSE 80

EXPOSE 443

RUN pip install --no-cache-dir -r requirements.txt

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

ENTRYPOINT ["/localshare/docker-entrypoint.sh"]

CMD python main.py
