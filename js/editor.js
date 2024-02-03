function addDay(itineraryID, dayNo) {
    axios({
        method: 'post',
        url: `/api/addDay`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "itineraryID": itineraryID,
            "dayNo": parseInt(parseInt(dayNo) + 1),
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while adding a day. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            return;
        }
        console.log(response.data)
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error adding day:', error);
    });    
}

function deleteDay(itineraryID, dayNo) {
    var isConfirmedDelete = confirm(`Are you sure you want to delete this day?`);
    if (isConfirmedDelete) {
        axios({
            method: 'post',
            url: `/api/deleteDay`,
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}'
            },
            data: {
                "itineraryID": itineraryID,
                "dayNo": parseInt(dayNo),
            }
        })
        .then(function (response) {
            if (response.data.startsWith("ERROR:")){
                console.log(response.data);
                alert("An error occurred while deleting this day. Please try again.");
                return;
            }
            else if (response.data.startsWith("UERROR:")){
                console.log(response.data);
                alert(response.data.substring("UERROR: ".length));
                return;
            }
            console.log(response.data);
            location.href = `/editor/${itineraryID}/${parseInt(dayNo) - 1}`;
        })
        .catch(function (error) {
            console.error('Error deleting day:', error);
        });    
    }
}
    

function editDate(){
    document.getElementById('editDatePopup').style.display = "block"
}

function closeEditPopup(){
    window.location.reload()
}

function editDateSave(itineraryID, day, previousDate){
    const editedDate = document.getElementById("newDate").value; // Already formatted

    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1;
    const currentDay = currentDate.getDate();
    const currentDateString = `${currentYear}-${currentMonth < 10 ? '0' : ''}${currentMonth}-${currentDay < 10 ? '0' : ''}${currentDay}`;

    const oneDayMilliseconds = 24 * 60 * 60 * 1000;

    const currentDateObj = new Date(currentDateString);
    const previousDateObj = new Date(previousDate);
    const editedDateObj = new Date(editedDate);

    const utcPreviousDate = Date.UTC(previousDateObj.getFullYear(), previousDateObj.getMonth(), previousDateObj.getDate());
    const utcEditedDate = Date.UTC(editedDateObj.getFullYear(), editedDateObj.getMonth(), editedDateObj.getDate());
    const utcCurrentDate = Date.UTC(currentDateObj.getFullYear(), currentDateObj.getMonth(), currentDateObj.getDate());
    const utcMaxDate = Date.UTC(currentDateObj.getFullYear(), currentDateObj.getMonth() + 2, currentDateObj.getDate());

    const timeDifference = utcEditedDate - utcCurrentDate;
    const diffOfDays = Math.floor(timeDifference / oneDayMilliseconds);

    const timeDistanceDifference = utcMaxDate - utcEditedDate;

    const previousVSeditedDifference = utcEditedDate - utcPreviousDate;
    const diffBetweenPreviousVSedited = Math.floor(previousVSeditedDifference / oneDayMilliseconds);

    if (diffOfDays > 0){
        if (utcEditedDate > utcMaxDate){
            alert("New date cannot be more than 2 months from currrent real-time date.");
            return;
        }
    }
    if (parseInt(diffOfDays) < 0){
        alert("New date cannot be earlier than current date.");
        return;
    }
    if (parseInt(diffOfDays) == 0){
        alert("Chosen date can't be today's date!");
        return;
    }
    if (parseInt(diffBetweenPreviousVSedited) == 0){
        alert("You didn't make any changes to the date!")
        return;
    }

    axios({
        method: 'post',
        url: `/api/editDate`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "itineraryID": itineraryID,
            "day": day,
            "editedDate": editedDate
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while editing the date. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            return;
        }
        console.log(response.data)
        alert("Date sucessfully edited!")
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error editing date:', error);
    });
}

function capitalizeEachWord(str) {
    str = String(str).toLowerCase()
    return str.replace(/(^\w{1})|(\s+\w{1})/g, letter => letter.toUpperCase());
}

function isLastTwoCharsLessThan60(str) {
    var lastTwoChars = str.slice(-2)
    var lastTwoDigits = parseInt(lastTwoChars, 10)
    return (lastTwoDigits < 60)
}

