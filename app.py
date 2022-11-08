from flask import Flask, request, jsonify, Config
# from psycopg2 import cursor
from script.function import *
from script.function_post import *
from script.conf import *
from script.main_function import *
from script.account import *
import yact
import requests
import flask
import psycopg2
from flask_cors import CORS
import pandas as pd
from datetime import datetime
from datetime import date

import jsonpickle

app = Flask(__name__)
CORS(app)

# Recuperation des variables
# TODO : doit inclure le host et le port
CLIENT_ID = configuration()['CLIENT_ID']
CLIENT_SECRET = configuration()['CLIENT_SECRET']
GRANT_TYPE = configuration()['GRANT_TYPE']
URI = configuration()['URI']
URI_USER = configuration()['URI_USER']
URI_ROLES = configuration()['URI_ROLES']
REALM = configuration()['REALM']
URI_BASE = configuration()['URI_BASE']

# simple inventaire info
@app.route('/simpleinventaire')
def simpleinventaire():
    return simple_inventaire()



# requete historique/date
@app.route('/historique', methods=['POST'])
def historique():
    return get_historique_by_date()

# Good doublons
@app.route('/listedoublons', methods=['GET'])
def GetDoublon():
    return get_doublon()

# Liste des coupures
@app.route('/listecoupures', methods=['GET'])
def GetCoupure():
    return get_coupure()


# Historique Taux d'utilisation du débit
@app.route('/historiquetauxutilisation', methods=['GET'])
def TauxUtilisationDebit():
    return taux_utilisation_debit()

# Historique des coupures
@app.route('/historiquecoupures', methods=['GET'])
def GetHistoriqueCoupure():
    return get_historique_coupure()

# return historique
@app.route('/get_historique', methods=['GET', 'POST'])
def get_historique_():
    con = connect()
    if request.method == 'GET':
        res = get_historique()
    if request.method == 'POST':
        data = request.get_json()
        date = data['date']
        if date is not None and date != "":
            # Mettre ici la requete
            query = "Select numero, date_, created_at from historique_diagnostic where anomalie like '%Coupure%' and (NOW()::date  -  date_) >= 30 ;"
            data_ = pd.read_sql(query, con)
            print(data_)

            res = get_historique()
        else:
            return "ERROR 404", 404
    return


@app.route('/get_test_historique', methods=['GET', 'POST'])
def get_test_historique():
    con = connect()
    if request.method == 'GET':
        res = get_historique()
    if request.method == 'POST':
        data = request.get_json()
        dateFrom = data['dateFrom']
        dateTo = data['dateTo']
        Duree = data['Duree']
        if dateFrom is not None and dateFrom != "" and dateTo is not None and dateTo != "":
            print(dateFrom)
            print(dateTo)
        query = "Select numero, count(numero) FROM maintenance_predictive_ftth WHERE date BETWEEN '{}'  AND  '{}' GROUP BY numero HAVING COUNT(numero) = {}".format(
            dateFrom, dateTo, Duree)
        data_ = pd.read_sql(query, con)
        print(data_)
        res = data_.to_dict(orient='records')
        return res
    return res


# Fontion de test des args
@app.route('/with_parameters')
def with_parameters():
    name = request.args.get('name')
    age = request.args.get('age')
    return jsonify(message="My name is" + str(name) + "and I am" + str(age))


@app.route('/with_url_variables/<string:name>/<int:age>')
def with_url_variables(name: str, age: int):
    return jsonify(message="My name is" + name + " and I am" + str(age) + "Years old")


@app.route('/index/<subject>')
def subject(subject):
    return "The value is: " + subject


@app.route('/posteee/<int:post_id>/<string:test>')
def show_post(post_id, test):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}, Test' + str(test)


@app.route('/test_query')
def test_query():
    # data = []
    con = None
    try:
        con = connect()
        cur = con.cursor()
        cur.execute("SElect * from historique_diagnostic limit 4 ;")
        data = cur.fetchall()
        cur.close()
        con.commit()
        # return jsonpickle.encode(data)
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
    return data


