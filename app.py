import os

import psycopg2
from flask import Flask, g , jsonify, request, Config
from script.function import *
import jsonify, json, jsonpickle
import requests
from flask_cors import CORS
from functools import wraps
from flask_oidc import OpenIDConnect
import logging
import yact as yact



app = Flask(__name__)
test = "ceci est un test()"
#export Flask_APP =

# Build custom conf object yaml conf
class YactConfig(Config):
    def from_yaml(self, config_file, directory=None):

        config = yact.from_file(config_file, directory=directory)
        for section in config.sections:
            self[section.upper()] = config[section]

def cfg():

    with open(os.path.dirname(os.path.abspath(__file__)) + './script/config.yaml', "r") as ymlfile:
        cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)
        return cfg

Client_d = cfg()['CLIENT_ID']
client_secret = cfg()['CLIENT_SECRET']
Realm = cfg()['REALM']

client_test = os.getenv('CLIENT_ID')
print("Le client secret est " + client_secret)
print("Le client Id est " + Client_d)



@app.route("/")
def home():
    return  Client_d # "Hello Flask  on fait des tesst test"

#create_table_inventaire()
@app.route("/inventaire")
def table_inventaire():
    con = None
    #response = []
    try:
        con = connect()
        cur = con.cursor();
        cur.execute("SELECT * FROM inventaireglobal_ftth ;")
        response = cur.fetchall()
        #print("Response data is ok ...")
        cur.close()
        con.commit()
        return response
        #print("Database closed .....")
    except (Exception, psycopg2.DatabaseError) as error:
        print("The database error " + error )
    finally:
        if con is not None:
            con.close()
    #return response

# simple inventaire info
@app.route('/simpleinventaire')
def simpleinventaire():
    #data = []
    con = None
    try:
        con = connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM inventaireglobal_ftth ;")
        data = cur.fetchall()
        cur.close()
        con.commit()
        #return jsonpickle.encode(data)
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    return jsonpickle.encode(data)

# Keycloak test
@app.route('/token_login/', methods=['POST'])
def get_token():
    body = request.get_json()
    for field in ['username', 'password']:
        if field not in body:

            return  ("Error :::::::: Field {field}  is missing! , 400")

    data = {
        'grant_type': 'password',
        'client_id': 'test'
    }

# function pour obtenir les variables d'env

def sysEnvOrDefault(envVar, defaultVal):
    if os.getenv(envVar):
        return os.getenv(envVar)
    return defaultVal

# Recuperation des variables
CLIENT_ID = cfg()['CLIENT_ID']
CLIENT_SECRET = cfg()['CLIENT_SECRET']
GRANT_TYPE = cfg()['GRANT_TYPE']
#HOST = cfg()['CLIENT_ID']
#PORT = sysEnvOrDefault("PORT", app.config['PORT'])
URI = cfg()['URI']
URI_USER = cfg()['URI_USER']
URI_ROLES = cfg()['URI_ROLES']
REALM = cfg()['REALM']
URI_BASE = cfg()['URI_BASE']

print("CLIENT_ID" + CLIENT_ID + "CLIENT_SECRET" + CLIENT_SECRET + "GRANT_TYPE" + GRANT_TYPE + "URI" + URI + "URI_USER" + URI_USER + "URI_ROLES" + URI_ROLES + "REALM" + REALM + "URI_BASE" + URI_BASE)
















