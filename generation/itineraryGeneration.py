from flask import Flask, Blueprint, render_template, url_for, request, redirect, flash, send_file, send_from_directory
from main import DI, manageIDToken, Logger, Universal
import os, json, datetime, random

itineraryGenBP = Blueprint('itineraryGen', __name__)

@itineraryGenBP.route("/generate/targetLocations")
def targetLocations():
    return render_template("generation/targetLocations.html", popularLocations=Universal.generationData["locations"])