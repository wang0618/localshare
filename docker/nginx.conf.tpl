map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    server_name   ~^(?<app_name>.+)\.{{ server_name }}$;
    listen 80;
    {% if cert_dir %}
    listen 443 ssl;

    ssl_certificate   {{ cert_dir }}/cert.pem;
    ssl_certificate_key  {{ cert_dir }}/cert.key;
    {% endif %}

    location / {
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_pass http://unix:{{ socket_dir }}/${app_name}.sock;
    }
}

server {
    listen 80 default_server;
    server_name _;

    location / {
        return 302 https://github.com/wang0618/localshare;
    }
}