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

// // Get the button element by its ID
// const myButton = document.getElementById('myButton');

// // Add a click event listener to the button
// myButton.addEventListener('click', function() {
//   alert('Button clicked!');
// });