import argparse
import configparser
import sys

from models import OPTIONS, UserInputs

URL = ('url', 'The http/https url to scrape image for')
OUTPUT_FOLDER = ('output_folder', 'The output folder the images will be saved to')
IMAGE_SUB_PATH = ('image_url_sub_path', 'Some images are grouped by a sub-path. Use if wanting just a particular group of images')
MIN_SIZE_KB = ('min_image_size_kb', 'The minimum size an image must be to download')
FILE_EXTENSIONS = ('file_extensions', 'The file extension to filter by')


def get_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("A tool to scrape some images from a single page of a website")
    parser.add_argument(f'--{URL[0]}', '-u', help=URL[1])
    parser.add_argument(f'--{OUTPUT_FOLDER[0]}', '-f', help=OUTPUT_FOLDER[1])
    parser.add_argument(f'--{IMAGE_SUB_PATH[0]}', '-s', help=IMAGE_SUB_PATH[1])
    parser.add_argument(f'--{MIN_SIZE_KB[0]}', '-m', help=MIN_SIZE_KB[1])
    parser.add_argument(f'--{FILE_EXTENSIONS[0]}', '-e', help=FILE_EXTENSIONS[1])

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
