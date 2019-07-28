# Author:  DINDIN Meryll
# Date:    27 July 2019
# Project: AsTeR

import requests
import json
import joblib
import string
import nltk
import numpy as np
import pandas as pd

from nltk.corpus import stopwords
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features
from watson_developer_cloud.natural_language_understanding_v1 import KeywordsOptions
from watson_developer_cloud.natural_language_understanding_v1 import SentimentOptions

# Endpoint relative imports
from flask import Flask
from flask import request
from flask import Response
from functools import wraps