def datebetween(date1, date2):
    date1 = datetime.strptime(date1, "%Y-%m-%d")
    date2 = datetime.strptime(date2, "%Y-%m-%d")
    duree = date2 - date1
    return duree


@app.route('/testdatee', methods=['POST', 'GET'])
def testdatee():
    date1 = request.args.get('date1')
    date2 = request.args.get('date2')

    print(type(date1))
    print(type(date2))
    print("Date 1 is" + date1 + "Date 2 is" + date2)
    # date1 = datetime.strptime()
    date1 = datetime.strptime(date1, '%Y-%m-%d')
    date2 = datetime.strptime(date2, '%Y-%m-%d')
    date1 = date1.date()
    date2 = date2.date()

    print(type(date1))
    print(type(date2))
    delta = date2 - date1
    print("La duree est de :")
    print(delta.days)
    # print("Date 1 is" + date1 + "Date 2 is" + date2)
    return "print(type(date1)) i "


@app.route('/datee', methods=['POST', 'GET'])
def get_Date_Diff():
    con = connect()

    dateFrom = request.args.get('dateFrom')
    dateTo = request.args.get('dateTo')

    print(type(dateFrom))
    print(type(dateTo))

    print("Date iss" + dateFrom + "Date To is" + dateTo)
    dateFrom = datetime.strptime(dateFrom, '%Y-%m-%d')
    dateTo = datetime.strptime(dateTo, '%Y-%m-%d')

    dateFrom = dateFrom.date()
    dateTo = dateTo.date()

    print(type(dateFrom))
    print(type(dateTo))

    Duree = dateTo - dateFrom

    print("La duree est de")
    print(Duree.days)
    Duree = Duree.days
    # Duree = request.args.get('Duree')
    # print("DateFrom is " + dateFrom + "DateTo is " + dateTo + "and Duree is " + Duree)
    print(type(dateFrom))
    print(type(dateTo))
    if dateFrom is not None and dateFrom != "" and dateTo is not None and dateTo != "":
        print(dateFrom)
        print(dateTo)
    query = "Select numero, ip, anomalie, nom_olt,  count(numero) as Dureee FROM maintenance_predictive_ftth WHERE date BETWEEN '{}'  AND  '{}' GROUP BY numero, ip, anomalie, nom_olt HAVING COUNT(numero) = {}".format(
        dateFrom, dateTo, Duree)
    data_ = pd.read_sql(query, con)
    print(data_)
    res = data_.to_dict(orient='records')
    return res

    # return 'From Date is'+request.args.get('from_date') + ' To Date is ' + request.args.get('to_date')



# La fonction qui retourne les numeros en doublon
@app.route('/doublonstest', methods=['GET'])
def getDoublon():
    if request.method == 'GET':

        con = connect()

        numero = request.args.get('numero')
        # print(type(numero))
        # print("le numero saisi est" + numero)

        if numero is None or numero == "":
            return getAllDoublon()
        else:

            query = ''' 
                            Select db.service_id, db.created_at::date, db.nom_olt, db.ip_olt, db.vendeur, mt.oltrxpwr, mt.ontrxpwr
                                From doublons_ftth as db, metric_seytu_network as mt
                                where db.service_id = mt.numero 
                                and db.ip_olt = mt.olt_ip
                                and db.service_id = '{}'  order by db.created_at::date desc
                        '''.format(numero)
            data_ = pd.read_sql(query, con)
            print(data_)
            res = data_.to_dict(orient='records')
            return res


# API pour l'affichage de la dernière date de coupure
@app.route('/derniereheureCoupure', methods=['GET'])
def get_Heure_Coupure():
    if request.method == 'GET':

        con = connect()
        numero = request.args.get('numero')
        # print(type(numero))
        # print("le numero saisi est" + numero)
        if numero is None or numero == "":
            return getDerniereHeureDeCoupure()
        else:

            query = '''
                        Select numero,nom_olt, ip, vendeur, anomalie, criticite, created_at
                               from maintenance_predictive_ftth
                               where numero = '{}' 
                               order by created_at DESC limit 1
                    '''.format(numero)
            data_ = pd.read_sql(query, con)
            print(data_)
            res = data_.to_dict(orient='records')
            return res


