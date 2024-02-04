function sendTestEmail() {
    var confirmation = confirm("Are you sure you want to send a test email?");
    var sendTestEmailButton = document.getElementById("test-email-button");
    sendTestEmailButton.innerHTML = "Sending...";
    sendTestEmailButton.disabled = true;
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
                    location.reload();
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                    window.alert("An error occurred: " + response.data);
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
    else {
        sendTestEmailButton.innerHTML = "Send test email";
        sendTestEmailButton.disabled = false;
    }
}
function toggleEmailer(){
    var confirmation = confirm("Are you sure you want to toggle the emailer?");
    var emailSwitch = document.getElementById("emailerSwitch")
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
                    window.alert("Emailer has been toggled successfully!");
                    location.reload();
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                    window.alert("An error occurred: " + response.data);
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
        emailSwitch.checked = !emailSwitch.checked;
    }
}

function toggleAnalytics(){
    var confirmation = confirm("Are you sure you want to toggle analytics?");
    var analyticsSwitch = document.getElementById("analyticsSwitch")
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
                    window.alert("Analytics has been toggled successfully!");
                    location.reload();
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                    window.alert("An error occurred: " + response.data);
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
        analyticsSwitch.checked = !analyticsSwitch.checked;
    }
}

function reloadDatabase(){
    var confirmation = confirm("Are you sure you want to reload the database? It is critical and could affect the whole system. Proceed with caution!");
    var reloadButton = document.getElementById("reload-database");
    reloadButton.innerHTML = "Reloading...";
    reloadButton.disabled = true;
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
                } else {
                    console.log("Unknown response received: " + response.data);
                    window.alert("Unknown response received: " + response.data);
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
        reloadButton.innerHTML = "Reload database interface";
        reloadButton.disabled = false;
    }
}

function reloadFireauth(){
    var confirmation = confirm("Are you sure you want to reload the Firebase Auth?");
    var fireAuthButton = document.getElementById("reload-fireauth");
    fireAuthButton.innerHTML = "Reloading...";
    fireAuthButton.disabled = true;
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
                    window.alert("An error occurred: " + response.data);
                }
                else {
                    console.log("Unknown response received: " + response.data);
                    window.alert("Unknown response received: " + response.data);
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
        fireAuthButton.innerHTML = "Reload Firebase Authentication";
        fireAuthButton.disabled = false;
    }
}

function reply(){{
        var email_title = document.getElementById("question-title").value;
        if (email_title === "") {
            window.alert("Please enter a title for the email.");
            return;
        }
        var email_body = document.getElementById("question-body").value;
        if (email_body === "") {
            window.alert("Please enter a body for the email.");
            return;
        }
        var email_name = document.getElementById("question-name").innerHTML;
        var email_target = document.getElementById("question-email").innerHTML;
        var questionID = document.getElementById("question-id").innerHTML;
        var questionMessage = document.getElementById("question-message").innerHTML;
        var submitButton = document.getElementById("submitButton");
        submitButton.innerHTML = "Sending...";
        submitButton.disabled = true;

        axios({
            method: 'post',
            url: '/api/reply',
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}' 
            },
            data: {
                "email_title": email_title,
                "email_body": email_body,
                "email_name": email_name,
                "email_target": email_target,
                "questionID": questionID,
                "questionMessage": questionMessage
            }
        })
        .then(response => {
            if (response.status === 200) {
                if (response.data.startsWith("SUCCESS:")) {
                    console.log("Reply sent successfully.");
                    window.alert("Reply has been sent successfully!");
                    window.location.href = '{{ url_for("admin.reply") }}'
                } else if (response.data.startsWith("ERROR:")) {
                    console.log("An error occurred: " + response.data);
                    window.alert("An error occurred: " + response.data);
                    submitButton.innerHTML = "Send email"
                }
                else {
                    console.log("Unknown response received: " + response.data);
                    window.alert("Unknown response received: " + response.data);
                }
            } else {
                console.log("Non-200 response status code received from the server.");
            }
        })
        .catch(error => {
            console.log("An error occurred while sending the reply: " + error);
        });
    }
}

function goBack(){
    window.location.href = '{{ url_for("admin.reply") }}'
}