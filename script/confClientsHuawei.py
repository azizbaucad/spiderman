from script.function import *

from pysnmp.hlapi import *


def configurationClientsHuawei(serviceId):
    """ fonction permettant d'avoir la configuration des clients
        au niveau des équipemnts
        Arguments : serviceId
        serviceId : le Numero du client
    """
    df = data_inventaire(serviceId)
    _index_, ip, _ont_, pon, slot = str(df[df['serviceId'] == serviceId]['ont_index'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['ip_olt'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['ont_id'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['pon'].values[0]), \
                                    str(df[df['serviceId'] == serviceId]['slot'].values[0])

    df_final = data_infos_huawei_conf(ip, pon, slot)
    down_str = df_final[(df_final["ip"] == ip) & (df_final["onuId"] == int(_ont_)) & (df_final["pon"] == int(pon)) & (
            df_final["slot"] == int(slot))]["nomTrafDown"].values[0]
    up_str = df_final[(df_final["ip"] == ip) & (df_final["onuId"] == int(_ont_)) & (df_final["pon"] == int(pon)) & (
            df_final["slot"] == int(slot))]["nomTrafUp"].values[0]

    oid_index = "1.3.6.1.4.1.2011.5.14.3.8.1.2"
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('OLT@osn_read'),
                              UdpTransportTarget(transportAddr=(ip, 161), timeout=2.0, retries=5),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid_index)),
                              lexicographicMode=False,
                              lookupMib=False):
        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                if varBind[1].prettyPrint() == down_str:
                    id_dwstr = varBind[0].prettyPrint().split(".")[-1]
                elif varBind[1].prettyPrint() == up_str:
                    id_upstr = varBind[0].prettyPrint().split(".")[-1]

    oid_debit_up = "1.3.6.1.4.1.2011.5.14.3.8.1.5" + "." + id_dwstr

    oid_debit_down = "1.3.6.1.4.1.2011.5.14.3.8.1.5" + "." + id_upstr

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(
        SnmpEngine(),
        CommunityData('OLT@osn_read'),
        UdpTransportTarget(transportAddr=(ip, 161), timeout=2.0, retries=5),
        ContextData(),
        ObjectType(ObjectIdentity(oid_debit_up)),
        lexicographicMode=False,
        lookupMib=False):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                debit_up = int(varBind[1].prettyPrint()) / 1000

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds
         ) in getCmd(SnmpEngine(),
                     CommunityData('OLT@osn_read'),
                     UdpTransportTarget(transportAddr=(ip, 161), timeout=2.0, retries=5),
                     ContextData(),
                     ObjectType(ObjectIdentity(oid_debit_down)),
                     lexicographicMode=False,
                     lookupMib=False):
        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                debit_down = int(varBind[1].prettyPrint()) / 1000
                if debit_down <= 39:
                    offre = "FIBRE BI"
                    # 20 down
                    break
                elif debit_down > 39 and debit_down <= 59:
                    offre = "FIBRE MAX"
                    # 40 down
                    break
                elif debit_down > 59 and debit_down <= 99:
                    offre = "FIBRE MEGA"
                    # 60 down
                    break
                else:
                    offre = "FIBRE MEGA PLUS"
                    # 100 down
                    break

    oid_rxPower = "1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4" + "." + str(_index_) + "." + _ont_

    oid_operstatus = "1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15." + str(_index_) + "." + str(_ont_)

    for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(
            SnmpEngine(),
            CommunityData('OLT@osn'),
            UdpTransportTarget(transportAddr=(ip, 161), timeout=2.0, retries=5),
            ContextData(),
            ObjectType(ObjectIdentity(oid_operstatus)),
            lexicographicMode=False,
            lookupMib=False):

        if errorIndication:
            raise Exception('SNMP getCmd error {0}'.format(errorIndication))
        else:
            for varBind in varBinds:
                operstatus = varBind[1].prettyPrint()
                if operstatus == "1":
                    statut = "Actif"
                else:
                    statut = "Inactif"

    for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(
            SnmpEngine(),
            CommunityData('OLT@osn_read'),
            UdpTransportTarget(transportAddr=(ip, 161), timeout=20, retries=5),
            ContextData(),
            ObjectType(ObjectIdentity(oid_rxPower)),
            lexicographicMode=False,
            lookupMib=False):

        if errorIndication:
            raise Exception('SNMP getCmd error {0} '.format(errorIndication))
        else:
            for varBind in varBinds:
                rxPower = int(varBind[1].prettyPrint()) / 100
                if int(varBind[1].prettyPrint()) == 2147483647:
                    qualitySignal = "Signal indisponible"
                elif rxPower <= -30:
                    qualitySignal = "Très dégradé"
                elif ((rxPower > -30 and rxPower <= -27) or rxPower > 10):
                    qualitySignal = "Dégradé"
                else:
                    qualitySignal = "Normal"

    return {
        "offre": offre,
        "MaxUp": debit_up,
        "MaxDown": debit_down,
        "StatutModem": statut,
        "qualitySignal": qualitySignal
    }
