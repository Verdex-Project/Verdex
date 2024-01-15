// document.addEventListener("DOMContentLoaded", function () {
//     const usernameInput = document.getElementById("usernameInput");
//     const emailInput = document.getElementById("emailInput");
//     const passwordInput = document.getElementById("passwordInput");
//     const confirmPasswordInput = document.getElementById("confirmPasswordInput");
//     const signUpButton = document.getElementById("signUpButton");
    
//     signUpButton.addEventListener("click", function () {
//         const username = usernameInput.value;
//         const email = emailInput.value;
//         const password = passwordInput.value;
//         const confirmPassword = confirmPasswordInput.value;

//         console.log("Username:", username);
//         console.log("Email:", email);
//         console.log("Password:", password);
//         console.log("Confirm Password:", confirmPassword);
//     });
// });

function signUp() {
    const usernameInput = document.getElementById("usernameInput");
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const confirmPasswordInput = document.getElementById("confirmPasswordInput");
    const cfmPasswordMsg = document.getElementById("cfmPasswordMsg");
//  const signUpButton = document.getElementById("signUpButton");

    if (!usernameInput.value || usernameInput.value == "" || !emailInput.value || emailInput.value == "" || !passwordInput.value || passwordInput.value == "" || !confirmPasswordInput.value || confirmPasswordInput.value == "") {
        // alert("One or more fields is empty. Please try again.")
        cfmPasswordMsg.style.visibility = 'visible'
        cfmPasswordMsg.style.color = 'red'
        cfmPasswordMsg.innerHTML = "Please fill in all the fields."
        return
    }

    if (passwordInput.value !== confirmPasswordInput.value) {
        // alert("Passwords do not match.")
        cfmPasswordMsg.style.visibility = 'visible'
        cfmPasswordMsg.style.color = 'red'
        cfmPasswordMsg.innerHTML = "Passwords do not match."
        return
    }
    
    cfmPasswordMsg.style.visibility = 'visible'
    cfmPasswordMsg.style.color = "green";
    cfmPasswordMsg.innerHTML = "Creating account..."

    axios({
        method: 'post',
        url: '/api/createAccount',
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "username": usernameInput.value,
            "email": emailInput.value,
            "password": passwordInput.value
        }
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        setTimeout(() => {
                            cfmPasswordMsg.innerHTML = "Account created! Redirecting now..."
                            location.href = `${origin}/account/info`;
                        }, 2000)
                    } else {
                        cfmPasswordMsg.style.color = 'red'
                        cfmPasswordMsg.innerText = "An unknown error occured in creating the account. Please try again."
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    console.log("User error occured: " + response.data)
                    cfmPasswordMsg.style.color = 'red'
                    cfmPasswordMsg.innerText = response.data.substring("UERROR: ".length)
                }
            } else {
                cfmPasswordMsg.style.color = 'red'
                cfmPasswordMsg.innerText = "An error occured in creating your account. Please try again."
                console.log("Error occured in making login request: " + response.data)
            }
        } else {
            cfmPasswordMsg.style.color = 'red'
            cfmPasswordMsg.innerText = "An error occured while connecting to Verdex Servers. Please try again later."
            console.log("Non-200 responnse status code recieved from Verdex Servers.")
        }
    })
    .catch(err => {
        console.log("An error occured in connecting to Verdex Servers: " + err)
        cfmPasswordMsg.style.color = 'red'
        cfmPasswordMsg.innerText = "An error occured in connecting to Verdex Servers. Please try again later or check logs for more information."
    })

}