function isFirstTwoCharsLessThan25(str) {
    var firstTwoChars = str.slice(0, 2);
    var firstTwoDigits = parseInt(firstTwoChars, 10);
    return (firstTwoDigits < 25);
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

function deleteActivity(activityId) {
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var dayCount = urlParts[urlParts.length - 1];
    var itineraryId = urlParts[urlParts.length - 2];
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
                    "itineraryID" : itineraryId,
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
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var itineraryId = urlParts[urlParts.length - 2];
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
                    "itineraryID" : itineraryId
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

function checkActivity(activity) {
    activity = capitalizeEachWord(activity);
    if (activity.length > 10) {
        return false
    } else {
        return true
    }
}

function checkName(name) {
    name = capitalizeEachWord(name);
    if (name.length > 40) {
        return false
    } else {
        return true
    }
}

function checkStartTime(startTime) {
    return (!isNaN(startTime) && String(startTime).length == 4 && startTime.slice(0,2) < 24 && startTime.slice(2) < 60)
}

function checkEndTime(endTime,startTime) {
    let timeDiff = parseInt(endTime) - parseInt(startTime)
    return (!isNaN(endTime) && String(endTime).length == 4 && parseInt(startTime) < parseInt(endTime) && timeDiff >= 30 && endTime.slice(0,2) < 24 && endTime.slice(2) < 60)
}

function saveActivityEdits(activityId) {
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var dayCount = urlParts[urlParts.length - 1];
    var itineraryId = urlParts[urlParts.length - 2];

    let newActivity = document.getElementById(`activityActivityModal${activityId}`).innerText
    let newName = document.getElementById(`activityNameModal${activityId}`).innerText
    let newStartTime = document.getElementById(`startTimeModal${activityId}`).innerText
    let newEndTime = document.getElementById(`endTimeModal${activityId}`).innerText
    let errorDisplayModal = document.getElementById(`errorDisplayModal${activityId}`)

    // Check format of all fields; startTime and endTime should be in 24-hr format, perform length check on other fields
    if (!(checkStartTime(newStartTime) && isLastTwoCharsLessThan60(newStartTime) && isFirstTwoCharsLessThan25(newStartTime))) {
        errorDisplayModal.innerHTML = "Start time should be in 24-hour format and 4 digits!"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newStartTime = newStartTime
    }

    if (!(checkEndTime(newEndTime, newStartTime) && isLastTwoCharsLessThan60(newEndTime) && isFirstTwoCharsLessThan25(newEndTime))) {
        errorDisplayModal.innerHTML = "End time should be in 24-hour format and 4 digits! and\n must be later than START TIME by 30 minutes"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newEndTime = newEndTime
    }

    if (!checkActivity(newActivity)) {
        errorDisplayModal.innerHTML = "Activity activity should not be more than 10 characters!"
        return
    } else {
        errorDisplayModal.innerHTML = "" 
        newActivity = capitalizeEachWord(newActivity)
    }

    if (!checkName(newName)) {
        errorDisplayModal.innerHTML = "Activity name should not be more than 40 characters!"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newName = capitalizeEachWord(newName)
    }

    // Make request via axios
    if (checkStartTime(newStartTime) && checkEndTime(newEndTime, newStartTime) && checkActivity(newActivity) && checkName(newName)) {
        axios({
            method: 'post',
            url: `/api/editActivity`,
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}'
            },
            data: {
                "itineraryID" : itineraryId,
                'dayCount' : dayCount,
                'activityId' : activityId,
                'newStartTime' : newStartTime,
                'newEndTime' : newEndTime,
                'newActivity' : newActivity,
                'newName' : newName
            }
        })
        .then(response => {
            console.log("Response:", response);  // Add this line to print the response
            if (response.status == 200) {
                if (!response.data.startsWith("ERROR:")) {
                    if (!response.data.startsWith("UERROR")) {
                        if (response.data.startsWith("SUCCESS:")) {
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
            alert("An error occured while updating your edits for your activity. Please try again later.")
        })
    }
}

function addNewActivity(activityId) {
    var currentUrl = window.location.href;
    var urlParts = currentUrl.split('/');
    var dayCount = urlParts[urlParts.length - 1];
    var itineraryId = urlParts[urlParts.length - 2];
    let newActivityId = parseInt(activityId)

    let newImageURL = document.getElementById(`newActivityImageURL${newActivityId}`).value
    let newActivity = document.getElementById(`activityActivityModal${activityId}`).innerText
    let newName = document.getElementById(`activityNameModal${activityId}`).innerText
    let newStartTime = document.getElementById(`startTimeModal${activityId}`).innerText
    let newEndTime = document.getElementById(`endTimeModal${activityId}`).innerText
    let errorDisplayModal = document.getElementById(`errorDisplayModal${activityId}`)

    // Check format of all fields; startTime and endTime should be in 24-hr format, perform length check on other fields
    if (!(checkStartTime(newStartTime) && isLastTwoCharsLessThan60(newStartTime) && isFirstTwoCharsLessThan25(newStartTime))) {
        errorDisplayModal.innerHTML = "Start time should be in 24-hour format and 4 digits!"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newStartTime = newStartTime
    }

    if (!(checkEndTime(newEndTime, newStartTime) && isLastTwoCharsLessThan60(newEndTime) && isFirstTwoCharsLessThan25(newEndTime))) {
        errorDisplayModal.innerHTML = "End time should be in 24-hour format and 4 digits! and\n must be later than START TIME by 30 minutes"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newEndTime = newEndTime
    }

    if (!checkActivity(newActivity)) {
        errorDisplayModal.innerHTML = "Activity activity should not be more than 10 characters!"
        return
    } else {
        errorDisplayModal.innerHTML = "" 
        newActivity = capitalizeEachWord(newActivity)
    }

    if (!checkName(newName)) {
        errorDisplayModal.innerHTML = "Activity name should not be more than 40 characters!"
        return
    } else {
        errorDisplayModal.innerHTML = ""
        newName = capitalizeEachWord(newName)
    }

    // Make request via axios
    if (checkStartTime(newStartTime) && checkEndTime(newEndTime, newStartTime) && checkActivity(newActivity) && checkName(newName)) {
        axios({
            method: 'post',
            url: `/api/addNewActivity`,
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}'
            },
            data: {
                "itineraryID" : itineraryId,
                'dayCount' : dayCount,
                'currentStartTime' : newStartTime,
                'currentEndTime' : newEndTime,
                'currentImageURL' : newImageURL,
                'currentActivity' : newActivity,
                'currentName' : newName,
                'newActivityID' : newActivityId
            }
        })
        .then(response => {
            console.log("Response:", response);  // Add this line to print the response
            if (response.status == 200) {
                if (!response.data.startsWith("ERROR:")) {
                    if (!response.data.startsWith("UERROR")) {
                        if (response.data.startsWith("SUCCESS:")) {
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
                    console.log("Error occured while adding a new activity to your itinerary: " + response.data)
                }
            } else {
                alert("An error occured while connecting to Verdex Servers. Please try again later.")
                console.log("Non-200 responnse status code recieved from Verdex Servers.")
            }
        })
        .catch(err => {
            console.log("An error occured in connecting to Verdex Servers: " + err)
            alert("An error occured while adding a new activity to your itinerary. Please try again later.")
        })
    }
}