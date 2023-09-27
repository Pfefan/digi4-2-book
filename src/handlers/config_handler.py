import configparser
import os

class Config:
    def __init__(self) -> None:
        pass

    def check_config(self) -> bool:
        if not os.path.isfile("config.ini"):
            config = configparser.ConfigParser()

            config['DEFAULT'] = {
                'email': 'email',
                'password': 'password',
            }
            with open('config.ini', 'w+', encoding="utf-8") as configfile:
                config.write(configfile)
            print("No Config file!!")
            return False
        else:
            config = configparser.ConfigParser()
            config.read('config.ini')
            config = config['DEFAULT']

            if config["email"] == "email" or config["password"] == "password":
                print("Config not set!!!")
                return False

            return True

    def get_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['DEFAULT']
