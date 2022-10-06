import os
import yaml
import psycopg2
from pathlib import Path
import random
import shutil
import smtplib
import socket
import string
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import HTTPStatus
from pathlib import Path
import jwt
import pandas as pd
from psycopg2 import Error
import glob
import logging

with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml', "r") as ymlfile:
    cfg = yaml.load(ymlfile.read(), Loader=yaml.FullLoader)

# function de connection à la BDD
def connect():
    return psycopg2.connect(database=cfg["NAME_DB"], user=cfg["USER_DB"], password=cfg["PASSWORD_DB"], host=cfg["HOST_DB"], port=cfg["PORT_DB"])

# function de creation de la table inventaire
def create_table_inventaire():
    con = connect()
    cursor = con.cursor()
    try:
        create_table_query = '''CREATE TABLE IF NOT EXISTS inventaireglobal_ftth 
        (
        id serial PRIMARY KEY,
        ont_index BIGINT NOT NULL,
        ont_id int NOT NULL,
        service_id varchar(20) NOT NULL,
        ip_olt varchar(20) NOT NULL,
        slot int NOT NULL,
        pon int NOT NULL,
        pon_index BIGINT NOT NULL,
        vendeur varchar(100) NOT NULL,
        nom_olt varchar(100) NOT NULL,
        created_at TIMESTAMP DEFAULT Now()
        ); '''

        cursor.execute(create_table_query)
        con.commit()
        print("Table created succesfully in Postgresql")
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if con:
            cursor.close()
            con.close()
            print("Connection on Postgresql database is disconnected")

# function de decodage du token avec JWT
def decodeToken(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return {"data": decoded, 'code': HTTPStatus.ok}
    except:
        return {"message": "invalid token", 'code': HTTPStatus.UNAUTHORIZED}

# function getRoleToken pour l'attribution des roles
def getRoleToken(token):
    try:
        roles = decodeToken(token)['data']['realm_access']['roles']
        for role in roles:
            if (role != 'offline-access' and role != 'uma_authorization'):
                return role

    except ValueError:
        return {'status': 'Error', 'error': ValueError}








