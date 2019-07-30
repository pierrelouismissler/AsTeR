# Author:  DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

import os
import uuid
import json
import yaml
import tqdm
import joblib
import warnings
import numpy as np

from flask import Flask
from flask import abort
from flask import request
from flask import Response
from pqdict import PQDict
from functools import wraps
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy

# Heavy imports (not suitable for micro-service)
# import geopandas
# import pandas as pd