# La fonction de récupération du taux d'ocuupation
@app.route('/tauxoccupation', methods=['GET'])
def tauxOccupation():
    con = connect()
    dateFrom = request.args.get('dateFrom')
    dateTo = request.args.get('dateTo')

    if dateFrom is not None and dateFrom != "" and dateTo is not None and dateTo != "":

        query = ''' 
                    select slot,  pon, nom_olt,created_at::date, count(distinct service_id) 
                    from inventaireglobal_ftth where created_at::date between '{}' and '{}'
                    group by pon, slot,nom_olt,created_at::date
                '''.format(dateFrom, dateTo)
        data_ = pd.read_sql(query, con)
        print(data_)
        res = data_.to_dict(orient='records')
        return res
    else:
        return "Veullez saisir une date"


# API de l'historissation du taux d'occupation
@app.route('/testgitt')
def HistoriqueTauxOccupation():
    return testQuery()


# Test de la fonction d'activation
@app.route('/users/testActivation/<string:userId>/', methods=['GET'])
def testActivation(userId):
    try:
        headers = flask.request.headers
        reponse = get_user_by_id(userId)
        if reponse.get("status") == 'error':
            return {'message': 'Utilisateur Not Found', 'code': HTTPStatus.NOT_FOUND}
        else:
            return {'message': 'Good User', 'code': 200}
        # headerss = flask.request.headers
        # print("------------------------------Le headerrs est-----------------------")
        # print(headerss)
        # return jsonify({"test": headerss})#print(headers)
    except:
        print("------------------------------Mauvais  Headers------------------")


# la fonction d'activation de l'utilisateur


# creation de la fonction get_keycloak_headers


@app.route('/')
def hello_world():  # put application's code here
    return 'WELCOME TO Saytu Network Backend'


def get_keycloak_headers():
    donnee = testGetTokenUserAdmin()
    token_admin = donnee['tokens']['access_token']
    return {
        'Authorization': 'Bearer ' + token_admin,
        'Content-Type': 'application/json'
    }


@app.route('/auth', methods=['POST'])
def GetToken():
    # TODO : Control username et password
    body = request.get_json(force=True)

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
        messageLogging = body['username'] + " a tenté de se connecter sans success "
        message_log = {
            "url.path": request.base_url,
            "http.request.method": request.method,
            "client.ip": getIpAdress(),
            "event.message": messageLogging,
            "process.id": os.getpid(),
        }
        log_app(message_log)
        print('-----------------------LOG--------------------')
        print(message_log)

        return {"message": "Username ou Password Incorrect", 'code': HTTPStatus.BAD_REQUEST}

    tokens_data = response.json()

    ret = {
        'tokens': {
            "access_token": tokens_data['access_token'],
            "refresh_token": tokens_data['refresh_token'],
        }
    }

    messageLogging = body['username'] + " s'est connecté avec success"
    message_log = {
        "url.path": request.base_url,
        "http.request.method": request.method,
        "client.ip": getIpAdress(),
        "event.message": messageLogging,
        "process.id": os.getpid(),
    }
    log_app(message_log)

    print('-----------------------LOG--------------------')
    print(message_log)

    return jsonify(ret), 200

    # return jsonify({"message": "ok", "codes": 200}, ret), 200


# Test Get User By ID
@app.route('/testGetUserId', methods=['GET'])
def testGetUserId():
    try:
        userId = '64b43eff-fcdf-4394-b207-0f067afd7894'
        url = URI_USER + '/' + userId
        print("----------------le url recuperer est-------------------")
        print(url)
        donnee = adminToken()
        token_admin = donnee['tokens']['access_token']
        print("---------------le token admin est-----------------")
        print(token_admin)
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
        status = response.status_code
        tokens_data = response.json()

        # print(data)
        # data = {lllououoooukykykykyky
        #     "enabled": tokens_data['enabled'],
        #     "id": tokens_data['id'],
        # }
        # print("---")
        return {'message': 'good', 'code': 200, 'status status': status, 'token': token_admin}
        # return {'code':0}
    except:
        print("-----------ERRORR------------------")


