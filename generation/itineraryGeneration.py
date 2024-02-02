from flask import Flask, Blueprint, render_template, url_for, request, redirect, flash, send_file, send_from_directory
from main import DI, manageIDToken, Logger, Universal
import os, json, datetime, random

itineraryGenBP = Blueprint('itineraryGen', __name__)

@itineraryGenBP.route("/generate/targetLocations")
def targetLocations():
    ## DEBUG PHASE ONLY
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for('unauthorised', error=authCheck))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "admin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["admin"] == True:
        return redirect(url_for('admin.admin'))

    return render_template("generation/targetLocationsNew.html", popularLocations=Universal.generationData["locations"])