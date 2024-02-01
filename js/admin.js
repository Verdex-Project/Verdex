function sendTestEmail() {
    var confirmation = confirm("Are you sure you want to send a test email?");
    if (confirmation) {
        axios({
            method: 'post',
            url: '/api/sendTestEmail',
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}' 
            },
            data: {}
        })
        .then(response => {
            if (response.status === 200) {
                if (response.data.startsWith("SUCCESS:")) {
                    console.log("Test email sent successfully.");
                    window.alert("Test email has been sent successfully!");
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                } 
                else {
                    console.log("Unknown response received: " + response.data);
                }
            } else {
                console.log("Non-200 response status code received from the server.");
            }
        })
        .catch(error => {
            console.log("An error occurred while sending the test email: " + error);
        });
    }
}
function toggleEmailer(){
    var confirmation = confirm("Are you sure you want to toggle the emailer?");
    if (confirmation) {
        axios({
            method: 'post',
            url: '/api/toggleEmailer',
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}' 
            },
            data: {}
        })
        .then(response => {
            if (response.status === 200) {
                if (response.data.startsWith("SUCCESS:")) {
                    console.log("Emailer toggled successfully.");
                    location.reload();
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                } 
                else {
                    console.log("Unknown response received: " + response.data);
                }
            } else {
                console.log("Non-200 response status code received from the server.");
            }
        })
        .catch(error => {
            console.log("An error occurred while toggling the emailer: " + error);
        });
    }
    else {
        window.alert("Emailer toggle cancelled.");
        location.reload();
    }
}

function toggleAnalytics(){
    var confirmation = confirm("Are you sure you want to toggle analytics?");
    if (confirmation) {
        axios({
            method: 'post',
            url: '/api/toggleAnalytics',
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}' 
            },
            data: {}
        })
        .then(response => {
            if (response.status === 200) {
                if (response.data.startsWith("SUCCESS:")) {
                    console.log("Analytics toggled successfully.");
                    location.reload();
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                } 
                else {
                    console.log("Unknown response received: " + response.data);
                }
            } else {
                console.log("Non-200 response status code received from the server.");
            }
        })
        .catch(error => {
            console.log("An error occurred while toggling analytics: " + error);
        });
    }
    else {
        window.alert("Analytics toggle cancelled.");
        location.reload();
    }
}

function reloadDatabase(){
    var confirmation = confirm("Are you sure you want to reload the database?");
    if (confirmation) {
        axios({
            method: 'post',
            url: '/api/reload_database',
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}' 
            },
            data: {}
        })
        .then(response => {
            if (response.status === 200) {
                if (response.data.startsWith("SUCCESS:")) {
                    console.log("Database reloaded successfully.");
                    window.alert("Database has been reloaded successfully!");
                    location.reload();
                }
                else if (response.data.startsWith("UERROR:")) {
                    console.log("User error occurred: " + response.data.substring("UERROR: ".length));
                } else {
                    console.log("Unknown response received: " + response.data);
                }
            } else {
                console.log("Non-200 response status code received from the server.");
            }
        })
        .catch(error => {
            console.log("An error occurred while reloading the database: " + error);
        });
    }
    else {
        window.alert("Database reload cancelled.");
        location.reload();
    }
}

function reloadFireauth(){
    var confirmation = confirm("Are you sure you want to reload the Firebase Auth?");
    if (confirmation) {
        axios({
            method: 'post',
            url: '/api/reload_fireauth',
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}' 
            },
            data: {}
        })
        .then(response => {
            if (response.status === 200) {
                if (response.data.startsWith("SUCCESS:")) {
                    console.log("Firebase Auth reloaded successfully.");
                    window.alert("Firebase Auth has been reloaded successfully!"); 
                    location.reload();
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                }
                else {
                    console.log("Unknown response received: " + response.data);
                }
            } else {
                console.log("Non-200 response status code received from the server.");
            }
        })
        .catch(error => {
            console.log("An error occurred while reloading the Firebase Auth: " + error);
        });
    }
    else {
        window.alert("Firebase Auth reload cancelled.");
        location.reload();
    }
}