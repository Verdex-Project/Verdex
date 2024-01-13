function createPostPopup() {
    document.getElementById("create-a-post-popup").style.display = "block";
}

function itineraryShortcutButtonPopup(shortcut) {
    document.getElementById("create-a-post-popup").style.display = "block";
    document.getElementById("post-title").innerHTML = shortcut
}

function closeCreatePopup() {
    closeCreateConfirmation = confirm("Are you sure you'd like to discard all changes?");
    if (closeCreateConfirmation == true) {
        window.location.reload();
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
        document.getElementById("edit-post-popup").style.display = "none";
        document.getElementById("edit-post-form").reset();
        editedSelectedTag = ""
        alert("Changes discarded.");
        return false;
    }
    return false;
}

let selectedTag = ""
function submitPost() {
    document.getElementById("post-tag").value = selectedTag;
    var createPostForm = document.getElementById("create-post-form");

    if (createPostForm.checkValidity()) {
        alert("Post submitted!");
        document.getElementById("create-a-post-popup").style.display = "none";
    } else {
        createPostForm.reportValidity();
        return false;
    }
}

function likePost(postId) {
    // Use Axios to send a POST request to the server
    axios.post('/api/likePost', { postId: postId }, { headers: { 'Content-Type': 'application/json' } })
        .then(function (response) {
            // Update the like count on the client side
            const likeButton = document.querySelector(`[data-post-id='${postId}'] .reaction-buttons`);
            likeButton.innerHTML = `Likes (${response.data.likes})`;
        })
        .catch(function (error) {
            console.error('Error liking post:', error);
        });
}

function deletePost(postId){
    confirmation = confirm("Are you sure you want to delete this post?")
    if (confirmation){
        axios.post('/api/deletePost', {
            postId: postId,
        })
        .then(response => {
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
    window.commentedPostId = postId;
}

function submitComment() {
    const commentDescription = document.getElementById("comment_description").value;
    const postId = window.commentedPostId;

    if (commentDescription.trim() === "") {
        alert("Please enter a valid comment.");
        return;
    }

    axios.post('/comment_post', {
        postId: postId,
        comment_description: commentDescription
    })
    .then(response => {
        console.log(response.data);
        alert("Comment added");
        document.getElementById("comment-on-post-popup").style.display = "none";
        window.location.reload();
    })
    .catch(error => {
        console.error(error);
    });
}

function editPost(postId) {
    document.getElementById("edit-post-popup").style.display = "block";
    window.editPostId = postId;
}

let editedSelectedTag = ""
function submitEdit() {
    document.getElementById("edit-post-tag").value = editedSelectedTag;
    const editUserNames = document.getElementById("edit_user_names").value;
    const editPostTitle = document.getElementById("edit-post-title").value;
    const editPostDescription = document.getElementById("edit-post-description").value;
    const editPostTag = document.getElementById("edit-post-tag").value;
    const postId = window.editPostId;

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

    axios.post('/edit_post', {
        postId: postId,
        edit_user_names: editUserNames,
        edit_post_title: editPostTitle,
        edit_post_description: editPostDescription,
        edit_post_tag: editPostTag
    })
    .then(response => {
        console.log(response.data);
        alert("Post edited");
        document.getElementById("edit-post-popup").style.display = "none";
        window.location.reload();
    })
    .catch(error => {
        console.error(error);
    });
}

function selectTag(tag, event, buttonToEnable, firstButtonToDisable, secondButtonToDisable){
    selectedTag = tag
    document.getElementById(buttonToEnable).style.backgroundColor = "#66BB69";
    document.getElementById(buttonToEnable).style.color = "white";

    document.getElementById(firstButtonToDisable).style.backgroundColor = "white";
    document.getElementById(firstButtonToDisable).style.color = "black";

    document.getElementById(secondButtonToDisable).style.backgroundColor = "white";
    document.getElementById(secondButtonToDisable).style.color = "black";

    event.preventDefault();
    event.stopPropagation();
}

function editSelectTag(tag, event, buttonToEnable, firstButtonToDisable, secondButtonToDisable){
    console.log("function call success")
    editedSelectedTag = tag
    document.getElementById(buttonToEnable).style.backgroundColor = "#66BB69";
    document.getElementById(buttonToEnable).style.color = "white";

    document.getElementById(firstButtonToDisable).style.backgroundColor = "white";
    document.getElementById(firstButtonToDisable).style.color = "black";

    document.getElementById(secondButtonToDisable).style.backgroundColor = "white";
    document.getElementById(secondButtonToDisable).style.color = "black";

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
        // Use Axios to send a POST request to the server
        axios.post('/api/deleteComment', {
            postId: postId,
            commentId: commentId
        })
        .then(response => {
            console.log(response.data);
            window.location.reload();
        })
        .catch(error => {
            console.error(error);
        });
    }
}