# Fonction de test d'activaton
@app.route('/users/activation/', methods=['GET'])
def activation_users():
    try:
        headers = flask.request.headers
        response = get_user_by_id('64b43eff-fcdf-4394-b207-0f067afd7894')
        # if response.get("status") == 'error':
        #     return {"message": "l'utilisateur n'est pas trouve", 'code': HTTPStatus.NOT_FOUND}
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                else:
                    return {'message': 'token invalid 1'}
            else:
                return {'message': 'token invalid 2'}
        else:
            return {'message': 'token invalid 3'}

    except:
        print("-------------ERRORR--------")
        return {"Good": "response"}


# Fonction permettant de tester l'obtention du to2ken Simple User
@app.route('/testGetTokenUserAdmin', methods=['GET'])
def testGetTokenUserAdmin():
    url = "https://keycloak-pprod.orange-sonatel.com/auth/realms/Saytu_realm/protocol/openid-connect/token"
    params = {
        'client_id': 'saytu_keycloak_python',
        'grant_type': 'client_credentials',
        'client_secret': '5b00ff07-a482-417d-8aff-0e5d83045078',
        # 'username': 'dbm_user',
        # 'password': 'Aziz_2030'
    }
    response = requests.post(url, params, verify=False)
    if response.status_code > 200:
        return {'message': 'Username ou Password Incorrect', 'status': 'error'}
    tokens_data = response.json()
    ret = {
        'tokens': {
            'access_token': tokens_data['access_token'],
            'token_type': tokens_data['token_type'],
        },
        'status': 'success',
    }
    print(response)
    return ret  # jsonify({'message':'ok', "token": response.json()})


# Fonction permettant de tester l'obtention du token Admin
@app.route('/testGetTokenUserSimple', methods=['GET'])
def testGetTokenUserSimple():
    url = "https://keycloak-pprod.orange-sonatel.com/auth/realms/Saytu_realm/protocol/openid-connect/token"
    params = {
        'client_id': 'saytu_keycloak_python',
        'grant_type': 'password',
        'client_secret': '5b00ff07-a482-417d-8aff-0e5d83045078',
        'username': 'aziz',
        'password': 'test'
    }
    x = requests.post(url, params, verify=False)
    print(x)
    return jsonify({'message': 'ok', "token": x.json()})


# Fonction de test du get user by ID
@app.route('/testGetUserByID', methods=['GET'])
def GetUserByID(userId):
    try:

        URI_USER = 'https://keycloak-pprod.orange-sonatel.com/auth/admin/realms/saytu_realm/users'
        # userId = '97a28af5-89ad-445b-87e6-4e83afcab8fe'
        # userId = '64b43eff-fcdf-4394-b207-0f067afd7894'
        # userName = 'aziz'
        url = URI_USER + '/' + userId
        # urls = URI_USER + '?username=' + userName
        print('-----------------------le url recuperer est----------------')
        print(url)
        donnee = testGetTokenUserAdmin()
        print('-----------------------le url avec userName recuperer est----------------')
        # print(urls)
        donnee = testGetTokenUserAdmin()
        token_admin = donnee['tokens']['access_token']
        print('---------------le token Admin recuperer est ---------')
        print(token_admin)
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
        # if response.status_code > 200:
        #     return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
        # tokens_data = response.json()
        status = response.status_code
        if status > 200:
            return {'message': 'Erreur', 'status': 'error', 'code': status}
        tokens_data = response.json()
        print("--------------la reponse renvoye  est-----------")
        print(tokens_data)
        print("---------------le status recuperer---------------")
        print(status)
        data = {
            "enabled": tokens_data['enabled'],
            "id": tokens_data['id'],
            "firstName": tokens_data['firstName'],
            "lastName": tokens_data['lastName'],
            "username": tokens_data['username'],
        }
        response = {'status': 'Success', 'data': data, 'code': HTTPStatus.OK}
        return response
        # return {'message': 'test', 'status': status, 'code': 200}
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})
        # Do Something


