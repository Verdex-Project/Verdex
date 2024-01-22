#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template, json, request, jsonify, redirect, url_for, flash, session
from main import Universal, DI, manageIDToken
import datetime

forumBP = Blueprint("forum", __name__)

@forumBP.route('/verdextalks')
def verdextalks():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "admin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["admin"] == True:
        return redirect(url_for("admin.admin"))

    if "forumBanned" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["forumBanned"] == True:
        return redirect(url_for("unauthorised", error="Access Denied. You have been banned from the forum."))
    
    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"], itineraryInfoJson=DI.data["itineraries"], accountsInfoJson=DI.data["accounts"], targetAccountID=targetAccountID)
    