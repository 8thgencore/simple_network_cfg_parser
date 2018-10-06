#! python
import re
import os
import json
import optparse
from optparse import OptionGroup
from colorama import Fore, Back, Style

Tversion = 'VERSION 0.1'


def read_config(cfg):
    with open(cfg, 'r') as f:
        cfg_lines = f.readlines()
        cfg_lines = [line.rstrip() for line in cfg_lines]
    return cfg_lines


class IOSParse(object):
    def __init__(self, cfg, supp_types_json):
    	# Считываем файл конфигурации и json
        self.cfg = read_config(cfg)
        self.supp_types_json = json.load(open(supp_types_json))

    def srch_for_supp_obj_prop(self, category, key, line):
    	# Ищет наличие свойства у интерфейса
        instructions = self.supp_types_json[category]['properties'][key]['read']
        match = re.findall(instructions, line)
        try:
            return match[0].strip()
        except IndexError:
            pass

    def get_interface_names(self):
        # Возвращает список всех имен интерфейсов, найденных в файле конфигурации
        interface_list = []
        for line in self.cfg:
            if self.srch_for_supp_obj_prop('ios_interface', 'name', line):
                interface_list.append(line.rstrip())
        return interface_list

    def get_interface_properties(self):
        # Возвращает список свойств интерфейсов, найденных в файле конфигурации
    	interface_properties_list = []
    	properties = {}
    	for line in self.cfg:
    		for k, v in self.supp_types_json['ios_interface']['properties'].items():
    			match = self.srch_for_supp_obj_prop('ios_interface', k, line)
    			if match:
    				if properties.get(k):
    					properties[k] += ",{}".format(match)
    				else:
    					properties[k] = match
    			elif line == '!' and properties.get('name'):
    			# elif properties.get('name'):
    				interface_properties_list.append(properties)
    				properties = {}

    	return interface_properties_list

if __name__ == '__main__':

	parser = optparse.OptionParser(version = Tversion)
	group = OptionGroup(parser,'Filter Options')
	group.add_option('-f', action='store', dest='config_file' , help='path to config file')
	parser.add_option_group(group)

	options,_ = parser.parse_args()

	print (options.config_file)

	if (options.config_file):
		net_device = IOSParse(options.config_file, 'supported_types.json')
		all_interfaces = net_device.get_interface_names()
		test = net_device.get_interface_properties()

		# вывод на экран
		print_test = json.dumps(test, indent = 4)
		print (Fore.CYAN + print_test)

		# запись в файл
		with open('data.json', 'w') as outfile:
			json.dump(test, outfile, indent = 4)