var commentedPostId = null
var editPostId = null
var authorAccID = null

function createPostPopup() {
    document.getElementById("create-a-post-popup").style.display = "block";
}

function itineraryShortcutButtonPopup(shortcut) {
    document.getElementById("create-a-post-popup").style.display = "block";
    document.getElementById("post-title").value = shortcut
}

function closeCreatePopup() {
    closeCreateConfirmation = confirm("Are you sure you'd like to discard all changes?");
    if (closeCreateConfirmation == true) {
        window.location.reload();
        selectedTag = ""
    }
}

function closeCommentPopup(){
    closeCommentConfirmation = confirm("Are you sure you'd like to discard all changes?");
    if (closeCommentConfirmation == true) {
        window.location.reload();
    }
}

function closeEditPopup() {
    confirmation = confirm("Are you sure you'd like to discard all changes?");
    if (confirmation == true) {
        window.location.reload();
    }
}

let selectedTag = ""
function submitPost() {
    document.getElementById("post-tag").value = selectedTag;
    const post_title = document.getElementById("post-title");
    const post_description = document.getElementById("post-description");
    const post_tag = document.getElementById("post-tag");

    if (post_title.value.trim() === ""){
        alert("Please enter a valid post title")
        return;
    }
    if (post_description.value.trim() === ""){
        alert("Please enter a valid post desription")
        return;
    }

    axios({
        method: 'post',
        url: `/api/submitPost`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "post_title": post_title.value,
            "post_description": post_description.value,
            "post_tag": post_tag.value
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while submitting post. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            return;
        }
        console.log(response.data)
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error creating post:', error);
    });
}

function likePost(postId) {
    axios.post('/api/likePost', { postId: postId }, { headers: { 'Content-Type': 'application/json', 'VerdexAPIKey': '\{{ API_KEY }}' } })
        .then(function (response) {
            if (typeof response.data !== "string") {
                const likesCountElement = document.getElementById('likes-count');
                console.log('likesCountElement:', likesCountElement);

                if (likesCountElement) {
                    likesCountElement.textContent = ` (${response.data.likes})`;
                } else {
                    console.error('Error: likesCountElement not found.');
                }
            } else if (response.data.startsWith("ERROR:")) {
                console.log(response.data);
                alert("An error occurred while liking the post. Please try again.");
                return;
            } else if (response.data.startsWith("UERROR:")) {
                console.log(response.data);
                alert(response.data.substring("UERROR: ".length));
                return;
            }
        })
        .catch(function (error) {
            console.error('Error liking post:', error);
        });
}

function deletePost(postId){
    confirmation = confirm("Are you sure you want to delete this post?")
    if (confirmation){
        axios.post('/api/deletePost', { postId: postId }, { headers: { 'Content-Type': 'application/json', 'VerdexAPIKey': '\{{ API_KEY }}' } })
        .then(response => {
            if (response.data.startsWith("ERROR:")){
                console.log(response.data)
                alert("An error occured while deleting post. Please try again.")
                return;
            }
            else if (response.data.startsWith("UERROR:")){
                console.log(response.data)
                alert(response.data.substring("UERROR: ".length))
                return;
            }
            console.log(response.data);
            window.location.reload();
        })
        .catch(error => {
            console.error(error);
        });
    }
}

function commentPost(postId) {
    document.getElementById("comment-on-post-popup").style.display = "block";
    commentedPostId = postId;
}

function submitComment() {
    const commentDescription = document.getElementById("comment_description");
    const postId = commentedPostId;

    if (!commentDescription.value || commentDescription.value == "" || commentDescription.value.trim() == "") {
        alert("Please enter a valid comment.")
        return
    }

    axios({
        method: 'post',
        url: `/api/commentPost`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "post_id": postId,
            "comment_description": commentDescription.value
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while commenting on post. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            return;
        }
        console.log(response.data)
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error commenting on post:', error);
    });
}

function editPost(postId) {
    editPostId = postId;

    axios({
        method: 'post',
        url: `/api/openEditPost`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "post_id": editPostId
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while trying to edit post. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            document.getElementById("edit-post-popup").style.display = "none";
            return;
        }
        else if (response.data.startsWith("SUCCESS:")){
            document.getElementById("edit-post-popup").style.display = "block";
        }
    })
    .catch(function (error) {
        console.error('Error trying to edit post:', error);
    });
}

