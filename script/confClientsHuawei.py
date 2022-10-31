from function import *

def configurationClientsHuawei(serviceId):
    """ fonction permettant d'avoir la configuration des clients
        au niveau des équipemnts
        Arguments : serviceId
        serviceId : le Numero du client
    """
    df = data_inventaire(serviceId)
    _index_, ip, _ont_, pon, slot =   str(df[df['serviceId'] == serviceId]['ont_index'].values[0]), \
                                      str(df[df['serviceId'] == serviceId]['ip_olt'].values[0]), \
                                      str(df[df['serviceId'] == serviceId]['ont_id'].values[0]), \
                                      str(df[df['serviceId'] == serviceId]['pon'].values[0]), \
                                      str(df[df['serviceId'] == serviceId]['slot'].values[0])

    #df_final = data