# la fonction permettant d'avoir tous les info user
@app.route('/testGetInfoUser', methods=['GET'])
def GetInfoUser(userId):
    try:

        URI_USER = 'https://keycloak-pprod.orange-sonatel.com/auth/admin/realms/saytu_realm/users'
        # userId = '64b43eff-fcdf-4394-b207-0f067afd7894'
        url = URI_USER + '/' + userId + '/role-mappings/realm'
        donnee = testGetTokenUserAdmin()
        token_admin = donnee['tokens']['access_token']
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
        if response.status_code > 200:
            return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
        tokens_data = response.json()
        data = {
            "name": tokens_data[0]['name'],
            "id": tokens_data[0]['id']

        }
        print("la data recuper est --------------------------------------------------")
        print(data)

        return data
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API pour consulter la liste des utilisateurs
@app.route('/users/', methods=['GET'])
def GetAllUsers():
    try:

        headers = flask.request.headers
        if request.headers.get('Authorization'):
            if request.headers.get('Authorization').startswith('Bearer'):
                bearer = headers.get('Authorization')
                taille = len(bearer.split())
                if taille == 2:
                    token = bearer.split()[1]
                    print('--------------------le token retourne est--------------------')
                    print(token)
                    data = {'message': 'token valid', 'token retourne': token}
                    print(data)
                    # return data
                else:
                    return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
            else:
                return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

        data = decodeToken(token)
        print('--------------------------la data renvoye est-------------------')
        print(data)
        code = data['code']
        name = data['data']['name']

        if code == 200:
            data = {"code": code, "name": name, "data": data}
            print(data)
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':
                print('-------------le role est ---------------')
                print(getRoleToken(token))

                url = URI_USER + '?max=1000'
                donnee = testGetTokenUserAdmin()
                token_admin = donnee['tokens']['access_token']
                response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
                if response.status_code > 200:
                    return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()
                result = []
                for i in range(len(tokens_data)):
                    data = {
                        'enabled': tokens_data[i]['enabled'],
                        'id': tokens_data[i]['id'],
                        'firstName': tokens_data[i]['firstName'],
                        'lastName': tokens_data[i]['lastName'],
                        'username': tokens_data[i]['username'],
                        'profil': GetInfoUser(tokens_data[i]['id']),

                    }
                    result.append(data)
                response = jsonify({'status': 'Success', 'data': result, 'code': HTTPStatus.OK})
                messageLogging = name + " a consulté la liste des utilisateurs "
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),

                }
                log_app(message_log)
                return add_headers(response)
            messageLogging = name + "a tenté de consulter la liste des utilisateurs"
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": getIpAdress(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)

            return {'message': 'invalid user', 'code': HTTPStatus.UNAUTHORIZED}
        else:

            return decodeToken(token)

            # return data
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant l'obtention d'un seul user
@app.route('/users/<string:userId>/', methods=['GET'])
def GetOnlyUser(userId):
    try:
        headers = flask.request.headers
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

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        donneerec = {'code': code, 'name': name}
        print('-------------------la data recuperer est-------------')
        print(donneerec)
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':

                url = URI_USER + '/' + userId
                donnee = testGetTokenUserAdmin()
                token_admin = donnee['tokens']['access_token']
                response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
                if response.status_code > 200:
                    return {'message': 'Erreur', 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()

                response = jsonify({'status': 'Success', 'data': tokens_data, 'code': HTTPStatus.OK})
                GetUserByID(userId)

                messageLogging = name + " a consulté l'utilisateur " + GetUserByID(userId)['data']['username']
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)

                return add_headers(response)
            messageLogging = name + " a tenté de consulter l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": getIpAdress(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            return {"message": "invalid user", "code": HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de creer un utitlisateur
@app.route('/users', methods=['POST'])
def CreateUser():
    try:
        headers = flask.request.headers
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
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # ceci est un test : les roles de creation des users doivent etre établis par la matrice de reponsabilite

                url = URI_USER

                body = request.get_json()
                # for field in ['firstName', 'lastName', 'username', 'password']:
                #     if field not in body:
                #         return error(f"Field {field} is missing!"), 400

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

                donnee = testGetTokenUserAdmin()
                headers = get_keycloak_headers()
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 409:
                    return {"message": "Le nom de l'utilisateur existe Déjà", 'status': 'error',
                            'code': response.status_code}
                if response.status_code > 201:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                response = jsonify({'status': 'Success', 'data': 'Utilisateur Créé avec succès', 'code': HTTPStatus.OK})
                messageLogging = name + " a cree l'utilisateur " + body['firstName'] + ' ' + body[
                    'lastName'] + '' + ' de username ' + body['username']
                # logger_user(messageLogging, LOG_AUTHENTIFICATION)
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                return add_headers(response)
            # messageLogging = name + " a tenté de creer l'utilisateur " + body['firstName'] + ' ' + body[
            #         'lastName'] + '' + ' de username' + body['username']
            # logger_user(messageLogging, LOG_AUTHENTIFICATION)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# API permettant de modifier les params d'un utilisateur
@app.route('/users/<string:userId>/', methods=['PUT'])
def UpdateUser(userId):
    try:
        headers = flask.request.headers
        reponse = GetUserByID(userId)
        prenom = reponse.get("data")["firstName"]
        nom = reponse.get("data")["lastName"]
        login = reponse.get("data")["username"]

        if reponse.get("status") == 'error':
            return {"message": "User Not Found", 'code': HTTPStatus.NOT_FOUND}
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
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # ceci est un test Ne doit posseder que le role admin
                url = URI_USER + '/' + userId

                body = request.get_json()
                # TODO : les controles doivent etre faites ici : firstName, lastName ...
                data = {
                    "firstName": body['firstName'],
                    "lastName": body['lastName'],
                    # "enabled": body['enabled'],
                    "username": body['username'],

                    "credentials": [
                        {
                            "type": "password",
                            "value": body['password'],
                            "temporary": False
                        }
                    ]
                }

                donnee = testGetTokenUserAdmin()
                token_admin = donnee['tokens']["access_token"]
                headers = get_keycloak_headers()
                response = requests.put(url, headers=headers, json=data)
                if response.status_code > 204:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                response = jsonify(
                    {'status': 'Success', 'data': 'Utilisateur modifie avec success', 'code': HTTPStatus.OK})
                messageLogging = name + " a modifie l'utilisateur " + prenom + ' ' + nom + '' + ' de username ' + login + " en " + \
                                 body['firstName'] + ' ' + body['lastName'] + '' + ' de username ' + body['username']

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)

                return add_headers(response)
            messageLogging = name + " a tenté de modifier l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": getIpAdress(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)

            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)

    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant d'activer l'utilisateur
