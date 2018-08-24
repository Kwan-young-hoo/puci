import fileinput

from puci import *
from common.log import *
from common.env import *

UCI_DHCP_FILE ="dhcp"
UCI_DHCP_COMMON_CONFIG = "dhcp_common"
UCI_DHCP_INTERFACE_POOL_CONFIG = "dhcp_interface_pool"
UCI_DHCP_INTERFACE_V6POOL_CONFIG = "dhcp_interface_v6pool"
UCI_DHCP_STATIC_LEASE_CONFIG = "dhcp_static_leases"


'''
#DHCP Common
'''
def puci_dhcp_common_config_list():
    dhcp_common_data = dict()

    dhcp_common_data = dhcp_common_uci_get(UCI_DHCP_COMMON_CONFIG, dhcp_common_data)

    data = {
        "dhcp-dns": dhcp_common_data,
        'header': {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }

    return data

def puci_dhcp_common_config_create(request):
    return dhcp_common_set(request)

def puci_dhcp_common_config_update(request):
    return dhcp_common_set(request)

def dhcp_common_set(request):
    dhcp_common_data = dict()

    log_info(LOG_MODULE_SAL, "request data = ", request)

    dhcp_common_data = dhcp_common_uci_set(UCI_DHCP_COMMON_CONFIG, dhcp_common_data)

    data = {
        'header': {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }
    return data

def dhcp_common_uci_get(uci_file, dhcp_data):
    uci_config = ConfigUCI(UCI_DHCP_COMMON_CONFIG, uci_file)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    uci_config.show_uci_config()

    for map_key, map_val in uci_config.section_map.items():
        dhcp_data[map_key] = map_val[2]

    return dhcp_data

def dhcp_common_uci_set(uci_file, dhcp_data):
 #   log_info(LOG_MODULE_SAL, "request data = ", req_data)
    uci_config = ConfigUCI(UCI_DHCP_COMMON_CONFIG, uci_file)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        if dhcp_data:
            dhcp_data[map_key] = map_val[2]

    return dhcp_data

'''
#DHCP Pool
'''
def puci_dhcp_pool_config_list():
    iflist=['lan', 'wan', 'wan6']

    for i in range (0, len(iflist)):
        log_info(LOG_MODULE_SAL, "[ifname] : " + iflist[i])
        rc = puci_dhcp_pool_config_retrieve(iflist[i], 0)
        if i == 0:
            iflist_body = [rc]
        else:
            iflist_body.append(rc)

    data = {
            "dhcp-pool": iflist_body,
            'header': {
                        'resultCode': 200,
                        'resultMessage': 'Success.',
                        'isSuccessful': 'true'
                       }
            }

    return data

def puci_dhcp_pool_config_retrieve(ifname, add_header):
    if not ifname:
        raise RespNotFound("dhcp")
    log_info(LOG_MODULE_SAL, "[ifname] : " + ifname)

    dhcp_data = dict()

    dhcp_data = dhcp_pool_uci_get(ifname, dhcp_data)
    dhcp_data = dhcp_pool_v6pool_uci_get(ifname, dhcp_data)


    if add_header == 1:
        data = {
            'interface' : dhcp_data,
            'header' : {
                            'resultCode':200,
                            'resultMessage':'Success.',
                            'isSuccessful':'true'
                        }
        }
    else:
        data = dhcp_data

    return data

def puci_dhcp_pool_config_create(request):
    return dhcp_pool_set(request)

def puci_dhcp_pool_config_update(request):
    return dhcp_pool_set(request)

def puci_dhcp_pool_config_detail_create(request, ifname):
    return dhcp_pool_detail_set(request, ifname)

def puci_dhcp_pool_config_detail_update(request, ifname):
    return dhcp_pool_detail_set(request, ifname)

def dhcp_pool_set(request):
    dhcp_list = request['dhcp-pool']

    while len(dhcp_list) > 0:
        ifdata = dhcp_list.pop(0)

        ifname = ifdata['ifname']

        dhcp_pool_uci_set(ifdata, ifname)
        if "v6pool" in ifdata:
            dhcp_pool_v6pool_uci_set(ifdata['v6pool'], ifname)

    data = {
        'header': {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }
    return data


def dhcp_pool_detail_set(request, ifname):
    if not ifname:
        raise RespNotFound("dhcp")

    dhcp_pool_uci_set(request, ifname)
    if "v6pool" in request:
        dhcp_pool_v6pool_uci_set(request['v6pool'], ifname)

    data = {
        'header' : {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }
    return data


def dhcp_pool_uci_get(ifname, dhcp_data):
    uci_config = ConfigUCI(UCI_DHCP_FILE,UCI_DHCP_INTERFACE_POOL_CONFIG, ifname)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    uci_config.show_uci_config()

    dhcp_data['ifname'] = ifname
    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        dhcp_data[map_key] = map_val[2]

    return dhcp_data

def dhcp_pool_uci_set(req_data, ifname):
    if not ifname:
        raise RespNotFound("dhcp")

    uci_config = ConfigUCI(UCI_DHCP_FILE, UCI_DHCP_INTERFACE_POOL_CONFIG, ifname)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    uci_config.set_uci_config(req_data)

def dhcp_pool_v6pool_uci_get(ifname, dhcp_data):
    pool_data = dict()

    uci_config = ConfigUCI(UCI_DHCP_FILE, UCI_DHCP_INTERFACE_V6POOL_CONFIG, ifname)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    uci_config.show_uci_config()

    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        pool_data[map_key] = map_val[2]

    dhcp_data['v6pool'] = pool_data

    log_info(LOG_MODULE_SAL, dhcp_data)

    return dhcp_data

def dhcp_pool_v6pool_uci_set(req_data, ifname):

    uci_config = ConfigUCI(UCI_DHCP_FILE, UCI_DHCP_INTERFACE_V6POOL_CONFIG, ifname)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    uci_config.set_uci_config(req_data)


'''
#DHCP_Static_leases
'''

def puci_dhcp_static_leases_config_list():

    return data

def puci_dhcp_static_leases_config_create():

    return data

def puci_dhcp_static_leases_config_update():

    return data

def puci_dhcp_static_leases_config_retrieve():

    return data

def puci_dhcp_static_leases_config_detail_create():

    return data

def puci_dhcp_static_leases_config_detail_update():

    return data



