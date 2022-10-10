from flask import Flask, request, jsonify, Config
from script.function import *
import yact
import requests
import flask

app = Flask(__name__)


class YactConfig(Config):
    def from_yaml(self, config_file, directory=None):
        config = yact.from_file(config_file, directory=directory)
        for section in config.sections:
            self[section.upper()] = config[section]


def cfg():
    with open(os.path.dirname(os.path.abspath(__file__)) + './script/config.yaml', "r") as ymlfile:
        cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)
        return cfg


#  Les fonctions utiles
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')

    return response


# La fonction adminToken
def adminToken():
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    url = URI

    response = requests.post(url, data=data)

    if response.status_code > 200:
        return {"message": "Username ou Password Incorrect", 'status': 'error'}
    tokens_data = response.json()
    ret = {
        'tokens': {"access_token": tokens_data['access_token'],
                   "token_type": tokens_data['token_type'],
                   },
        "status": 'success',
    }
    return ret


# la fonction error

def error(message):
    return jsonify({
        'success': False,
        'message': message
    })


# la fonction create_users
@app.route('/users/', methods=['POST'])
def create_user():
    try:
        headers = flask.request.headers
        # data_token = decodeToken(token)
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data_token = decodeToken(token)
        code = data_token['code']
        name = data_token['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin':
                url = URI_USER

                body = request.json
                for field in ['firstName', 'lastName', 'username', 'password']:
                    if field not in body:
                        return error(f"Field {field} is missing"), 400
                data = {
                    "firstName": body['firstName'],
                    "lastName": body['lastName'],
                    "enabled": "true",
                    "username": body['username'],
                    "credentials": [
                        {
                            "type": "password",
                            "value": body['password'],
                            "temporary": False

                        }
                    ]
                }
                # return data
                donnee = adminToken()
                headers = get_keycloak_headers()
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 400:
                    return {"message": "Le nom de l'utilisateur existe deja", 'status': 'error',
                            'code': response.status_code}
                if response.status_code > 201:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                response = jsonify(
                    {'status': 'Success', 'data': 'Utilisateur Cree avec success', 'code': HTTPStatus.OK})
                # Mettre ici les logs
                return add_headers(response)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)

        # code = decodeToken(token)['code']

    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# creation de la fonction get_keycloak_headers
def get_keycloak_headers():
    donnee = adminToken()
    token_admin = donnee['tokens']['access_token']
    return {
        'Authorization': 'Bearer' + token_admin,
        'Content-type': 'application/json'
    }


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World! WELCOME TO Saytu Network Backend'


@app.route('/auth', methods=['POST'])
def get_token():
    # TODO : Control username et password
    body = request.json

    data = {

        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": 'password',
        'username': body['username'],
        'password': body['password']
    }

    url = URI
    response = requests.post(url, data=data)
    if response.status_code > 200:
        messageLogging = body['username'] + "a tente de se connecter"
        return {"message": "Username ou Password Incorrect", 'code': HTTPStatus.BAD_REQUEST}

    tokens_data = response.json()

    ret = {
        'tokens': {
            "access_token": tokens_data['access_token'],
            "refresh_token": tokens_data['refresh_token'],
        }
    }
    messageLogging = body['username'] + "s'est connecté avec success"

    return jsonify({"message": "ok", "codes": 200}, ret), 200


# La fonction get_user_by_id
def get_user_by_id(userId):
    try:
        url = URI_USER + '/' + userId
        donnee = adminToken()
        token_admin = donnee['tokens']['access_token']
        response = requests.get(url,
                                headers={'Authorization': 'Bearer {}'.format(token_admin)})
        if response.status_code > 200:
            return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
        tokens_data = response.json()
        data = {
            "enabled": tokens_data['enabled'],
            "id": tokens_data['id'],
            "firstName": tokens_data['firstName'],
            "lastName": tokens_data['lastName'],
            "username": tokens_data['username'],
        }
        response = {'status': 'Success', 'data': data, 'code': HTTPStatus.OK}
        return response
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# la fonction get_info_user
def get_info_user(userId):
    try:
        url = URI_USER + '/' + userId + '/role-mappings/realm'
        donnee = adminToken()
        token_admin = donnee['tokens']["access_token"]
        response = requests.get(url,
                                headers={'Authorization': 'Bearer {}'.format(token_admin)})
        if response.status_code > 200:
            return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
            tokens_data = response.json
            data = {
                "name": tokens_data[0]['name'],
                "id": tokens_data[0]['id']
            }
            return data
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# api de recupération des users

@app.route('/users/', methods=['GET'])
def all_users():
    print(decodeToken(request.headers.get('Authorization').split()[1]))
    #ffdecodeToken()
    try:
        headers = flask.request.headers
        #print
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {"message": "invalid token roel", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token orl", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token rlo", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        code = data['code']
        #name = data['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':

                url = URI_USER + '?max=1000'
                donnee = adminToken()
                token_admin = donnee['tokens']["access_token"]
                response = requests.get(url,
                                        headers={'Authorization': 'Bearer {}'.format(token_admin)})
                if response.status_code > 200:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()
                # return tokens_data[0]
                result = []
                for i in range(len(tokens_data)):
                    data = {
                        "enabled": tokens_data[i]['enabled'],
                        "id": tokens_data[i]['id'],
                        "firstName": tokens_data[i]['firstName'].split(' ', 1)[0],
                        "lastName": tokens_data[i]['lastName'].upper(),
                        "username": tokens_data[i]['username'],
                        "profil": get_info_user(tokens_data[i]['id']),
                    }
                    result.append(data)
                # return result
                response = jsonify({'status': 'Success', 'data': result, 'code': HTTPStatus.OK})
                # messageLogging = name + " a consulté la liste des utilisateurs "
                # message_log = {
                #     "url.path": request.base_url,
                #     "http.request.method": request.method,
                #     "client.ip": getIpAdress(),
                #     "event.message": messageLogging,
                #     "process.id": os.getpid(),
                # }
                # log_app(message_log)
                # logger_user(messageLogging, LOG_AUTHENTIFICATION)
                return add_headers(response)
            # messageLogging = name + " a tenté de consulter la liste des utilisateurs "
            # message_log = {
            #     "url.path": request.base_url,
            #     "http.request.method": request.method,
            #     "client.ip": getIpAdress(),
            #     "event.message": messageLogging,
            #     "process.id": os.getpid(),
            # }
            # log_app(message_log)
            # logger_user(messageLogging, LOG_AUTHENTIFICATION)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# Recuperation des variables
CLIENT_ID = cfg()['CLIENT_ID']
CLIENT_SECRET = cfg()['CLIENT_SECRET']
GRANT_TYPE = cfg()['GRANT_TYPE']
# HOST = cfg()['CLIENT_ID']
# PORT = sysEnvOrDefault("PORT", app.config['PORT'])
URI = cfg()['URI']
URI_USER = cfg()['URI_USER']
URI_ROLES = cfg()['URI_ROLES']
REALM = cfg()['REALM']
URI_BASE = cfg()['URI_BASE']

print(
    "CLIENT_ID" + CLIENT_ID + "CLIENT_SECRET" + CLIENT_SECRET + "GRANT_TYPE" + GRANT_TYPE + "URI" + URI + "URI_USER" + URI_USER + "URI_ROLES" + URI_ROLES + "REALM" + REALM + "URI_BASE" + URI_BASE)
field = "aziz"
print(f"error() : Field {field} is missing", 400)

if __name__ == '__main__':
    app.run(debug=True)
