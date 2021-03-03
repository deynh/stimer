import configparser
import logging

from core import STimer

CONFIG_FILENAME = "stimer.conf"
CONFIG_SECTIONS = {
    "general": "GENERAL",
    "timers": "TIMERS",
}


# TODO: No duplicate names
def save_timer(timer):
    timer_json = timer.to_json()
    name = None
    if timer.name:
        name = timer.name
    else:
        name = _find_timer_number()
    write_value(name, timer_json, CONFIG_SECTIONS["timers"])
    return name


def remove_timer(name):
    config = _load_config_file()
    if CONFIG_SECTIONS["timers"] in config:
        if name in config[CONFIG_SECTIONS["timers"]]:
            config[CONFIG_SECTIONS["timers"]].pop(name)
            _write_config_file(config)
            logging.info("Timer " + name + " removed.")
            return True
    return False


def load_timer(name):
    timer_json = read_value(name, CONFIG_SECTIONS["timers"])
    if timer_json is None:
        return None
    return STimer().from_json(timer_json)


def get_timers_list():
    config = _load_config_file()
    timers = []
    if CONFIG_SECTIONS["timers"] in config:
        for name in config[CONFIG_SECTIONS["timers"]]:
            timer = load_timer(name)
            if timer:
                timers.append([name, timer])
    return timers


def _find_timer_number():
    config = _load_config_file()
    if CONFIG_SECTIONS["timers"] not in config:
        config.add_section(CONFIG_SECTIONS["timers"])
    names = config[CONFIG_SECTIONS["timers"]].keys()
    name_nums = []
    for name in names:
        if name.isdigit():
            name_nums.append(int(name))
    name_nums.sort()
    new_num = 1
    for num in name_nums:
        if new_num == num:
            new_num = new_num + 1
    return str(new_num)


def read_value(key: str, section: str = CONFIG_SECTIONS["general"]) -> str:
    config = _load_config_file()
    value = None
    if section in config:
        if key in config[section]:
            value = config[section][key]
    return value


def write_value(key: str, value: str, section: str = CONFIG_SECTIONS["general"]):
    config = _load_config_file()
    if section not in config:
        config[section] = {}
    config[section][key] = value
    _write_config_file(config)


def _load_config_file() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    try:
        with open(CONFIG_FILENAME, "r") as f:
            config.read_file(f)
    except FileNotFoundError:
        with open(CONFIG_FILENAME, "x"):
            logging.info("stimer.conf file created.")
    except OSError as e:
        logging.error(e)
        return None
    return config


def _write_config_file(config: configparser.ConfigParser) -> configparser.ConfigParser:
    try:
        with open(CONFIG_FILENAME, "w") as f:
            config.write(f)
    except OSError as e:
        logging.error(e)
        return None
    return config
