# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

import io
import os
import time
import yaml
import json
import wave
import argparse

# Rev.ai package
from rev_ai import apiclient
# IBM Watson package
from watson_developer_cloud import SpeechToTextV1
# Google Cloud package
from google.oauth2 import service_account
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Endpoint relative imports
from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from werkzeug.utils import secure_filename
