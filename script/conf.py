import os
import yact
import yaml
from flask import Config, jsonify
import psycopg2
import pandas as pd



class YactConfig(Config):
    def from_yaml(self, config_file, directory=None):
        config = yact.from_file(config_file, directory=directory)
        for section in config.sections:
            self[section.upper()] = config[section]

# fonction configuration
def configuration():
    with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml', "r") as ymlfile:
        cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)
        return cfg

# fonction add_headers
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    return response

#fonction error
def error(message):
    return jsonify({
        'success': False,
        'message': message
    })

# fonction de connection à la BDD
def connect():
    return psycopg2.connect(database=NAME_DB, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)

# fonction pour les requetes de type select sans arguments
def select_query(query):
    con = None
    try:
        con = connect()
        df = pd.read_sql(query, con)
        data = df.to_dict(orient='records')
        con.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    return data

NAME_DB = configuration()["NAME_DB"]
USER_DB = configuration()["USER_DB"]
PASSWORD_DB = configuration()["PASSWORD_DB"]
HOST_DB = configuration()["HOST_DB"]
PORT_DB = configuration()["PORT_DB"]
