# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

from IPython.display import display
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return 'This is the home page of home.py. \n The method used is: %s' % request.method

@app.route('/bacon', methods=['GET', 'POST'])
def bacon():
    if request.method == 'POST':
        return 'You are using POST'
    else:
        return 'You are probably using GET'

@app.route('/profile/<username>')
def profile(username):
    return render_template('profile.html', name=username)


if __name__ == "__main__":
    app.run()

