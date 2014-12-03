{% set app_name = "elastic_website" %}
{% set home = "/home/elastic_website" %}
{% set uwsgi_socket = home ~ "/uwsgi/control/uwsgi.sock" %}

nginx:
  ng:
    server:
      config: 
        worker_processes: 4
        pid: /run/nginx.pid
        events:
          worker_connections: 768
        http:
          sendfile: 'on'
          include:
            - /etc/nginx/mime.types
            - /etc/nginx/conf.d/*.conf
            - /etc/nginx/sites-enabled/*.conf
    vhosts:
      managed:
        {{ app_name }}.conf:
          enabled: True
          config:
            - server:
              - server_name: www.elastic-coders.com
              - listen:
                - 80
              - location /:
                - uwsgi_pass: unix://{{ uwsgi_socket }}
                - include: uwsgi_params
                - uwsgi_param:  UWSGI_SCHEME $http_x_forwarded_proto  {# $scheme #}
                - uwsgi_param:     SERVER_SOFTWARE    nginx/$nginx_version
                - location ~ ^/favicon\.(ico|png)$:
                  - rewrite: (.*) /static/images$1
                - location /static:
                  - alias: {{ home }}/static

users:
  {{ app_name }}:
    fullname: Elastic Coders website
    homedir: {{ home }}
    createhome: True
    groups:
      - uwsgi

uwsgi_ng:
  apps:
    managed:
      {{ app_name }}:
        home: {{ home }}
        package_name: elastic-website
        uwsgi_socket: {{ uwsgi_socket }}
