import psycopg2
from script.conf import *
import pandas as pd

def simple_inventaire():
     data = select_query(''' SElect * from historique_diagnostic limit 10 ''')
     print()
     return data

















