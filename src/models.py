import argparse
import configparser


class InputOption:
    def __init__(self, name: str, short_hand: str, help: str, config_section: str, default_value):
        self.name = name
        self.short_hand = short_hand
        self.help = help
        self.config_section = config_section
        self.default_value = default_value


class UserInputs:
    url: str
    output_folder: str
    image_url_sub_path: str
    min_image_size_kb: int
    file_extensions: list[str]

    def __init__(self, cli_args: argparse.Namespace, config: configparser.ConfigParser):
        missing_variables = set()
        for key, value in OPTIONS.items():
            attr = getattr(cli_args, key)
            try:
                setattr(self, key, attr if attr else config[value.config_section][key])
            except KeyError as e:
                missing_variables.add(e.args[0])

        for attr_name, attr_value in self.__dict__.items():
            if attr_value is None:
                missing_variables.add(attr_name)

        if missing_variables:
            raise Exception(f"Error: The following instance variables are missing: {', '.join(missing_variables)}")
        
OPTIONS = {
    'url': InputOption('url', 'u', 'The http/https url to scrape image for', 'PRIMARY', 'https://www.salty-crew.com/products/flagship-boardshort-dusty-olive'),
    'output_folder': InputOption('output_folder', 'f', 'The output folder the images will be saved to', 'PRIMARY', 'images'),
    'image_url_sub_path': InputOption('image_url_sub_path', 's', 'Some images are grouped by a sub-path. Use if wanting just a particular group of images', 'FILTERS', 'shop/files'),
    'min_image_size_kb': InputOption('min_image_size_kb', 'm', 'The minimum size an image must be to download', 'FILTERS', 100),
    'file_extensions': InputOption('file_extensions', 'e', 'The file extension to filter by', 'FILTERS', '.jpg')
}