let editedSelectedTag = ""
function submitEdit() {
    document.getElementById("edit-post-tag").value = editedSelectedTag;
    const editPostTitle = document.getElementById("edit-post-title").value;
    const editPostDescription = document.getElementById("edit-post-description").value;
    const editPostTag = document.getElementById("edit-post-tag").value;
    const postId = editPostId;

    if (editPostTitle.trim() === "") {
        alert("Please enter a valid title.");
        return;
    }
    else if (editPostDescription.trim() === "") {
        alert("Please enter a valid description.");
        return;
    }

    axios({
        method: 'post',
        url: `/api/editPost`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "post_id": postId,
            "edit_post_title": editPostTitle,
            "edit_post_description": editPostDescription,
            "edit_post_tag": editPostTag
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while submitting edit. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            return;
        }
        console.log(response.data)
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error editing post:', error);
    });
}

function selectTag(tag, event, buttonToEnable, firstButtonToDisable, secondButtonToDisable) {
    if (selectedTag === tag) {
        selectedTag = "";
        document.getElementById(buttonToEnable).style.backgroundColor = "white";
        document.getElementById(buttonToEnable).style.color = "black";
    } else {
        selectedTag = tag;
        document.getElementById(buttonToEnable).style.backgroundColor = "#66BB69";
        document.getElementById(buttonToEnable).style.color = "white";

        document.getElementById(firstButtonToDisable).style.backgroundColor = "white";
        document.getElementById(firstButtonToDisable).style.color = "black";

        document.getElementById(secondButtonToDisable).style.backgroundColor = "white";
        document.getElementById(secondButtonToDisable).style.color = "black";
    }

    event.preventDefault();
    event.stopPropagation();
}

function editSelectTag(tag, event, buttonToEnable, firstButtonToDisable, secondButtonToDisable) {
    if (editedSelectedTag === tag) {
        editedSelectedTag = "";
        document.getElementById(buttonToEnable).style.backgroundColor = "white";
        document.getElementById(buttonToEnable).style.color = "black";
    } else {
        editedSelectedTag = tag;
        document.getElementById(buttonToEnable).style.backgroundColor = "#66BB69";
        document.getElementById(buttonToEnable).style.color = "white";

        document.getElementById(firstButtonToDisable).style.backgroundColor = "white";
        document.getElementById(firstButtonToDisable).style.color = "black";

        document.getElementById(secondButtonToDisable).style.backgroundColor = "white";
        document.getElementById(secondButtonToDisable).style.color = "black";
    }

    event.preventDefault();
    event.stopPropagation();
}

function filterPosts(tagToDisplay) {
    var allPosts = document.querySelectorAll('.post-section-container > #individual-posts');

    allPosts.forEach(function(post) {
        var postTag = post.classList[0]; 
        if (tagToDisplay == 'All' || postTag == tagToDisplay) {
            post.style.display = "block";
        } else {
            post.style.display = "none";
        }
    });
    console.log(allPosts)
}

function deleteComment(postId, commentId){
    confirmation = confirm("Are you sure you want to delete this comment?")
    if (confirmation){
        axios.post('/api/deleteComment', { postId: postId, commentId: commentId}, { headers: { 'Content-Type': 'application/json', 'VerdexAPIKey': '\{{ API_KEY }}' } })
        .then(response => {
            if (response.data.startsWith("ERROR:")){
                console.log(response.data)
                alert("An error occured while deleting comment. Please try again.")
                return;
            }
            else if (response.data.startsWith("UERROR:")){
                console.log(response.data)
                alert(response.data.substring("UERROR: ".length))
                return;
            }
            console.log(response.data);
            window.location.reload();
        })
        .catch(error => {
            console.error(error);
        });
    }
}

function createPostPopupWithItinerary(itinerary_id, itinerary_title, itinerary_description){
    document.getElementById('create-a-post-popup-with-itinerary').style.display = "block";
    document.getElementById('itinerary-id').value = itinerary_id
    document.getElementById('itinerary-title').value = "Itinerary title: " + itinerary_title
    document.getElementById('itinerary-description').value = "Itinerary description: " + itinerary_description
}

let itinerarySelectedTag = ""
function submitPostWithItinerary(){
    document.getElementById("itinerary-post-tag").value = itinerarySelectedTag;
    const itinerary_id = document.getElementById('itinerary-id');
    const itinerary_post_title = document.getElementById("itinerary-post-title");
    const itinerary_post_description = document.getElementById('itinerary-post-description');
    const itinerary_post_tag = document.getElementById("itinerary-post-tag");
    const itinerary_title = document.getElementById('itinerary-title');
    const itinerary_description = document.getElementById('itinerary-description');

    if (itinerary_post_title.value.trim() === ""){
        alert("Please enter a valid post title")
        return;
    }
    if (itinerary_post_description.value.trim() === ""){
        alert("Please enter a valid post desription")
        return;
    }

    axios({
        method: 'post',
        url: `/api/submitPostWithItinerary`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "itinerary_id": itinerary_id.value,
            "itinerary_post_title": itinerary_post_title.value,
            "itinerary_post_tag": itinerary_post_tag.value,
            "itinerary_title": itinerary_title.value,
            "itinerary_post_description": itinerary_post_description.value,
            "itinerary_description": itinerary_description.value
        }
    })
    .then(function (response) {
        console.log("Payload successfully sent")
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while sharing itinerary. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            return;
        }
        console.log(response.data)
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error sharing itinerary:', error);
    });
}

