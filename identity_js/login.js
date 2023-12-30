document.addEventListener("DOMContentLoaded", function () {
    const usernameInput = document.getElementById("usernameInput");
    const passwordInput = document.getElementById("passwordInput");
    const signInButton = document.getElementById("signInButton");

    signInButton.addEventListener("click", function () {
        const username = usernameInput.value;
        const password = passwordInput.value;
        
        console.log("Username:", username);
        console.log("Password:", password);
    });
});