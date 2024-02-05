document.addEventListener("DOMContentLoaded", function() {
    document.addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            signIn();
        }
    });
});

function signIn() {
    const usernameInput = document.getElementById("usernameInput");
    const passwordInput = document.getElementById("passwordInput");
    const statusLabel = document.getElementById("statusLabel")
    const signInButton = document.getElementById("signInButton")

    statusLabel.style.visibility = 'visible'

    if (!usernameInput.value || usernameInput.value == "" || !passwordInput.value || passwordInput.value == "") {
        statusLabel.style.color = "red";
        statusLabel.innerHTML = "Please fill in all the fields."
        return
    }

    signInButton.disabled = true
    signInButton.innerText = "Logging you in..."

    axios({
        method: 'post',
        url: `/api/loginAccount`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "usernameOrEmail": usernameInput.value,
            "password": passwordInput.value
        }
    })
    .then(response => {
        // console.log("Response:", response);  // Add this line to print the response
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS")) {
                        signInButton.innerText = "Logged in! Redirecting now..."
                        if (response.data.startsWith("SUCCESS ITINERARYREDIRECT:")) {
                            location.href = `${origin}/editor/${response.data.substring("SUCCESS ITINERARYREDIRECT: User logged in succesfully. Itinerary ID: ".length)}`
                        } else {
                            location.href = `${origin}/account/info`;
                        }
                    } else {
                        statusLabel.style.color = "red";
                        statusLabel.innerText = "An unknown response was recieved from Verdex Servers."
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    statusLabel.style.color = "red";
                    statusLabel.innerText = response.data.substring("UERROR: ".length)
                    console.log("User error occured: " + response.data)
                }
            } else {
                statusLabel.style.color = "red";
                statusLabel.innerText = "An error occured in logging you in. Please try again later."
                console.log("Error occured in making login request: " + response.data)
            }
        } else {
            statusLabel.style.color = "red";
            statusLabel.innerText = "An error occured while connecting to Verdex Servers. Please try again later."
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
        signInButton.disabled = false
        signInButton.innerText = "Sign In"
    })
    .catch(err => {
        statusLabel.style.color = "red";
        statusLabel.innerText = "An error occured in connecting to Verdex Servers. Please try again later."
        console.log("An error occured in connecting to Verdex Servers: " + err)
        signInButton.disabled = false
        signInButton.innerText = "Sign In"
    })

}

function editElement() {
    var element = document.getElementById('editableElement');
    element.contentEditable = true; // Enable editing
    element.classList.add('editing'); // Add editing class for styling
    element.focus(); // Set focus to the edited element
    
    // Attach a blur event listener to save changes when the element loses focus
    element.addEventListener('blur', function () {
        element.contentEditable = false; // Disable editing
        element.classList.remove('editing'); // Remove editing class
    });
}