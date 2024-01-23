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
                        emailResetKeyBtn.innerText = "Password reset key sent!!"
                        usernameMsg.style.visibility = 'hidden'
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