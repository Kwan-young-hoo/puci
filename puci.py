import subprocess
import shlex

from common.log import *
from common.env import *
from uci_data import *


UCI_SHOW_CMD="uci show "
UCI_EXPORT_CMD="uci export "
UCI_GET_CMD="uci get "
UCI_SET_CMD="uci set "
UCI_DELETE_CMD="uci delete "
UCI_ADD_LIST_CMD="uci add_list "
UCI_DELETE_LIST_CMD="uci delete_list "
UCI_COMMIT_CMD="uci commit "



def subprocess_open(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata

def subprocess_open_when_shell_false(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata

def subprocess_open_when_shell_false_with_shelx(command):
    popen = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata

def subprocess_pipe(cmd_list):
    prev_stdin = None
    last_p = None
    
    for str_cmd in cmd_list:
        cmd = str_cmd.split()
        last_p = subprocess.Popen(cmd, stdin=prev_stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        prev_stdin = last_p.stdout
    
    (stdoutdata, stderrdata) = last_p.communicate()
    return stdoutdata, stderrdata


# TODO: Detail error handling 
#
class ConfigUCI:
    def __init__(self, config_file, config_name, *args):
        self.config_file = config_file
        self.config_name = config_name
        self.section_map = uci_get_section_map(config_name, *args)
        log_info(LOG_MODULE_SAL, "Section_map(" + config_name + "): " + str(self.section_map))

    def restart_module(self):
        command = '/www/openAPgent/utils/apply_config '+ self.config_file + ' &'
        log_info(LOG_MODULE_SAL, "===" , command + "===")  
        return subprocess_open(command)
                               
    def commit_uci_config(self):
        log_info(LOG_MODULE_SAL, "===" , UCI_COMMIT_CMD + self.config_file + "===")
        return subprocess_open(UCI_COMMIT_CMD + self.config_file)

    def set_uci_config_scalar(self, option, value):
        log_info(LOG_MODULE_SAL, UCI_SET_CMD + option + '=' + value)
        output, error = subprocess_open(UCI_SET_CMD + option + '=' + value)
        if not error:
            self.commit_uci_config()
        else:
            log_error(LOG_MODULE_SAL, "set_uci_config_scalar() error:" + error)
        return output, error

    def set_uci_config_list(self, option, values):
        list_value = values.split(' ')

        for i in range(0, len(list_value)):
            log_info(LOG_MODULE_SAL, UCI_ADD_LIST_CMD + option + '=' + str(list_value[i]))
            output, error = subprocess_open(UCI_ADD_LIST_CMD + option + '=' + list_value[i])
            if not error:
                self.commit_uci_config()
            else:
                log_error(LOG_MODULE_SAL, "set_uci_config_list() error:" + error)
        return output, error

    def set_uci_config(self, req):
        for req_key in req.keys():
            req_val = req[req_key]
            # Check dictionary value
            if isinstance(req_val, dict):
                continue;

            req_key = req_key
            req_val = req[req_key]

            # Update the requested SET Value to section_map
            if req_key in self.section_map:
                map_val = self.section_map[req_key]
                map_val[2] = self.convert_config_value(req_val)
                map_val.append('section_map_value_updated')

        for map_val in self.section_map.values():
            if not 'section_map_value_updated' in map_val: continue

            self.delete_uci_config(map_val[1])

            map_val[2] = map_val[2].strip()
            if not map_val[2]: continue

            if map_val[0] == CONFIG_TYPE_SCALAR:
                self.set_uci_config_scalar(map_val[1], str(map_val[2]))
            else:
                self.set_uci_config_list(map_val[1], map_val[2])

    def delete_uci_list_config(self, option, value):
        log_info(LOG_MODULE_SAL, UCI_DELETE_LIST_CMD + option + '=' + value)  
        output, error = subprocess_open(UCI_DELETE_LIST_CMD + option + '=' + value)
        if not error:
            self.commit_uci_config()
        return output, error
        
    def delete_uci_config(self, option):
        log_info(LOG_MODULE_SAL, UCI_DELETE_CMD + option)  
        output, error = subprocess_open(UCI_DELETE_CMD + option)
        if not error:
            self.commit_uci_config()
        return output, error
        
    def show_uci_config(self):
        log_info(LOG_MODULE_SAL, UCI_SHOW_CMD + self.config_file)
        output, error = subprocess_open(UCI_SHOW_CMD + self.config_file)
        
        if not error:
            lines = output.splitlines()

            for line in lines:
                token = line.split('=')

                for map_val in self.section_map.values():
                    if map_val[1] == token[0]:
                        if token[1][0] == "'" and map_val[0] == CONFIG_TYPE_SCALAR :
                            token[1] = token[1][1:-1]
                        map_val[2] = token[1]
                        break;

            log_info(LOG_MODULE_SAL, "self.section_map = ", self.section_map)

    def convert_config_value(self, val):
        if val == True: return 1
        elif val == False: return 2
        else: return val