@app.route('/users/enable/<string:userId>/', methods=['PUT'])
def EnableDisableUser(userId):
    try:
        headers = flask.request.headers
        reponse = GetUserByID(userId)

        if reponse.get("status") == 'error':
            return {"message": "User Not Found", 'code': HTTPStatus.NOT_FOUND}
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
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':  # Le sf est à ommettre , ceci est un test
                url = URI_USER + '/' + userId
                body = request.get_json()

                data = {
                    "enabled": not body['enabled'],
                }

                donnee = testGetTokenUserAdmin()
                token_admin = donnee['tokens']["access_token"]
                headers = get_keycloak_headers()
                response = requests.put(url, headers=headers, json=data)

                if response.status_code > 204:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                response = jsonify(
                    {'status': 'Success', 'data': 'Utilisateur Activé/Desactivé avec success', 'code': HTTPStatus.OK})
                if not body['enabled'] == True:
                    print('ok')
                    messageLogging = name + " a désactivé l'utilisateur " + GetUserByID(userId)['data']['username']
                else:
                    print('ok')
                    messageLogging = name + " a activé l'utilisateur " + GetUserByID(userId)['data']['username']

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                return add_headers(response)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)



    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de supprimer un utilisateur
@app.route('/users/<string:userId>/', methods=['DELETE'])
def DeleteUser(userId):
    try:
        headers = flask.request.headers
        reponse = GetUserByID(userId)
        if reponse.get("status") == 'error':
            return {"message": "User Not Found", 'code': HTTPStatus.NOT_FOUND}
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
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # sf n'est pas autorisé seull admin doit pouvoir faire cette demande

                url = URI_USER + '/' + userId
                donnee = testGetTokenUserAdmin()
                token_admin = donnee['tokens']["access_token"]
                headers = get_keycloak_headers()
                messageLogging = name + " a supprimé l'utilisateur " + GetUserByID(userId)['data']['username']
                response = requests.delete(url, headers=headers)

                if response.status_code > 204:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)

                response = jsonify(
                    {'status': 'Success', 'data': 'Utilisateur supprimé avec success', 'code': HTTPStatus.OK})

                return add_headers(response)
            messageLogging = name + " a tenté de supprimer l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": getIpAdress(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de visualiser les profils des utilisateurs
@app.route('/profils/', methods=['GET'])
def AllProfils():
    try:

        headers = flask.request.headers
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

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':

                url = URI_ROLES
                donnee = testGetTokenUserAdmin()
                token_admin = donnee['tokens']["access_token"]
                response = requests.get(url,
                                        headers={'Authorization': 'Bearer {}'.format(token_admin)})
                if response.status_code > 200:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()
                # return jsonify(tokens_data)
                # input_dict = json.loads(tokens_data)

                # Filter python objects with list comprehensions
                output_dict = [x for x in tokens_data if
                               x['name'] == 'admin' or x['name'] == 'profil_1' or x[
                                   'name'] == 'profil_3' or x['name'] == 'sf' or x['name'] == 'profil_4']

                # Transform python object back into json
                # output_json = json.dumps(output_dict)

                response = jsonify({'status': 'Success', 'data': output_dict, 'code': HTTPStatus.OK})
                messageLogging = name + " a consulté la liste des profils "
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                # logger_user(messageLogging, LOG_AUTHENTIFICATION)
                return add_headers(response)
            messageLogging = name + " a tenté de consulter la liste des profils "
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": getIpAdress(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            # logger_user(messageLogging, LOG_AUTHENTIFICATION)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# API permettant de creer le profil d'un utilisateur
@app.route('/profils/', methods=['POST'])
def CreateProfils():
    try:

        headers = flask.request.headers
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

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(token) == 'sf':

                body = request.get_json()
                # TODO : a mettre les restrictions sur name

                data = {
                    "name": body["name"],
                    "composite": False,
                    "clientRole": False,
                    "containerId": "Saytu_realm"
                }
                url = URI_ROLES
                headers = get_keycloak_headers()
                response = requests.post(url, headers=headers, json=data)
                if response.status_code > 201:
                    return {"message": "Erreur", 'status': 'error', 'code': response.status_code}
                tokens_data = response.json()
                # return jsonify(tokens_data)

                response = jsonify({'status': 'Success', 'data': tokens_data, 'code': HTTPStatus.OK})
                messageLogging = name + " a cree le profil suivant " + body["name"]
                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                # logger_user(messageLogging, LOG_AUTHENTIFICATION)
                return add_headers(response)
            # messageLogging = name + " a de cree le profil suivant "
            # logger_user(messageLogging, LOG_AUTHENTIFICATION)
            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)
    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


