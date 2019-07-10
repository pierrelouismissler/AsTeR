# Author:  RADERMECKER Oskar, DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

import json
import requests

from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
