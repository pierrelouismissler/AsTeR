# Author:  DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

try: from service_SQL.imports import *
except: from imports import *

def format_url(credentials='configs/credentials.yaml'):

    with open(credentials) as raw: crd = yaml.safe_load(raw)['postgresql']
    arg = (crd['user'], crd['password'], crd['server'], crd['port'], crd['user'])
    
    return 'postgres://{}:{}@{}:{}/{}'.format(*arg)
