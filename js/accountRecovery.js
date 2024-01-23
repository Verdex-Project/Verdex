function sendPasswordResetKey() {
    var usernameOrEmail = document.getElementById("usernameOrEmail");
    const usernameMsg = document.getElementById("usernameMsg");
    const emailResetKeyBtn = document.getElementById("emailResetKeyBtn");
    const reset = document.getElementById("reset")

    usernameMsg.style.color = 'red'
    usernameMsg.style.visibility = 'visible'

    if (!usernameOrEmail.value || usernameOrEmail.value == "") {
        usernameMsg.innerHTML = "Please enter your email."
        return
    }

    emailResetKeyBtn.disabled = true
    emailResetKeyBtn.innerText = "Sending Email..."

    axios({
        method: 'post',
        url: `/api/sendPasswordResetKey`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "usernameOrEmail": usernameOrEmail.value,
        }
    }).then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        emailResetKeyBtn.style.display = "none"
                        usernameMsg.style.color = 'green'
                        usernameMsg.innerText = response.data.substring("SUCCESS: ".length)
                        reset.style.visibility = 'visible'
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                        emailResetKeyBtn.disabled = false
                        emailResetKeyBtn.innerText = "Send Reset Key"
                    }
                } else {
                    console.log("User error occured: " + response.data)
                    usernameMsg.innerText = response.data.substring("UERROR: ".length)
                    emailResetKeyBtn.disabled = false
                    emailResetKeyBtn.innerText = "Send Reset Key"
                }
            } else {
                alert("An error occured in sending the email. Please try again.")
                console.log("Error occured in sending the email: " + response.data)
                emailResetKeyBtn.disabled = false
                emailResetKeyBtn.innerText = "Send Reset Key"
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
            emailResetKeyBtn.disabled = false
            emailResetKeyBtn.innerText = "Send Reset Key"
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later.")
        emailResetKeyBtn.disabled = false
        emailResetKeyBtn.innerText = "Send Reset Key"
    })
}

function passwordReset() {
    var resetKey = document.getElementById("resetKey")
    var newPassword = document.getElementById("newPassword")
    var cfmPassword = document.getElementById("cfmPassword")
    const resetPasswordMsg = document.getElementById("resetPasswordMsg")
    const resetPasswordBtn = document.getElementById("resetPasswordBtn")

    resetPasswordMsg.style.visibility = 'visible'
    resetPasswordMsg.style.color = 'red'

    if (!resetKey.value || resetKey.value == "" || !newPassword.value || newPassword.value == "" || !cfmPassword.value || cfmPassword.value == "") {
        resetPasswordMsg.innerHTML = "Please fill in all the fields."
        return
    }

    resetPasswordBtn.disabled = true
    resetPasswordBtn.innerText = "Changing Password..."

    axios({
        method: 'post',
        url: `/api/passwordReset`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "resetKeyValue": resetKey.value,
            "newPassword": newPassword.value.trim(),
            "cfmPassword": cfmPassword.value.trim()
        }
    }).then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        alert("Your password has been changed successfully! Please log in with your new password.")
                        location.href = `${origin}/account/login`
                    } else {
                        alert("An unknown response was recieved from Verdex Servers.")
                        console.log("Unknown response received: " + response.data)
                        resetPasswordBtn.disabled = false
                        resetPasswordBtn.innerText = "Reset Password"
                    }
                } else {
                    console.log("User error occured: " + response.data)
                    resetPasswordMsg.innerText = response.data.substring("UERROR: ".length)
                    resetPasswordBtn.disabled = false
                    resetPasswordBtn.innerText = "Reset Password"
                }
            } else {
                alert("An error occured in sending the email. Please try again.")
                console.log("Error occured in sending the email: " + response.data)
                resetPasswordBtn.disabled = false
                resetPasswordBtn.innerText = "Reset Password"
            }
        } else {
            alert("An error occured while connecting to Verdex Servers. Please try again later.")
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
            resetPasswordBtn.disabled = false
            resetPasswordBtn.innerText = "Reset Password"
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        alert("An error occured in connecting to Verdex Servers. Please try again later.")
        resetPasswordBtn.disabled = false
        resetPasswordBtn.innerText = "Reset Password"
    })
}