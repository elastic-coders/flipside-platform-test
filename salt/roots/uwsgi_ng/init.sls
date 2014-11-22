{% from "uwsgi_ng/map.jinja" import uwsgi_ng with context %}
{% set settings = salt['pillar.get']('uwsgi_ng') %}

include:
  - python

# install uwsgi globally
# TODO: optionally install uwsgi in a separate virtualenv
uwsgi-installed:
   pkg.installed:
     - name: uwsgi

{% macro get_archive_dir(app) -%}
   {{ settings.apps.managed.get(app).get('archive_dir', 'salt://dist') }}
{%- endmacro %}

{% macro get_app_archive(app, tag='master') -%}
   {{ get_archive_dir(app) ~ '/' ~ app ~ '-' ~ tag ~ '.tgz' }}
{%- endmacro %}
{% macro get_app_home_dir(app) -%}
   {{ settings.apps.managed.get(app).get('home', uwsgi_ng.home ~ app) }}
{%- endmacro %}
{% macro get_app_dist_dir(app) -%}
   {{ get_app_home_dir(app) ~ '/.dist' }}
{%- endmacro %}
{% macro get_app_virtualenv(app) -%}
   {{ get_app_home_dir(app) ~ '/virtual_app' }}
{%- endmacro %}
{% macro get_app_package_name(app, app_settings) -%}
   {{ settings.apps.managed.get(app, app_settings).get('package_name', app) }}
{%- endmacro %}
{% macro get_app_wheelhouse(app) -%}
   {{ get_app_dist_dir(app) ~ '/wheelhouse' }}
{%- endmacro %}
{% macro get_app_uwsgi_config_template(app) -%}
   {{ settings.apps.managed.get(app).get('config_template', 'salt://uwsgi_ng/files/uwsgi.conf.jinja') }}
{%- endmacro %}
{% macro get_app_uwsgi_config(app) -%}
   {{ get_app_home_dir(app) ~ "/uwsgi/uwsgi.conf" }}
{%- endmacro %}
{% macro get_app_uwsgi_master_fifo(app) -%}
   get_app_home_dir(app) ~ "/uwsgi/control/master.fifo"
{%- endmacro %}
{% macro get_app_uwsgi_socket(app) -%}
   get_app_home_dir(app) ~ "/uwsgi/control/uwsgi.sock"
{%- endmacro %}
{% macro get_app_uwsgi_pidfile(app) -%}
   get_app_home_dir(app) ~ "/uwsgi/control/uwsgi.pid"
{%- endmacro %}


{% for app, app_settings in settings.apps.managed.items() %}
{% with %}
   {% set archive = get_app_archive(app) %}
   {% set dist = get_app_dist_dir(app) %}
   {% set virtualenv = get_app_virtualenv(app) %}
   {% set package_name = get_app_package_name(app) %}
   {% set wheelhouse = get_app_wheelhouse(app) %}
   {% set uwsgi_config_template = get_app_uwsgi_config_template(app) %}
   {% set uwsgi_config = get_app_uwsgi_config(app) %}

# TODO: Fetch the app
app-{{ app }}-dist-removed:
  file.absent:
    - name: {{ dist }}


app-{{ app }}-dist-extracted:
  archive:
    - extracted
    - name: {{ dist }}
    - source: {{ archive }}
    - archive_format: tar
    - require:
        - file: app-{{ app }}-dist-removed


# app virtualenv in app homedir
app-{{ app }}-virtualenv:
  virtualenv.managed:
    - name: {{ virtualenv }}
    - use_wheel: True
    - require:
        - pkg: python-virtualenv

# install app in virtualenv
app-{{ app }}-virtualenv-pip:
  pip.installed:
    - name: {{ package_name }}
    - find_links: {{ wheelhouse }}
    - no_index: True
    - use_wheel: True
    - activate: {{ virtualenv }}
    - use_vt: True
    - require:
        - virtualenv: app-{{ app }}-virtualenv
        - pkg: uwsgi-installed
        - archive: app-{{ app }}-dist-extracted

# create uwsgi configuration file
app-{{ app }}-uwsgi-config:
  file.managed:
    - name: {{ uwsgi_config }}
    - source: {{ uwsgi_config_template }}
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - require:
        - pip: app-{{ app }}-virtualenv-pip
    - defaults:
        custom_var: "default value"
        other_var: 123    

# TODO: collect staticfiles from django
# TODO: collect frontend files

{% endwith %}
{% endfor %}
