import psycopg2
from script.conf import *
import pandas as pd

def simple_inventaire():
     data = select_query(''' SElect * from historique_diagnostic limit 10 ''')
     return data

# fonction doublon
def get_doublon():
     data = select_query('''Select db.service_id, db.nom_olt, db.ip_olt, db.vendeur, db.created_at::date , mt.oltrxpwr, mt.ontrxpwr
                                   From doublons_ftth as db, metric_seytu_network as mt
                                   where db.service_id = mt.numero and db.ip_olt = mt.olt_ip order by db.created_at::date desc ''')
     return data


















