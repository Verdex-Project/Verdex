function changeUsername() {
    var newUsername = prompt("What is your new username?")
    newUsername = newUsername.trim()
    if (!newUsername || newUsername == "") {
        alert("Please provide a valid username.")
        return
    }

    axios({
        method: 'post',
        url: `/api/editUsername`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "username": newUsername
        }
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        location.reload()
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    alert("User error occured. Check logs for more information.")
                    console.log("User error occured: " + response.data)
                }
            } else {
                alert("An error occured in logging you in. Please try again or check logs for more information.")
                console.log("Error occured in making username update request: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later or check logs for more information.")
    })
}

function changeEmail() {
    var newEmail = prompt("What is your new email?")
    newEmail = newEmail.trim()
    if (!newEmail || newEmail == "") {
        alert("Please provide a valid email.")
        return
    }

    axios({
        method: 'post',
        url: `/api/editEmail`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "email": newEmail
        }
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        location.reload()
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    alert("Email already exists!")
                    console.log("User error occured: " + response.data)
                }
            } else {
                alert("An error occured in logging you in. Please try again or check logs for more information.")
                console.log("Error occured in making username update request: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later or check logs for more information.")
    })
}

function logoutIdentity() {
    axios({
        method: 'post',
        url: `/api/logoutIdentity`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {}
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        location.href = `${origin}/`;
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    alert("User error occured. Check logs for more information.")
                    console.log("User error occured: " + response.data)
                }
            } else {
                alert("An error occured in logging you in. Please try again or check logs for more information.")
                console.log("Error occured in making username update request: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later or check logs for more information.")
    })
}

function deleteIdentity() {
    axios({
        method: 'post',
        url: `/api/deleteIdentity`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {}
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        location.href = `${origin}/`;
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    alert("User error occured. Check logs for more information.")
                    console.log("User error occured: " + response.data)
                }
            } else {
                alert("An error occured in deleting your account. Please try again.")
                console.log("Error occured in making username update request: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later or check logs for more information.")
    })
}

function resendEmail() {
    axios({
        method: 'post',
        url: `/api/resendEmail`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {}
    }).then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        console.log("Email verification sent!")
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    alert("User error occured. Check logs for more information.")
                    console.log("User error occured: " + response.data)
                }
            } else {
                alert("An error occured in deleting your account. Please try again.")
                console.log("Error occured in resending email verification: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later or check logs for more information.")
    })
}