import os

import jwt
import yaml
import logging

from http import HTTPStatus
import socket
from psycopg2 import Error
import psycopg2
import pandas as pd

with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml', "r") as ymlfile:
    cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)

# function de connection à la BDD
def connect():
    return psycopg2.connect(database=cfg["NAME_DB"], user=cfg["USER_DB"], password=cfg["PASSWORD_DB"], host=cfg["HOST_DB"], port=cfg["PORT_DB"])

# function de decodage du token avec JWT
def decodeToken(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return {"data": decoded, 'code': HTTPStatus.OK}
    except:
        return {"message": "invalid token ", 'code': HTTPStatus.UNAUTHORIZED}

# function getRoleToken pour l'attribution des roles
# function getRoleToken pour l'attribution des roles
def getRoleToken(token):
    try:
        roles = decodeToken(token)['data']['realm_access']['roles']
        for role in roles:
            if (role != 'offline_access' and role != 'default-roles-saytu_realm' and role != 'uma_authorization'):
                return role

    except ValueError:
        return {'status': 'Error', 'error': ValueError}

# La fonction getIpAdress()
def getIpAdress():
    h_name = socket.gethostname()
    IP_addres = socket.gethostbyname(h_name)
    return IP_addres

# La fonction log_app()
def log_app(message):
    file_formatter = logging.Formatter(
        "{'time':'%(asctime)s', 'service.name': 'Diag_Distant', 'level': '%(levelname)s', 'message': " + str(
            message) + "}"
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    console.setFormatter(file_formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    # logging.basicConfig(format='%(asctime)s %(message)s ' + message, datefmt='%d/%m/%Y %H:%M:%S')
    # logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

# La fonction getAllDoublon
def getAllDoublon():
    con = connect()
    query = ''' 
                    Select db.service_id, db.nom_olt, db.ip_olt, db.vendeur, db.created_at::date , mt.oltrxpwr, mt.ontrxpwr
                    From doublons_ftth as db, metric_seytu_network as mt
                    where db.service_id = mt.numero
                    and db.ip_olt = mt.olt_ip order by db.created_at::date desc
                     
            '''
    data_ = pd.read_sql(query, con)
    print(data_)
    res = data_.to_dict(orient='records')
    return res

# La fonction affichage des dernieres heure de coupure
def getDerniereHeureDeCoupure():

    con = connect()
    query = ''' Select numero,nom_olt, ip, vendeur, anomalie, criticite, Max(created_at) as created_at  
                from maintenance_predictive_ftth Group by numero,nom_olt, ip, vendeur, anomalie, criticite
            '''
    data_ = pd.read_sql(query, con)
    print(data_)
    res = data_.to_dict(orient='records')
    return res

def testGit():
    return "ceci est un test"