@app.route('/users/profils/<string:userId>/', methods=['POST'])
def UserRole(userId):
    try:
        headers = flask.request.headers
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

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:
            if getRoleToken(token) == 'admin' or getRoleToken(
                    token) == 'sf':  # le role sf est un test ici, seul l'admin a le droit de crer des profils
                body = request.get_json()
                result = {
                    "name": body["name"],
                    # "id": body["id"],
                }
                print('------------ le res renvoye est----------')
                print(result)
                data = [result]
                url = URI_USER + '/' + userId + '/role-mappings/realm'
                headers = get_keycloak_headers()
                # TODO : appele la fonction deleteProfilUser
                DeleteProfilUser(userId)
                response = requests.post(url, headers=headers, json=data)
                if response.status_code > 204:
                    return {"message": "Erreur", 'status': response.json(), 'code': response.status_code}
                response = jsonify({'status': 'Success', 'data': 'Profil attribue avec success', 'code': HTTPStatus.OK})
                messageLogging = name + " a modifie le profil " + body["old_profil"] + " de l'utilisateur " + \
                                 GetUserByID(userId)['data']['username'] + ' en profil ' + body['name']

                message_log = {
                    "url.path": request.base_url,
                    "http.request.method": request.method,
                    "client.ip": getIpAdress(),
                    "event.message": messageLogging,
                    "process.id": os.getpid(),
                }
                log_app(message_log)
                return add_headers(response)

            messageLogging = name + " a tenté de modifier l'utilisateur " + GetUserByID(userId)['data']['username']
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": getIpAdress(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)

            return {"message": "invalid user", 'code': HTTPStatus.UNAUTHORIZED}
        else:
            return decodeToken(token)

    except ValueError:
        return jsonify({'status': 'Error', 'error': ValueError})


