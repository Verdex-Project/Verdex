import os, googlemaps, datetime, json, pprint
from models import Universal, Logger
from dotenv import load_dotenv
load_dotenv()

class GoogleMapsService:
    servicesEnabled = False
    contextChecked = False
    gmapsAPIKey = None
    gmapsClient = None

    @staticmethod
    def checkContext():
        if "GoogleMapsEnabled" in os.environ and os.environ["GoogleMapsEnabled"] == "True":
            GoogleMapsService.gmapsClient = googlemaps.Client(key=os.environ["GoogleMapsAPIKey"])
            GoogleMapsService.gmapsAPIKey = os.environ["GoogleMapsAPIKey"]
            GoogleMapsService.servicesEnabled = True
            GoogleMapsService.contextChecked = True
        
    @staticmethod
    def generateMapEmbedHTML(mapMode, mapType, zoom="default", classlist="", id="", width="600", height="450", placeQuery=None, directionsOrigin=None, directionsDestination=None, directionsMode=None, viewCenterCoordinates=None):
        '''Returns a string of `iframe` HTML that has a fully-embedded Google Map.

        ## Parameters:
        - `mapMode`: String --> `place`, `directions`, `view`
            - `place` to show the map of a specific place with a marker on the place's location
                - Requires `placeQuery`.
            - `directions` shows a map with a route plotted between a start and end destination.
                - Requires `directionsOrigin`, `directionsDestination`, and `directionsMode`
            - `view` displays a map around specific center co-ordinates. 
                - Requires `viewCenterCoordinates`.
        - `mapType`: String --> `roadmap`, `satellite`
        - `zoom`: String (optional, default: automatic) -->  Integer in a string. Ranges from 0 (the whole world) to 21 (individual buildings).
        - `classlist`: String (optional) --> Will set the classlist you provide in the `iframe`'s HTML. Could be used to apply CSS rules to the `iframe` embed.
        - `id`: String (optional) --> Will set the ID you provide in the `iframe`'s HTML. Could be used to apply CSS rules to the `iframe` embed or otherwise.
        - `width`: String (optional, default: 600) --> Sets the width of the `iframe`. All normal HTML and CSS width sizes can be applied (e.g `10%`).
        - `height`: String (optional, default: 450) --> Sets the height of the `iframe`. All normal HTML and CSS width sizes can be applied (e.g `10%`).
        - `placeQuery`: String (optional) --> Query a specific place on Google Maps. Example value: `Marina Bay Sands`.
        - `directionsOrigin`: String (optional) --> A query for the origin of a directions route plot. Example value: `Marina Bay Sands`.
        - `directionsDestination`: String (optional) --> A query for the destination of a directions route plot. Example value: `Jewel Changi Airport`.
        - `directionsMode`: String (optional) --> The mode of transit for a directions route plot. Valid values: `driving`, `walking`, `bicycling`, `transit`, `flying`
        - `viewCenterCoordinates`: String (optional) --> Comma-separated latitude and longitude coordinates. Example value: `37.4218,-122.0840`.

        ## Sample usage
        In a Python file:
        ```python
        GoogleMapsService.checkContext()
        @app.route("/map")
        def showMap():
            mapEmbed = GoogleMapsService.generateMapEmbedHTML(mapMode="place", mapType="satellite", classlist="maps", id="googleMap", placeQuery="Marina Bay Sands")
            return render_template("Map.html", map=mapEmbed)
        ```

        In an HTML template `Map.html`:
        ```html
        <html>
            <head>
                <style>
                    .maps {
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                {{ map|safe }}
            </body>
        </html>
        ```

        NOTE: To use `GoogleMapsService`, a Google Maps Platform API Key must be set as `GoogleMapsAPIKey` and `GoogleMapsEnabled` must be set to `True` in the .env file.
        '''

        
        # Check permission        
        if not GoogleMapsService.servicesEnabled:
            return "ERROR: Google Maps services are not enabled."
        
        # Validate inputs
        if mapMode not in ["place", "directions", "view"]:
            return "ERROR: Invalid map mode."
        if mapType not in ["roadmap", "satellite"]:
            return "ERROR: Invalid map type."
        
        ## Mode-based data validation
        if mapMode == "place" and placeQuery == None:
            return "ERROR: Place query not provided for place map mode."
        if mapMode == "directions":
            if directionsOrigin == None or directionsDestination == None or directionsMode == None:
                return "ERROR: Directions origin, destination and commute mode not provided for directions map mode."
            elif directionsMode not in ["driving", "walking", "bicycling", "transit", "flying"]:
                return "ERROR: Invalid directions mode."
        if mapMode == "view" and viewCenterCoordinates == None:
            return "ERROR: View center coordinates not provided for view map mode."
        
        # Formulate request parameters
        parameters = ["key={}".format(GoogleMapsService.gmapsAPIKey)]
        if mapMode == "place":
            parameters += [
                "q={}".format(placeQuery),
                "maptype={}".format(mapType)
            ]
        elif mapMode == "directions":
            parameters += [
                "origin={}".format(directionsOrigin),
                "destination={}".format(directionsDestination),
                "mode={}".format(directionsMode),
                "units=metric",
                "maptype={}".format(mapType)
            ]
        elif mapMode == "view":
            parameters += [
                "center={}".format(viewCenterCoordinates),
                "maptype={}".format(mapType)
            ]

        if zoom != "default":
            parameters.append("zoom={}".format(zoom))
        if mapMode != "view" and viewCenterCoordinates != None:
            parameters.append("center={}".format(viewCenterCoordinates))

        # Formulate HTML
        embedHTML = "<iframe class='{}' id='{}' width='{}' height='{}' frameborder='0' style='border:0' src='https://www.google.com/maps/embed/v1/{}?{}' allowfullscreen></iframe>".format(classlist, id, width, height, mapMode, "&".join(parameters))
        return embedHTML
    
    @staticmethod
    def generateRoute(startLocation: str, endLocation: str, mode: str, departureTime):
        # Check permission        
        if not GoogleMapsService.servicesEnabled:
            return "ERROR: Google Maps services are not enabled."
        
        if (not isinstance(startLocation, str)) or (not isinstance(endLocation, str)) or (not isinstance(mode, str)) or (not isinstance(departureTime, datetime.datetime)):
            return "ERROR: Invalid start location, end location, commute mode or departure time provided. Start location, end location and commute mode must be of type String while departureTime must be a Python datetime object."
        elif mode not in ["driving", "walking", "bicycling", "transit", "flying"]:
            return "ERROR: Invalid directions mode."
        
        # Obtain directions data from Google Maps
        try:
            directionsData = GoogleMapsService.gmapsClient.directions(startLocation, endLocation, mode=mode, departure_time=departureTime)
            # pprint.pprint(directionsData)
        except Exception as e:
            return "ERROR: Failed to obtain directions data from Google Maps; error: {}".format(e)
        
        # Extract and process relevant data
        directionsData = directionsData[0]
        response = {}
        response["copyright"] = directionsData["copyrights"]
        response["warnings"] = directionsData["warnings"]

        leg = directionsData["legs"][0]
        response["distance"] = leg["distance"]["text"]
        response["duration"] = leg["duration"]["text"]
        response["startAddress"] = leg["start_address"]
        response["endAddress"] = leg["end_address"]
        response["startLocation"] = leg["start_location"]
        response["endLocation"] = leg["end_location"]
        response["steps"] = leg["steps"]

        return response