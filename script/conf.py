import os
import yact
import yaml
from flask import Config


class YactConfig(Config):
    def from_yaml(self, config_file, directory=None):
        config = yact.from_file(config_file, directory=directory)
        for section in config.sections:
            self[section.upper()] = config[section]


# Fonction de recuperation des données du fichier de configuration /config.yaml
def configuration():
    with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml', "r") as ymlfile:
        cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)
        return cfg

