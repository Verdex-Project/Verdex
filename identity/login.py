from flask import Flask, render_template, Blueprint
from flask_cors import CORS

loginPage = Blueprint("loginPageBP",__name__)

@loginPage.route('/account/login')
def login():
    return render_template('identity/login.html')