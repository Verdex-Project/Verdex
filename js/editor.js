function allowDrop(event) {
    event.preventDefault();
}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id);
}

function drop(event) {
    event.preventDefault();
    var fetchData = event.dataTransfer.getData("text");
    event.target.appendChild(document.getElementById(fetchData));
}

function nextDay(){
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var dayCount = urlParts[urlParts.length - 1];
    var itineraryId = urlParts[urlParts.length - 2];
    var newDayCount= String(parseInt(dayCount) + 1);
    var newDay;
    axios({
        method: 'post',
        url: `/api/nextDay`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "nextDay": newDayCount,
            "itineraryID" : itineraryId
        }
    })
    .then(response => {
        console.log("Response:", response);  // Add this line to print the response
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (response.data.startsWith("SUCCESS:")) {
                    newDay = newDayCount
                    location.href = `/editor/${itineraryId}/${newDay}`;
                } else {
                    alert("An unknown response was recieved from Verdex Servers.")
                    console.log("Unknown response received: " + response.data)
                }
            } else {
                alert("An error occured while directing you to the next day. Please try again later.")
                console.log("Error occured in directing to the next day: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured while directing you to the next day. Please try again later or check you itinerary again.")
    })
    }

function previousDay(){
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var dayCount = urlParts[urlParts.length - 1];
    var itineraryId = urlParts[urlParts.length - 2];
    var previousDayCount= String(parseInt(dayCount) - 1);
    var previousDay;
    axios({
        method: 'post',
        url: `/api/previousDay`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "previousDay": previousDayCount,
            "itineraryID" : itineraryId
        }
    })
    .then(response => {
        console.log("Response:", response);  // Add this line to print the response
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (response.data.startsWith("SUCCESS:")) {
                    previousDay = previousDayCount
                    location.href = `/editor/${itineraryId}/${previousDay}`;
                } else {
                    alert("An unknown response was recieved from Verdex Servers.")
                    console.log("Unknown response received: " + response.data)
                }
            } else {
                alert("An error occured while directing you to the previous day. Please try again later.")
                console.log("Error occured in directing to the previous day: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured while directing you to the previous day. Please try again later or check you itinerary again.")
    })
    }

function editActivity(activityId, location, name) {
    let value = "";
    while (value == "") {
    value = prompt("Which one do you want to change : \n 1: Activity Name and Location \n 2: Activity Time \n 3: Exit" )
        if (value == "1") {
            var currentUrl = window.location.href;
            var urlParts = currentUrl.split('/');
            var dayCount = urlParts[urlParts.length - 1];
            let currentActivityId = activityId
            let currentActivityLocation = location;
            let currentActivityName = name;
            let newActivityLocation = prompt("Enter a new activity Location (Exp. Singapore):\n\nLeave here blank if you don't want to change ");
            if (newActivityLocation == "") {
                newActivityLocation = currentActivityLocation
            };
            let newActivityName = prompt("Enter a new activity name (Exp. Marina Bay Sands):\n\nLeave here blank if you don't want to change ");
            if (newActivityName == "") {
                newActivityName = currentActivityName
            };
            axios({
                method: 'post',
                url: `/api/newActivityLocationName`,
                headers: {
                    'Content-Type': 'application/json',
                    'VerdexAPIKey': '\{{ API_KEY }}'
                },
                data: {
                    "newActivityName" : newActivityName,
                    "newActivityLocation" : newActivityLocation,
                    "day" : dayCount,
                    "activityId": currentActivityId
                }
            })
            .then(response => {
                console.log("Response:", response);  // Add this line to print the response
                if (response.status == 200) {
                    if (!response.data.startsWith("ERROR:")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            alert("Your new activity location and name is updated!");
                            window.location.reload();
                        } else {
                            alert("An unknown response was recieved from Verdex Servers.")
                            console.log("Unknown response received: " + response.data)
                        }
                    } else {
                        alert("An error occured while updating your new activity location and name. Please try again later.")
                        console.log("Error occured updating new activity location and name: " + response.data)
                    }
                } else {
                    alert("An error occured while connecting to Verdex Servers. Please try again later.")
                    console.log("Non-200 responnse status code recieved from Verdex Servers.")
                }
            })
            .catch(err => {
                console.log("An error occured in connecting to Verdex Servers: " + err)
                alert("An error occured while updating your new activity location and name. Please try again later or check the value that you've input.")
            })
            break;
        }
        if (value == "2"){
            // edit time here
            break;
        }
        if (value == "3") {
            break;
        }
        else {
            alert("Please select a number that identicates the attribute that you would like to edit. \n\nIf you want to QUIT editing, TYPE 3")
            value = ""
            // value = prompt("Which one do you want to change : \n 1: Activity Name and Location \n 2: Activity Time \n 3: Exit" )
        }
    }
}

function deleteActivity(activityId) {
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var dayCount = urlParts[urlParts.length - 1];
    deleteStatus = false
    while (deleteStatus == false ){
    deleteStatus = confirm("Are you sure you want to delete this activity?")
        if (deleteStatus = true) {
            axios({
                method: 'post',
                url: `/api/deleteActivity`,
                headers: {
                    'Content-Type': 'application/json',
                    'VerdexAPIKey': '\{{ API_KEY }}'
                },
                data: {
                    "day" : dayCount,
                    "activityId": activityId
                }
            })
            .then(response => {
                console.log("Response:", response);  // Add this line to print the response
                if (response.status == 200) {
                    if (!response.data.startsWith("ERROR:")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            alert("This activity is deleted successfully!");
                            window.location.reload();
                        } else {
                            alert("An unknown response was recieved from Verdex Servers.")
                            console.log("Unknown response received: " + response.data)
                        }
                    } else {
                        alert("An error occured while deleting your activity. Please try again later.")
                        console.log("Error occured deleting your activity: " + response.data)
                    }
                } else {
                    alert("An error occured while connecting to Verdex Servers. Please try again later.")
                    console.log("Non-200 responnse status code recieved from Verdex Servers.")
                }
            })
            .catch(err => {
                console.log("An error occured in connecting to Verdex Servers: " + err)
                alert("An error occured while deleting your activity. Please try again later.")
            })
            break;
        }
        else {
            break;
        }
    }
}

// // Get the button element by its ID
// const myButton = document.getElementById('myButton');

// // Add a click event listener to the button
// myButton.addEventListener('click', function() {
//   alert('Button clicked!');
// });