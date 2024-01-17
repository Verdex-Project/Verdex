// function allowDrop(event) {
//     event.preventDefault();
// }

// function drag(event) {
//     event.dataTransfer.setData("text", event.target.id);
// }

// function drop(event) {
//     event.preventDefault();
//     var fetchData = event.dataTransfer.getData("text");
//     event.target.appendChild(document.getElementById(fetchData));
// }

function capitalizeEachWord(str) {
    str = String(str).toLowerCase()
    return str.replace(/(^\w{1})|(\s+\w{1})/g, letter => letter.toUpperCase());
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

function editActivity(activityId, location, name, startTime, endTime) {
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
            let newActivityLocation = ""
            while (newActivityLocation == "") {
            newActivityLocation = prompt("Enter a new activity Location (Exp. Singapore):\nNOTE: LENGTH IS NOT MORE THAN 10 WORDS\n\nLeave here blank if you don't want to change ");
                if (newActivityLocation == "") {
                    newActivityLocation = currentActivityLocation;
                } else if (newActivityLocation.length >10){
                    alert("Invalid input.\n\nInput LESS THAN 10 WORDS are accepted only");
                    newActivityLocation = "";
                } else {
                    newActivityLocation = capitalizeEachWord(newActivityLocation);
                    break;
                }
            }
            let newActivityName = ""
            while (newActivityName == "") {
            newActivityName = prompt("Enter a new activity name (Exp. Marina Bay Sands):\nNOTE: LENGTH IS NOT MORE THAN 25 WORDS\n\nLeave here blank if you don't want to change ");
                if (newActivityName == "") {
                    newActivityName = currentActivityName
                } else if (newActivityName.length >25){
                    alert("Invalid input.\n\nInput LESS THAN 25 WORDS are accepted only");
                    newActivityName = "";
                } else {
                    newActivityName = capitalizeEachWord(newActivityName);
                    break;
                }
            }
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
            var currentUrl = window.location.href;
            var urlParts = currentUrl.split('/');
            var dayCount = urlParts[urlParts.length - 1];
            let currentActivityId = activityId
            let currentActivityStartTime = startTime;
            let currentActivityEndTime = endTime;
            let newActivityStartTime = ""
            while (newActivityStartTime == "") {
            newActivityStartTime = prompt("Enter a new activity start time (Exp. 1200):\n\nLeave here blank if you don't want to change ");
                if (newActivityStartTime == "") {
                    newActivityStartTime = currentActivityStartTime;
                    break;
                } else if (isNaN(newActivityStartTime) || newActivityStartTime.length !== 4) {
                    alert("Invalid input.\n\nPlease enter a valid number for the start time.\n\nOR\n\nPlease enter a 4 DIGIT number to represent the time");
                    newActivityStartTime = "";
                } else {
                    break;
                }
            }
            let newActivityEndTime = ""
            while(newActivityEndTime == "") {
            newActivityEndTime = prompt("Enter a new activity end time (Exp. 1200):\n\nLeave here blank if you don't want to change ");
                if (newActivityEndTime == "") {
                    newActivityEndTime = currentActivityEndTime
                    break;
                } else if (isNaN(newActivityEndTime) || newActivityStartTime.length !== 4) {
                    alert("Invalid input.\n\nPlease enter a valid number for the start time.\n\nOR\n\nPlease enter a 4 DIGIT number to represent the time");
                    newActivityEndTime = "";
                } else {
                    break;
                }
            }
            axios({
                method: 'post',
                url: `/api/newActivityStartEndTime`,
                headers: {
                    'Content-Type': 'application/json',
                    'VerdexAPIKey': '\{{ API_KEY }}'
                },
                data: {
                    "newActivityStartTime" : newActivityStartTime,
                    "newActivityEndTime" : newActivityEndTime,
                    "day" : dayCount,
                    "activityId": currentActivityId
                }
            })
            .then(response => {
                console.log("Response:", response);  // Add this line to print the response
                if (response.status == 200) {
                    if (!response.data.startsWith("ERROR:")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            alert("Your new activity start time and end time is updated!");
                            window.location.reload();
                        } else {
                            alert("An unknown response was recieved from Verdex Servers.")
                            console.log("Unknown response received: " + response.data)
                        }
                    } else {
                        alert("An error occured while updating your new activity start time and end time. Please try again later.")
                        console.log("Error occured updating new activity start time and end time: " + response.data)
                    }
                } else {
                    alert("An error occured while connecting to Verdex Servers. Please try again later.")
                    console.log("Non-200 responnse status code recieved from Verdex Servers.")
                }
            })
            .catch(err => {
                console.log("An error occured in connecting to Verdex Servers: " + err)
                alert("An error occured while updating your new activity start time and end time. Please try again later or check the value that you've input.")
            })   
            break;            
        }
        if (value == "3" || value == null) {
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
        if (deleteStatus == true) {
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

function deleteItinerary() {
    let deleteItineraryStatus = false;
    while (deleteItineraryStatus == false ){
    deleteItineraryStatus = confirm("Are you sure you want to delete your itinerary?")
        if (deleteItineraryStatus == true) {
            axios({
                method: 'post',
                url: `/api/deleteItinerary`,
                headers: {
                    'Content-Type': 'application/json',
                    'VerdexAPIKey': '\{{ API_KEY }}'
                },
                data: {
                }
            })
            .then(response => {
                console.log("Response:", response);  // Add this line to print the response
                if (response.status == 200) {
                    if (!response.data.startsWith("ERROR:")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            alert("Your Itinerary is deleted successfully!");
                            window.location.reload()
                            window.location.href='/';
                        } else {
                            alert("An unknown response was recieved from Verdex Servers.")
                            console.log("Unknown response received: " + response.data)
                        }
                    } else {
                        alert("An error occured while deleting your itinerary. Please try again later.")
                        console.log("Error occured deleting your itinerary: " + response.data)
                    }
                } else {
                    alert("An error occured while connecting to Verdex Servers. Please try again later.")
                    console.log("Non-200 responnse status code recieved from Verdex Servers.")
                }
            })
            .catch(err => {
                console.log("An error occured in connecting to Verdex Servers: " + err)
                alert("An error occured while deleting your itinerary. Please try again later.")
            })
            break;
        }
        else {
            break;
        }
    }
}

// errorModal = []

// function newStartTime(currentStartTime){ 
//     let newStartTime = document.getElementById(startTimeModal);
//     let errorStartTime = "";
//     let currentStartTime = currentStartTime;
//     while (true) {
//         if (newStartTime.length !== 4 && isNaN(newActivityEndTime)){
//             newStartTime = currentStartTime
//             errorStartTime = "EDIT TIME must be 4 numbers"
//             break
//         } else {
//             newStartTime = newStartTime
//             errorStartTime = ""
//             break
//         }
//     }
//     if (errorStartTime != "") {
//         errorModal.push(errorStartTime);
//     }
// }

function checkLocation(location) {
    location = capitalizeEachWord(location);
    if (location.length > 10) {
        return false
    } else {
        return true
    }
}

function checkName(name) {
    name = capitalizeEachWord(name);
    if (name.length > 25) {
        return false
    } else {
        return true
    }
}

function checkStartTime(startTime) {
    return (!isNaN(startTime) && String(startTime).length == 4)
}

function checkEndTime(endTime,startTime) {
    let timeDiff = parseInt(endTime) - parseInt(startTime)
    return (!isNaN(endTime) && String(endTime).length == 4 && parseInt(startTime) < parseInt(endTime) && timeDiff > 30)
}

function saveActivityEdits(activityId,location, name, startTime, endTime) {
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var dayCount = urlParts[urlParts.length - 1];

    let currentLocation = location
    let currentName = name
    let currentstartTime = startTime
    let currentendTime = endTime

    let newLocation = document.getElementById(`activityLocationModal${activityId}`).innerText
    let newName = document.getElementById(`activityNameModal${activityId}`).innerText
    let newStartTime = document.getElementById(`startTimeModal${activityId}`).innerText
    let newEndTime = document.getElementById(`endTimeModal${activityId}`).innerText
    let errorDisplayModal = document.getElementById(`errorDisplayModal${activityId}`)

    console.log(newLocation)
    console.log(newName)
    console.log(newStartTime)
    console.log(newEndTime)
    console.log("Start Time:", newStartTime);
    console.log("String(startTime).length:", String(newStartTime).length);
    

    // Check format of all fields; startTime and endTime should be in 24-hr format, perform length check on other fields
    if (!checkStartTime(newStartTime)) {
        errorDisplayModal.innerHTML = "Start time should be in 24-hour format and 4 digits!"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newStartTime = newStartTime
    }

    if (!checkEndTime(newEndTime, newStartTime)) {
        errorDisplayModal.innerHTML = "End time should be in 24-hour format and 4 digits! and must not be earlier than START TIME"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newEndTime = newEndTime
    }

    if (!checkLocation(newLocation)) {
        errorDisplayModal.innerHTML = "Activity location should not be more than 10 characters!"
        return
    } else {
        errorDisplayModal.innerHTML = "" 
        newLocation = capitalizeEachWord(newLocation)
    }

    if (!checkName(newName)) {
        errorDisplayModal.innerHTML = "Activity name should not be more than 25 characters!"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newName = capitalizeEachWord(newName)
    }


    console.log(checkStartTime(newStartTime) && checkEndTime(newEndTime) && checkLocation(newLocation) && checkName(newName))
    console.log(checkStartTime(newStartTime))
    console.log(checkEndTime(newEndTime, newStartTime))
    console.log(checkLocation(newLocation))
    console.log(checkName(newName))

    // Make request via axios
    if (checkStartTime(newStartTime) && checkEndTime(newEndTime, newStartTime) && checkLocation(newLocation) && checkName(newName)) {
        axios({
            method: 'post',
            url: `/api/editActivityModal`,
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}'
            },
            data: {
                'dayCount' : dayCount,
                'activityId' : activityId,
                'newStartTime' : newStartTime,
                'newEndTime' : newEndTime,
                'newLocation' : newLocation,
                'newName' : newName
            }
        })
        .then(response => {
            console.log("Response:", response);  // Add this line to print the response
            if (response.status == 200) {
                if (!response.data.startsWith("ERROR:")) {
                    if (!response.data.startsWith("UERROR")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            alert("Your Itinerary is edited successfully!");
                            window.location.reload();
                        } else {
                            alert("An unknown response was recieved from Verdex Servers.")
                            console.log("Unknown response received: " + response.data)
                        }
                    } else {
                        alert("User error occured. Check for user inputs and try again")
                        console.log("User error occurred; error: " + response.data)
                    }
                } else {
                    alert("An error occured while updating your edits for your activity. Please try again later.")
                    console.log("Error occured while updating your edits for your activity: " + response.data)
                }
            } else {
                alert("An error occured while connecting to Verdex Servers. Please try again later.")
                console.log("Non-200 responnse status code recieved from Verdex Servers.")
            }
        })
        .catch(err => {
            console.log("An error occured in connecting to Verdex Servers: " + err)
            alert("An error occured while  updating your edits for your activity. Please try again later.")
        })
    }
}


// // Get the button element by its ID
// const myButton = document.getElementById('myButton');

// // Add a click event listener to the button
// myButton.addEventListener('click', function() {
//   alert('Button clicked!');
// });