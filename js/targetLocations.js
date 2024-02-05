const targetAttractionsBox = document.getElementById("targetAttractionsBox")
const popularAttractionsCarousel = document.getElementById("popularAttractionsCarousel")
const proceedButton = document.getElementById("proceedButton")
proceedButton.disabled = true
const generateButton = document.getElementById("generateButton")
const cancelButton = document.getElementById("cancelButton")
const titleInput = document.getElementById("titleInput")
const descriptionInput = document.getElementById("descriptionInput")
const titleAndDescriptionBox = document.getElementById("titleAndDescriptionBox")

var locations = []
var locationsConfirmed = false

function addAttraction(element) {
    const attractionName = element.id.split("-")[1];

    if (locations.includes(attractionName)) {
        alert("You have already added this attraction.")
        return
    }
    locations.push(attractionName)

    let newAttraction = document.createElement("div");
    newAttraction.classList.add("attraction-item");
    newAttraction.id = "target-" + attractionName;

    let span = document.createElement("span");
    span.innerText = attractionName;

    let removeButton = document.createElement("button");
    removeButton.classList.add("btn", "btn-danger", "removeButton");
    removeButton.innerText = "Remove";
    removeButton.onclick = function () {
        removeAttraction(attractionName);
    }

    newAttraction.appendChild(span);
    newAttraction.appendChild(removeButton);
    targetAttractionsBox.appendChild(newAttraction);

    document.getElementById(element.id).innerText = "Added"
    document.getElementById(element.id).disabled = true

    if (locations.length > 0) {
        proceedButton.disabled = false
    }
}

function removeAttraction(attractionName) {
    let attraction = document.getElementById("target-" + attractionName);
    attraction.remove();

    document.getElementById("add-" + attractionName).innerText = "Add"
    document.getElementById("add-" + attractionName).disabled = false

    // Remove the attraction from the locations array
    const index = locations.indexOf(attractionName);
    if (index > -1) {
        locations.splice(index, 1);
    }

    if (locations.length <= 0) {
        proceedButton.disabled = true
    }
}

function proceed() {
    if (!locationsConfirmed) {
        if (locations.length == 0) {
            alert("Please select at least one attraction.")
            return
        }
        targetAttractionsBox.remove()
        popularAttractionsCarousel.remove()
        cancelButton.remove()
        proceedButton.remove()
        titleAndDescriptionBox.style.visibility = "visible"
        locationsConfirmed = true
    } else {
        if (titleInput.value == "" || descriptionInput.value == "") {
            alert("Please enter a title and description for your itinerary.")
            return
        }

        // Change button to processing
        generateButton.innerText = "Generating... please wait!"
        generateButton.disabled = true

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
                        if (response.data.startsWith("SUCCESS")) {
                            if (response.data.startsWith("SUCCESS ACCOUNTREDIRECT")) {
                                window.location.href = `${origin}/account/signup?fromItineraryGeneration=true`
                            } else {
                                const newItineraryID = response.data.substring("SUCCESS: Itinerary ID: ".length)
                                window.location.href = `${origin}/editor/${newItineraryID}`
                            }
                            return
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
            generateButton.innerText = "Generate"
            generateButton.disabled = false
        })
        .catch(error => {
            alert("An error occurred. Please try again.")
            console.log("Error in submitting target locations; error: " + error)
            generateButton.innerText = "Generate"
            generateButton.disabled = false
        })
    }
}

function handleTypewriterEffect(resultDiv, generatedText, maxLength) {
    console.log(generatedText)
    const characters = generatedText.split('');
    let i = 0;

    const intervalId = setInterval(() => {
        resultDiv.innerHTML += characters[i];
        i++;

        if (i === characters.length || i === maxLength) {
            clearInterval(intervalId);
        }
    }, 5); 
}

function submitPrompt() {
    document.getElementById('response').innerHTML = "Hold tight! Verdex-GPT is thinking..."
    const prompt = document.getElementById("prompt");

    if (prompt.value !== "") {
        axios({
            method: 'post',
            url: `/api/verdexgpt`,
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}'
            },
            data: {
                "prompt": prompt.value
            }
        })
        .then(function (response) {
            console.log("Payload successfully sent")

            console.log(response.data);

            const resultDiv = document.getElementById('response');

            const maxLength = 1800;

            resultDiv.innerHTML = '';

            handleTypewriterEffect(resultDiv, response.data.generated_text, maxLength);
        })
        .catch(function (error) {
            console.error('Error generating text completion:', error);
        });
    } else {
        alert("Please enter a valid prompt.");
        return;
    }
}