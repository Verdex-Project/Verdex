#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template, json, request, jsonify, redirect, url_for, flash
from main import Universal, DI
import datetime

forumBP = Blueprint("forum", __name__)

@forumBP.route('/verdextalks')
def verdextalks():

    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"])
    