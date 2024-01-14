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
    const usernameMsg = document.getElementById("usernameMsg");
    const emailMsg = document.getElementById("emailMsg");
    const passwordMsg = document.getElementById("passwordMsg");
    const cfmPasswordMsg = document.getElementById("cfmPasswordMsg");
//  const signUpButton = document.getElementById("signUpButton");

    // Reset all to hidden
    usernameMsg.style.visibility = 'hidden';
    usernameMsg.innerHTML = '';
    emailMsg.style.visibility = 'hidden';
    emailMsg.innerHTML = '';
    passwordMsg.style.visibility = 'hidden';
    passwordMsg.innerHTML = '';
    cfmPasswordMsg.style.visibility = 'hidden';
    cfmPasswordMsg.innerHTML = '';

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
                        cfmPasswordMsg.style.visibility = 'visible'
                        cfmPasswordMsg.style.color = "green";
                        cfmPasswordMsg.innerHTML = "Creating account..."
                        setTimeout(() => {
                            cfmPasswordMsg.innerHTML = "Account created! Redirecting now..."
                            location.href = `${origin}/account/info`;
                        }, 2000)
                    } else {
                        alert("An unknown error occured in creating the account. Please try again. Check logs for more information.")
                        console.log("Unknown response received: " + response.data)
                    }
                } else {
                    // alert("User error occured. Check logs for more information.")
                    console.log("User error occured: " + response.data)
                    if (response.data == "UERROR: Username is already taken.") {
                        usernameMsg.style.visibility = 'visible'
                        usernameMsg.style.color = 'red'
                        usernameMsg.innerHTML = "Username is already taken."
                    }
                    else if (response.data == "UERROR: Email is already in use.") {
                        emailMsg.style.visibility = 'visible'
                        emailMsg.style.color = 'red'
                        emailMsg.innerHTML = "Email is already in use."
                    }
                    else if (response.data == "UERROR: Password must be at least 6 characters long.") {
                        passwordMsg.style.visibility = 'visible'
                        passwordMsg.style.color = 'red'
                        passwordMsg.innerHTML = "Password must be at least 6 characters."
                    }
                }
            } else {
                alert("An error occured in creating your account. Please try again or check logs for more information.")
                console.log("Error occured in making login request: " + response.data)
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