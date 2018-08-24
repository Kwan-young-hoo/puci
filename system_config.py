from puci import *
from common.log import *
from common.env import *
from common.error import *

UCI_SYSTEM_CONFIG_FILE = "system"
UCI_SYSTEM_CONFIG_LOGGING_CONFIG = "system_config_logging"
UCI_SYSTEM_CONFIG_NTP_CONFIG = "system_config_ntp"



'''
SystemConfig
'''
def puci_system_config_list():
    system_log_data = dict()
    system_ntp_data = dict()

    system_log_data = system_config_uci_get(UCI_SYSTEM_CONFIG_LOGGING_CONFIG, system_log_data)
    system_ntp_data = system_config_uci_get(UCI_SYSTEM_CONFIG_NTP_CONFIG, system_ntp_data)

    data = {
        "logging": system_log_data,
        "ntp": system_ntp_data,
        'header': {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }
    return data


def puci_system_config_retrieve(command, add_header):
    system_data = dict()

    log_info(LOG_MODULE_SAL, "command = ", command)

    if command == 'logging':
        system_data = system_config_uci_get(UCI_SYSTEM_CONFIG_LOGGING_CONFIG, system_data)
    elif command == 'ntp':
        system_data = system_config_uci_get(UCI_SYSTEM_CONFIG_NTP_CONFIG, system_data)
    else:
        raise RespNotFound("Command")

    data = {
        command: system_data,
        'header': {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }
    log_info(LOG_MODULE_SAL, "Response = ", str(data))

    return data


def puci_system_config_create(request):
    return system_config_set(request)


def puci_system_config_update(request):
    return system_config_set(request)


def puci_system_config_detail_create(request, command):
    return system_config_detail_set(request, command)


def puci_system_config_detail_update(request, command):
    return system_config_detail_set(request, command)

def system_config_set(request):
    system_log_data = dict()
    system_ntp_data = dict()

    log_info(LOG_MODULE_SAL, "request data = ", request)

    system_log_data = system_config_uci_set(UCI_SYSTEM_CONFIG_LOGGING_CONFIG, request['logging'], system_log_data)
    system_ntp_data = system_config_uci_set(UCI_SYSTEM_CONFIG_NTP_CONFIG, request['ntp'], system_ntp_data)

    data = {
        'header': {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }
    return data

def system_config_detail_set(request, command):
    system_data = dict()

    log_info(LOG_MODULE_SAL, "command = ", command)
    log_info(LOG_MODULE_SAL, "request data = ", request)

    if command == 'logging':
        system_data = system_config_uci_set(UCI_SYSTEM_CONFIG_LOGGING_CONFIG, request, system_data)
    elif command == 'ntp':
        system_data = system_config_uci_set(UCI_SYSTEM_CONFIG_NTP_CONFIG, request, system_data)
    else:
        raise RespNotFound("Command")

    data = {
        'header': {
            'resultCode': 200,
            'resultMessage': 'Success.',
            'isSuccessful': 'true'
        }
    }
    return data


def system_config_uci_get(uci_file, system_data):
    uci_config = ConfigUCI(UCI_SYSTEM_CONFIG_FILE, uci_file)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    uci_config.show_uci_config()

    for map_key, map_val in uci_config.section_map.items():
        system_data[map_key] = map_val[2]

    return system_data


def system_config_uci_set(uci_file, req_data, system_data):
    log_info(LOG_MODULE_SAL, "request data = ", req_data)
    uci_config = ConfigUCI(UCI_SYSTEM_CONFIG_FILE, uci_file)
    if uci_config == None:
        raise RespNotFound("UCI Config")

    uci_config.set_uci_config(req_data)

    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        if system_data:
            system_data[map_key] = map_val[2]

    return system_data
