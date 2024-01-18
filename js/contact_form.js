document.addEventListener('DOMContentLoaded', function() {
    var test = form_id;
    var test1 = time;
    document.getElementById('contactForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveFormData();
    });
});
function saveFormData() {
        var bodyFormData = new FormData();
        var name = document.getElementById('name').value;
        var email = document.getElementById('email').value;
        var message = document.getElementById('message').value;
        var uniqueIDFromServer = form_id;
        var timeStamp = time;
        bodyFormData.append('name', name);
        bodyFormData.append('email', email);
        bodyFormData.append('message', message);
        bodyFormData.append('form_id', uniqueIDFromServer);
        bodyFormData.append('time', timeStamp);
        
        axios({
            method: 'post',
            url: '/api/saveFormData',
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}'
            },    
            data: bodyFormData
        })
        .then(response => {
            console.log("Response:", response);  // Add this line to print the response
            if (response.status == 200) {
                if (!response.data.startsWith("ERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        alert('Form has been submitted successfully');
                        window.location.href = '/success';
                    } else {
                        alert("An error occurred when trying to save the form data into our database.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    alert("An error occurred while directing you to the next day. Please try again later.")
                    console.log("Error occurred in directing to the next day: " + response.data)
                }
            } else {
                alert("An error occurred while connecting to Verdex Servers. Please try again later.")
                console.log("Non-200 response status code received from Verdex Servers.")
            }
        })
        .catch(err => {
            console.log("An error occurred in connecting to Verdex Servers: " + err)
            alert("An error occurred while directing you to the next day. Please try again later or check your itinerary again.")
        });
    }