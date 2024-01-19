#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template, json, request, jsonify, redirect, url_for, flash
from main import Universal, DI, manageIDToken
import datetime

forumBP = Blueprint("forum", __name__)

@forumBP.route('/verdextalks')
def verdextalks():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if DI.data["accounts"][targetAccountID]["forumBanned"] == True:
        flash("Access Denied. You have been banned from the forum.")
        return redirect(url_for("error"))
    
    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"], itineraryInfoJson=DI.data["itineraries"])
    