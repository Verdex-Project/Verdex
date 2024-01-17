// document.addEventListener("DOMContentLoaded", function () {
//     const usernameInput = document.getElementById("usernameInput");
//     const passwordInput = document.getElementById("passwordInput");
//     const signInButton = document.getElementById("signInButton");

//     signInButton.addEventListener("click", function () {
//         const username = usernameInput.value;
//         const password = passwordInput.value;
        
//         console.log("Username:", username);
//         console.log("Password:", password);
//     });
// });


function signIn() {
    const usernameInput = document.getElementById("usernameInput");
    const passwordInput = document.getElementById("passwordInput");
    // const signInButton = document.getElementById("signInButton");

    if (!usernameInput.value || usernameInput.value == "" || !passwordInput.value || passwordInput.value == "") {
        alert("One or more fields is empty. Please try again.")
        return
    }

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
                    if (response.data.startsWith("SUCCESS:")) {
                        location.href = `${origin}/account/info`;
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