# API permettant de se déconnecter
@app.route('/logout/', methods=['GET'])
def logout():
    try:
        headers = flask.request.headers
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

        data = decodeToken(token)
        code = data['code']
        name = data['data']['name']
        if code == 200:

            messageLogging = name + " s'est deconnecté "
            message_log = {
                "url.path": request.base_url,
                "http.request.method": request.method,
                "client.ip": getIpAdress(),
                "event.message": messageLogging,
                "process.id": os.getpid(),
            }
            log_app(message_log)
            response = jsonify({'status': 'Success', 'data': 'Logout', 'code': HTTPStatus.OK})
            return add_headers(response)
        else:
            return decodeToken(token)

    except ValueError:
        return jsonify({'status': 'Error ', 'error': ValueError})


# API permettant de faire l'historisation
@app.route('/historiqueinventaire', methods=['GET'])
def HistoryInventary():
    con = connect()
    cursor = con.cursor()
    query = '''
                select   pon, slot, nom_olt,  count(distinct service_id) as NombreDeNumero 
                         from inventaireglobal_ftth group by  nom_olt, pon, slot 
            '''
    data_ = pd.read_sql(query, con)
    print('------------------Le dataFrame renvoyé est------------------------')
    # print(data_)
    my_dict = data_.to_dict(orient='records')
    df = pd.DataFrame(data=my_dict)
    i = 0
    for row in df.itertuples():
        # print(row)
        cursor.execute(
            ''' 
                INSERT INTO inventaireglobalhistory_ftth (pon, slot, nom_olt, nombre_de_numero)
                                                         VALUES (%s, %s, %s, %s)  ''',
            (row.pon, row.slot, row.nom_olt, row.nombredenumero),
        )
        con.commit()
        print(i)
        i = i + 1
        print("Inserted is running ..........................")
    print("Inserted")
    # print(row.pon)
    # print('----------------remplissage de la table-------------------')
    # df.to_sql(con=connect, name='inventaireglobalhistory_ftth', if_exists='append', index=False)
    # print('----------------------res envoye----------------------')
    # print(df)
    return df
    # print(res)
    # for
    # return res


# fonction DeleteProfilUser
def DeleteProfilUser(userId):
    url = URI_USER + '/' + userId + '/role-mappings/realm'
    donnee = testGetTokenUserAdmin()
    token_admin = donnee['tokens']["access_token"]
    response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
    for role in response.json():
        if (role.get('name') != 'offline_access' and role.get('name') != 'default-roles-saytu_realm' and role.get(
                'name') != 'uma_authorization'):
            result = {
                "name": role.get('name'),
                "id": role.get('id'),
            }

            data = [result]
            url = URI_USER + '/' + userId + '/role-mappings/realm'
            headers = get_keycloak_headers()
            reponse = requests.delete(url, headers=headers, json=data)


# La fonction get_user_by_id
def get_user_by_id(userId):
    try:
        url = URI_USER + '/' + userId
        donnee = adminToken()
        token_admin = donnee['tokens']["access_token"]
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
        return jsonify({'status': 'Error ', 'error': ValueError})


# la fonction get_info_user
def get_info_user(userId):
    try:
        url = URI_USER + '/' + userId + '/role-mappings/realm'
        donnee = adminToken()
        token_admin = donnee['tokens']["access_token"]
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token_admin)})
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


@app.route('/testgit')
def test_git():
    return testQuery()

@app.route('/historiquedebit')
def test_history():
    return testHistory()


# create_table_inventaire_history() # appel de la fonction
# HistoryInventary()  # appel de la
# configurationClientsHuawei("338234209")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
