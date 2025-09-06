import argparse
import configparser
import sys

from models import OPTIONS, UserInputs


def get_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("A tool to scrape some images from a single page of a website")
    for key, value in OPTIONS.items():
        parser.add_argument(f'--{key}', f'-{value.short_hand}', help=value.help)

    return parser.parse_args()


def build_default_config() -> None:
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    for key, value in OPTIONS.items():
        if value.config_section not in config:
            config[value.config_section] = {}
        
        config[value.config_section][f'# {value.help}'] = None
        config[value.config_section][key] = str(value.default_value)

    with open('config.ini', 'w') as fp:
        config.write(fp)


def get_inputs() -> UserInputs:
    config = configparser.ConfigParser()
    files_read = config.read('config.ini')
    if 'config.ini' not in files_read:
        build_default_config()
        sys.exit(0)
    
    args = get_cli_args()

    return UserInputs(args, config)
