const targetAttractionsBox = document.getElementById("targetAttractionsBox")
const popularAttractionsBox = document.getElementById("popularAttractionsBox")
var proceedButton = document.getElementById("proceedButton")
var proceedButton2 = document.getElementById("proceedButton2")
const cancelButton = document.getElementById("cancelButton")
const titleInput = document.getElementById("titleInput")
const descriptionInput = document.getElementById("descriptionInput")
const titleAndDescriptionBox = document.getElementById("titleAndDescriptionBox")

var locations = []
function proceedToGeneration() {
    if (locations.length == 0) {
        // Find all the locations by looping through children of targetAttractionsBox
        var targetAttractionsBox = document.getElementById("targetAttractionsBox")
        var children = targetAttractionsBox.children
        for (var i = 1; i < children.length; i++) {
            var location = children[i].children[0].innerHTML
            locations.push(location)
        }
        proceedButton.innerText = "Generate"
        targetAttractionsBox.remove()
        popularAttractionsBox.remove()
        titleAndDescriptionBox.style.visibility = "visible"
        cancelButton.remove()
        proceedButton.remove()
    } else {
        if (titleInput.value == "" || descriptionInput.value == "") {
            alert("Please enter a title and description for your itinerary.")
            return
        }

        // Change button to processing
        proceedButton2.innerText = "Processing..."
        proceedButton2.disabled = true

        // Send locations to server
        axios({
            method: 'post',
            url: `${origin}/api/generateItinerary`,
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': "\{{ API_KEY }}"
            },
            data: {
                "targetLocations": locations,
                "title": titleInput.value,
                "description": descriptionInput.value
            }
        })
        .then(response => {
            if (response.status == 200) {
                if (!response.data.startsWith("UERROR:")) {
                    if (!response.data.startsWith("ERROR:")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            const newItineraryID = response.data.substring("SUCCESS: Itinerary ID: ".length)
                            location.href = `${origin}/editor?itineraryID=${newItineraryID}`
                        } else {
                            alert("Something went wrong. Please try again.")
                            console.log("Non-success response received when submitting target locations; response: " + response.data)
                        }
                    } else {
                        alert("An error occurred. Please try again.")
                        console.log("Error response in submitting target locations; response: " + response.data)
                    }
                } else {
                    alert(response.data.substring("UERROR: ".length))
                    console.log("User error response in submitting target locations; response: " + response.data)
                }
            } else {
                alert("Something went wrong. Please try again.")
                console.log("Non-200 response received when submitting target locations; response: " + response.data)
            }
        })
        .catch(error => {
            alert("An error occurred. Please try again.")
            console.log("Error in submitting target locations; error: " + error)
        })
    }
}