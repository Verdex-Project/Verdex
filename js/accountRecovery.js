function emailResetKey() {
    var emailInput = document.getElementById("emailInput");
    const emailMsg = document.getElementById("emailMsg");
    const emailResetKeyBtn = document.getElementById("emailResetKeyBtn");

    emailMsg.style.visibility = 'visible'

    if (!emailInput.value || emailInput.value == "") {
        changePasswordMsg.innerHTML = "Please enter your email."
        return
    }

    emailResetKeyBtn.disabled = true
    emailResetKeyBtn.innerText = "Sending Email..."

    axios({
        method: 'post',
        url: `/api/emailResetKey`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "email": emailInput.value
        }
    }).then(response => {})
}