# le headers
# def add_headers(response):
#     response.headers.add('Content-Type', 'application/json')
#     response.headers.add('X-Frame-Options', 'SAMEORIGIN')
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
#     return response
#
# # creation des fonctions relatifs à Keycloak
# def adminToken():
#     data = {
#         'grant_type': 'client_credentials',
#         'client_id': CLIENT_ID,
#         'client_secret': CLIENT_SECRET,
#     }
#     url = URI
#     response = requests.post(url, data=data)
#
#     if response.status_code > 200:
#         return {"message": "Username ou password Incorrect", 'status': 'error'}
#     tokens_data = response.json()
#     ret = {
#         'tokens' : {
#             "access_token": tokens_data['access_token'],
#             "token_type": tokens_data['token_type'],
#         },
#         "status": 'success',
#     }
#     return ret
# # fin de la creation des fonctions relatis à keycloak
#
# fonction de récupération des variables d'environnement
# def sysEnvOrDefault(envVar, defaultVal):
#     if os.getenv(envVar):
#         return os.getenv(envVar)
#     return defaultVal
#
# # Les fichiers de ressources
#
# CLIENT_ID = sysEnvOrDefault("CLIENT_ID", app.config['CLIENT_ID'])
# CLIENT_SECRET = sysEnvOrDefault("CLIENT_SECRET", app.config['CLIENT_SECRET'])
# OPENID_URL = sysEnvOrDefault("OPENID_URL", app.config['OPENID_URL'])
# ADMIN_USER = sysEnvOrDefault("ADMIN_USER", app.config['ADMIN_USER'])
# ADMIN_PASS = sysEnvOrDefault("ADMIN_PASS", app.config['ADMIN_PASS'])
# REALM = sysEnvOrDefault("REALM", app.config['REALM'])
# KEYCLOAK_URI = sysEnvOrDefault("KEYCLOAK_URI", app.config['KEYCLOAK_URI'])
#
# # Test de Keycloak
# CORS(app)
# SECRET_KEY = 'test_secret_key'
#
# app.config.update({
#     'SECRET_KEY': SECRET_KEY,
#     'TESTING': True,
#     'DEBUG': True,
#     'OIDC_CLIENT_SECRETS': 'client_secrets_templates.json',
#     'OIDC_OPENID_REALM': 'hysds',
#     'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
#     'OIDC_TOKEN_TYPE_HINT': 'access_token',
#     'OIDC-SCOPES': ['openid']
# })

# class NewOpenIDConnect(OpenIDConnect):
#     def accept_token_modified(self, require_token=False, scopes_required=None, render_errors=True):
#         def wrapper(view_func):
#             @wraps(view_func)
#             def decorated(*args, **kwargs):
#                 print('HEADERS ################################"')
#                 print(request.headers)
#
#                 if True:
#                     print("Skip authenticating...")
#                     return view_func(*args, **kwargs)
#
#                 print("request coming through proxy, authenticating...")
#                 token = None
#
#                 if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer'):
#                     token = request.headers['Authorization'].split(None, 1)[1].strip()
#                 if 'access_token' in request.form:
#                     token = request.form['access_token']
#                 elif 'access_token' in request.args:
#                     token = request.args['access_token']
#
#                 validity = self.validate_token(token, scopes_required)
#                 if (validity is True) or (not require_token):
#                     return view_func(*args, **kwargs)
#                 else:
#                     response_body = {
#                         'error': 'invalid_token',
#                         'error_description': validity
#                     }
#                     if render_errors:
#                         response_body = json.dumps(response_body)
#                     return response_body, 401, {'WWW-Authenticate': 'Bearer'}
#                 return decorated
#             return wrapper
#
# oidc = NewOpenIDConnect(app)
#
# @app.route('/saytutest', methods=['GET'])
# def no_token_api():
#     return jsonify({
#         'results': 'No Need for token'
#     })
#
# @app.route('/api/test', methods=['GET'])
# @oidc.accept_token(require_token=True)
# def test_token_api():
#     print('HEADERS ###################################')
#     print(request.headers)
#     payload = g.oidc_token_info
#     print(json.dumps(payload, indent=2))
#
#     return jsonify({ 'succes': True, 'payload': payload})
#
# @app.route('/api/optional', methods= ['GET'])
# @oidc.accept_token_modified(require_token=True)
# def test_optional_token():
#     return jsonify({
#         'success': True,
#         "message": "testing the /api/optional endpoint"
#     })




# Executer le programme
if __name__ == '__main__':
    #create_table_inventaire()
    app.run(debug=True)

