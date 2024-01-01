from flask import Flask, render_template, Blueprint
from flask_cors import CORS

signUpPage = Blueprint("signUpPageBP",__name__)

@signUpPage.route('/account/signup')
def signUp():
    return render_template('identity/signup.html')