import os
import json


CONFIG_FILE = '.flipside-config.json'


def get_platform_config():
    if not os.path.isfile(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r+') as f:
        return json.load(f)



def set_platform_config(config, merge=True):
    if merge:
        default = get_platform_config()
        default.update(config)
    else:
        default = config
    with open(CONFIG_FILE, 'w') as f:
        f.write(json.dumps(default))
