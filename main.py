import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from flask_cors import CORS
from models import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    # Register routes
    
    ## Assets service
    from assets import assetsBP
    app.register_blueprint(assetsBP)

    app.run(port=8000, host='0.0.0.0', debug=True)