var commentedPostId = null
var editPostId = null

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
    const user_names = document.getElementById("user_names");
    const post_title = document.getElementById("post-title");
    const post_description = document.getElementById("post-description");
    const post_tag = document.getElementById("post-tag");

    if (user_names.value.trim() === ""){
        alert("Please enter valid name(s)")
        return;
    }
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
            "user_names": user_names.value,
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
            const likeButton = document.querySelector(`[data-post-id='${postId}'] .reaction-buttons`);
            if (!response.data.startsWith("ERROR:")){
                likeButton.innerHTML = `Likes (${response.data.likes})`;
            }
            else if (response.data.startsWith("ERROR:")){
                alert("An error occured while liking post. Please try again.")
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
        console.log(response.data)
        window.location.reload();
    })
    .catch(function (error) {
        console.error('Error commenting on post:', error);
    });
}

function editPost(postId) {
    document.getElementById("edit-post-popup").style.display = "block";
    editPostId = postId;
}

let editedSelectedTag = ""
function submitEdit() {
    document.getElementById("edit-post-tag").value = editedSelectedTag;
    const editUserNames = document.getElementById("edit_user_names").value;
    const editPostTitle = document.getElementById("edit-post-title").value;
    const editPostDescription = document.getElementById("edit-post-description").value;
    const editPostTag = document.getElementById("edit-post-tag").value;
    const postId = editPostId;

    if (editUserNames.trim() === "") {
        alert("Please enter valid name(s).");
        return;
    }
    else if (editPostTitle.trim() === "") {
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
            "edit_user_names": editUserNames,
            "edit_post_title": editPostTitle,
            "edit_post_description": editPostDescription,
            "edit_post_tag": editPostTag
        }
    })
    .then(function (response) {
        if (response.data.startsWith("ERROR:")){
            console.log(response.data)
            alert("An error occured while submitting edits. Please try again.")
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
            console.log(response.data);
            window.location.reload();
        })
        .catch(error => {
            console.error(error);
        });
    }
}