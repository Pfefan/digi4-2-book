import configparser
import os

from logging_formater import ConfigLogger


class Config:
    def __init__(self) -> None:
        self.logger = ConfigLogger().setup()

    def check_config(self) -> bool:
        if not os.path.isfile("config.ini"):
            config = configparser.ConfigParser()

            config['DEFAULT'] = {
                'email': 'email',
                'password': 'password',
            }
            with open('config.ini', 'w+', encoding="utf-8") as configfile:
                config.write(configfile)
            self.logger.warning("No Config file!!")
            return False
        else:
            config = configparser.ConfigParser()
            config.read('config.ini')
            config = config['DEFAULT']

            if config["email"] == "email" or config["password"] == "password":
                self.logger.warning("Config not set!!!")
                return False

            return True

    def get_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['DEFAULT']
