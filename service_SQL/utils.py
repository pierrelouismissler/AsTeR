# Author:  DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

try: from service_SQL.imports import *
except: from imports import *

def format_url(section, credentials='configs/credentials.yaml'):

    with open(credentials) as raw: crd = yaml.safe_load(raw)[section]

    if section == 'postgresql':
    
        arg = (crd['user'], crd['password'], crd['server'], crd['port'], crd['user'])
        return 'postgres://{}:{}@{}:{}/{}'.format(*arg)

    if section == 'sqlite':

        return crd['path']

def parse_arguments(request):

    dic = dict(request.args)
    for key, value in dic.items():
        if type(value) == list: dic[key] = str(value[0])

    return dic
