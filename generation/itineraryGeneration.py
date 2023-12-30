from flask import Flask, Blueprint, render_template, url_for, request, redirect, flash, send_file, send_from_directory

itineraryGenBP = Blueprint('itineraryGen', __name__)

@itineraryGenBP.route("/generate/targetLocations")
def generate():
    return render_template("generation/targetLocations.html")