function itinerarySelectTag(tag, event, buttonToEnable, firstButtonToDisable, secondButtonToDisable){
    if (itinerarySelectedTag === tag) {
        itinerarySelectedTag = "";
        document.getElementById(buttonToEnable).style.backgroundColor = "white";
        document.getElementById(buttonToEnable).style.color = "black";
    } else {
        itinerarySelectedTag = tag;
        document.getElementById(buttonToEnable).style.backgroundColor = "#66BB69";
        document.getElementById(buttonToEnable).style.color = "white";

        document.getElementById(firstButtonToDisable).style.backgroundColor = "white";
        document.getElementById(firstButtonToDisable).style.color = "black";

        document.getElementById(secondButtonToDisable).style.backgroundColor = "white";
        document.getElementById(secondButtonToDisable).style.color = "black";
    }

    event.preventDefault();
    event.stopPropagation();
}

function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('dark-mode');

    // Check if dark mode is currently active
    const isDarkMode = body.classList.contains('dark-mode');
    if (isDarkMode){
        document.getElementById('verdexNavbar').classList.add("bg-dark")
        document.getElementById('verdexNavbar').setAttribute("data-bs-theme", "dark")
    }
    else {
        document.getElementById('verdexNavbar').classList.remove("bg-dark")
        document.getElementById('verdexNavbar').removeAttribute("data-bs-theme")
    }
    // Store the current dark mode state in localStorage
    localStorage.setItem('darkMode', isDarkMode);

    // Update the toggle button state
    const darkModeToggle = document.getElementById('darkModeToggle');
    darkModeToggle.checked = isDarkMode;
}

// Check if dark mode was enabled before (on page load)
document.addEventListener('DOMContentLoaded', () => {
    const savedDarkMode = localStorage.getItem('darkMode');

    // If dark mode was enabled before, apply it on page load
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
        document.getElementById('verdexNavbar').classList.add("bg-dark")
        document.getElementById('verdexNavbar').setAttribute("data-bs-theme", "dark")

        // Update the toggle button state
        const darkModeToggle = document.getElementById('darkModeToggle');
        darkModeToggle.checked = true;
    }
});

function reportUser(passedInID){
    document.getElementById('reason-for-reporting-user-popup').style.display = "block"
    authorAccID = passedInID
}

function submitReport(){
    const reportReason = document.getElementById('report-reason').value
    if (reportReason.trim() === "") {
        alert("Please enter a valid reason. Empty inputs are not accepted.");
        return;
    }
    axios({
        method: 'post',
        url: `/api/submitReport`,
        headers: {
            'Content-Type': 'application/json',
            'VerdexAPIKey': '\{{ API_KEY }}'
        },
        data: {
            "author_acc_id": authorAccID,
            "report_reason": reportReason
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while reporting user. Please try again.")
            return;
        }
        else if (response.data.startsWith("UERROR:")){
            console.log(response.data)
            alert(response.data.substring("UERROR: ".length))
            return;
        }
        console.log(response.data)
        alert("Report submitted. We will review it and ban the user if necessary.")
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error reporting user:', error);
    });
}

function closeReportPopup(){
    closeReportConfirmation = confirm("Are you sure you'd like to discard all changes?");
    if (closeReportConfirmation == true) {
        window.location.reload();
    }
}


function handleTypewriterEffect(resultDiv, generatedText, maxLength) {
    console.log(generatedText)
    const characters = generatedText.split('');
    let i = 0;

    const intervalId = setInterval(() => {
        resultDiv.innerHTML += characters[i];
        i++;

        if (i === characters.length || i === maxLength) {
            clearInterval(intervalId);
        }
    }, 10); 
}

function submitPrompt() {
    const prompt = document.getElementById("prompt");

    if (prompt.value !== "") {
        axios({
            method: 'post',
            url: `/api/verdexgpt`,
            headers: {
                'Content-Type': 'application/json',
                'VerdexAPIKey': '\{{ API_KEY }}'
            },
            data: {
                "prompt": prompt.value
            }
        })
        .then(function (response) {
            console.log("Payload successfully sent")

            console.log(response.data);

            const resultDiv = document.getElementById('response');
            
            resultDiv.innerHTML = '';

            const maxLength = 600;

            handleTypewriterEffect(resultDiv, response.data.generated_text, maxLength);
        })
        .catch(function (error) {
            console.error('Error generating text completion:', error);
        });
    } else {
        alert("Please enter a valid prompt.");
        return;
    }
}
