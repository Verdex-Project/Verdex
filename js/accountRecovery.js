function emailResetKey() {
    var usernameOrEmail = document.getElementById("usernameOrEmail");
    const usernameMsg = document.getElementById("usernameMsg");
    const emailResetKeyBtn = document.getElementById("emailResetKeyBtn");

    usernameMsg.style.visibility = 'visible'

    if (!usernameOrEmail.value || usernameOrEmail.value == "") {
        usernameMsg.style.color = 'red'
        usernameMsg.innerHTML = "Please enter your email."
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
            "usernameOrEmail": usernameOrEmail.value,
        }
    }).then(response => {})
}