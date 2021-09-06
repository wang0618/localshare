FROM python:3.9-buster

WORKDIR /usr/src/app

ADD ./ .

RUN bash /usr/src/app/install-nginx-debian.sh


RUN cp /usr/src/app/nginx.conf /etc/nginx/conf.d/

# for ssh
EXPOSE 1022

EXPOSE 80

RUN pip install --no-cache-dir -r requirements.txt

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

CMD python main.py
