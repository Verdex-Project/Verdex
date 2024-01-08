from flask import Flask, Blueprint, render_template, url_for, request, redirect, flash, send_file, send_from_directory

itineraryGenBP = Blueprint('itineraryGen', __name__)

staticLocations = [
    "Marina Bay Sands",
    "Universal Studios Singapore",
    "Singapore Zoo",
    "SEA Aquarium",
    "Botanical Gardens",
    "Gardens by the Bay",
    "Singapore Flyer",
    "Jewel Changi Airport",
    "East Coast Park",
    "Fort Canning Park"
]

@itineraryGenBP.route("/generate/targetLocations")
def targetLocations():
    return render_template("generation/targetLocations.html", popularLocations=staticLocations)