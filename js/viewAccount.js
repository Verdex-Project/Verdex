function changeUsername() {
    var newUsername = prompt("What is your new username?")
    newUsername = newUsername.trim()
    const editUsernameButton = document.getElementById("editUsernameButton")

    editUsernameButton.disabled = true
    editUsernameButton.innerText = "Changing Username..."

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
                    alert("Username is already taken.")
                    console.log("User error occured: " + response.data)
                }
            } else {
                alert("An error occured while changing your username. Please try again later.")
                console.log("Error occured in making username update request: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
        editUsernameButton.disabled = false
        editUsernameButton.innerText = "Edit"
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later.")
        editUsernameButton.disabled = false
        editUsernameButton.innerText = "Edit"
    })
}

function changeEmail() {
    var newEmail = prompt("What is your new email?")
    newEmail = newEmail.trim()
    const editEmailButton = document.getElementById("editEmailButton")

    if (!newEmail || newEmail == "") {
        alert("Please provide a valid email.")
        return
    }

    editEmailButton.disabled = true
    editEmailButton.innerText = "Changing Email..."

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
                        alert("Email changed successfully! For security reasons, you have been logged out. Please sign in again.")
                        location.href = `${origin}/account/login`
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    alert(response.data.substring("UERROR: ".length))
                    console.log("User error occured: " + response.data)
                }
            } else {
                alert("An error occured while changing your email. Please try again later.")
                console.log("Error occured in making username update request: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
        editEmailButton.disabled = false
        editEmailButton.innerText = "Edit"
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later.")
        editEmailButton.disabled = false
        editEmailButton.innerText = "Edit"
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
                alert("An error occured in logging you out. Please try again later.")
                console.log("Error occured in making username update request: " + response.data)
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later.")
    })
}

function deleteIdentity() {
    if (!confirm("Are you sure you want to delete your account?")) { return }
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
        alert("An error occured in connecting to Verdex Servers. Please try again later.")
    })
}

function resendEmail() {
    const resendEmailBtn = document.getElementById("resendEmailBtn")

    resendEmailBtn.disabled = true
    resendEmailBtn.innerText = "Resending Email..."

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
                        resendEmailBtn.innerText = "Email Resent!"
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                        resendEmailBtn.disabled = false
                        resendEmailBtn.innerText = "Resend Verification Email"
                    }
                } else {
                    alert("User error occured. Check logs for more information.")
                    console.log("User error occured: " + response.data)
                    resendEmailBtn.disabled = false
                    resendEmailBtn.innerText = "Resend Verification Email"
                }
            } else {
                if (response.data == "ERROR: Email already verified!") {
                    location.reload()
                    return
                }
                alert("An error occured in resending the email verification. Please try again.")
                console.log("Error occured in resending email verification: " + response.data)
                resendEmailBtn.disabled = false
                resendEmailBtn.innerText = "Resend Verification Email"
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
            resendEmailBtn.disabled = false
            resendEmailBtn.innerText = "Resend Verification Email"
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later.")
        resendEmailBtn.disabled = false
        resendEmailBtn.innerText = "Resend Verification Email"
    })
}

function changePassword() {
    var currentPassword = document.getElementById("currentPasswordInput");
    var newPassword = document.getElementById("newPasswordInput");
    var cfmPassword = document.getElementById("cfmPasswordInput");
    const changePasswordMsg = document.getElementById("changePasswordMsg")
    const saveBtn = document.getElementById("modalSaveBtn");
    const modal = new bootstrap.Modal(document.getElementById("newPasswordModal"));

    changePasswordMsg.style.visibility = 'visible'

    if (!currentPassword.value || currentPassword.value == "" || !newPassword.value || newPassword.value == "" || !cfmPassword.value || cfmPassword.value == "") {
        changePasswordMsg.innerHTML = "Please fill in all the fields."
        return
    }

    if (currentPassword == newPassword) {
        changePasswordMsg.innerHTML = "New password must differ from the current password."
        return
    }

    if (newPassword.value !== cfmPassword.value) {
        changePasswordMsg.innerHTML = "Passwords do not match."
        return
    }
    
    saveBtn.disabled = true
    saveBtn.innerText = "Saving Changes..."

    location.reload()
    console.log("Pass")

    // axios({
    //     method: 'post',
    //     url: '/api/createAccount',
    //     headers: {
    //         'Content-Type': 'application/json',
    //         'VerdexAPIKey': '\{{ API_KEY }}'
    //     },
    //     data: {
    //         "currentPassword": currentPassword.value,
    //         "newPassword": newPassword.value,
    //         "cfmNewPassword": cfmPassword.value
    //     }
    // })
    // .then(response => {
    //     if (response.status == 200) {
    //         if (!response.data.startsWith("ERROR:")) {
    //             if (!response.data.startsWith("UERROR:")) {
    //                 if (response.data.startsWith("SUCCESS:")) {
    //                     // signUpButton.innerHTML = "Account created! Redirecting now..."
    //                     // location.href = `${origin}/account/info`;
    //                 } else {
    //                     // cfmPasswordMsg.style.color = 'red'
    //                     // cfmPasswordMsg.innerText = "An unknown error occured in creating the account. Please try again."
    //                     console.log("Unknown response received: " + response.data)
    //                 }
    //             } else {
    //                 console.log("User error occured: " + response.data)
    //                 cfmPasswordMsg.style.color = 'red'
    //                 cfmPasswordMsg.innerText = response.data.substring("UERROR: ".length)
    //             }
    //         } else {
    //             cfmPasswordMsg.style.color = 'red'
    //             cfmPasswordMsg.innerText = "An error occured in creating your account. Please try again."
    //             console.log("Error occured in making login request: " + response.data)
    //         }
    //     } else {
    //         cfmPasswordMsg.style.color = 'red'
    //         cfmPasswordMsg.innerText = "An error occured while connecting to Verdex Servers. Please try again later."
    //         console.log("Non-200 responnse status code recieved from Verdex Servers.")
    //     }
    //     signUpButton.disabled = false
    //     signUpButton.innerText = "Sign Up"
    // })
    // .catch(err => {
    //     console.log("An error occured in connecting to Verdex Servers: " + err)
    //     cfmPasswordMsg.style.color = 'red'
    //     cfmPasswordMsg.innerText = "An error occured in connecting to Verdex Servers. Please try again later."
    //     signUpButton.disabled = false
    //     signUpButton.innerText = "Sign Up"
    // })

}