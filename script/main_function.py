import psycopg2
from script.conf import *
import pandas as pd


def simple_inventaire():
    data = select_query(''' SElect * from historique_diagnostic limit 10 ''')
    return data


# fonction doublon
def get_doublon():
    numero = request.args.get('numero')
    if numero is None or numero == "":
        data = select_query('''Select db.service_id, db.nom_olt, db.ip_olt, db.vendeur, db.created_at::date , mt.oltrxpwr, mt.ontrxpwr
                                   From doublons_ftth as db, metric_seytu_network as mt
                                   where db.service_id = mt.numero
                                   and db.ip_olt = mt.olt_ip order by db.created_at::date desc''')
        return data
    else:
        data = select_query_argument('''Select db.service_id, db.created_at::date, db.nom_olt, db.ip_olt, db.vendeur, mt.oltrxpwr, mt.ontrxpwr
                                           From doublons_ftth as db, metric_seytu_network as mt
                                           where db.service_id = mt.numero 
                                           and db.ip_olt = mt.olt_ip
                                           and db.service_id = '{}'  order by db.created_at::date desc''', numero)
        return data

# Liste des coupures
def get_coupure():
    numero = request.args.get('numero')
    if numero is None or numero == "":
         return "La liste des coupures est vide"
    else:
        data = select_query_argument('''SELECT numero,pon , slot, ip, nom_olt, vendeur, anomalie, criticite,   created_at  
	                                         FROM maintenance_predictive_ftth WHERE anomalie LIKE '%Coupure%' AND numero = '{}' ''', numero)
        return data

# Historique du taux d'utilisation
def taux_utilisation():
    numero = request.args.get('numero')
    if numero is None or numero == "":
        data = select_query('''SELECT DISTINCT service_id, offre,vendeur, debitup, debitdown, ip_olt,nom_olt,slot,pon,  created_at::date
                               FROM inventaireglobal_network_bis''')
        return data
    else:
        data = select_query_argument(''' SELECT DISTINCT service_id, offre, debitup, debitdown, ip_olt,nom_olt,slot,pon,  created_at::date
                                         FROM inventaireglobal_network_bis where  service_id = '{}' ''', numero)
        return data

# fonction derniere heure de coupure
#def get_derniere_heure_coupure():

