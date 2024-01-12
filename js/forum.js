function createPostPopup() {
    document.getElementById("create-a-post-popup").style.display = "block";
}

function itineraryShortcutButtonPopup(shortcut) {
    document.getElementById("create-a-post-popup").style.display = "block";
    document.getElementById("post-title").innerHTML = shortcut
}

function closeCreatePopup() {
    confirmation = confirm("Are you sure you'd like to discard all changes?");
    if (confirmation == true) {
        document.getElementById("create-a-post-popup").style.display = "none";
        document.getElementById("comment-on-post-popup").style.display = "none";
        document.getElementById("create-post-form").reset();
        document.getElementById("comment-post-form").reset();
        alert("Changes discarded.");
        return false;
    }
    return false;
}

// function closeEditPopup() {
//     confirmation = confirm("Are you sure you'd like to discard all changes?");
//     if (confirmation == true) {
//         document.getElementById("edit-post-popup").style.display = "none";
//         document.getElementById("edit-post-form").reset();
//         alert("Changes discarded.");
//         return false;
//     }
//     return false;
// }

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
        // Use Axios to send a POST request to the server
        axios.post('/api/deletePost', { postId: postId }, { headers: { 'Content-Type': 'application/json' } })
            .then(function (response) {
                window.location.reload();
            })
            .catch(function (error) {
                console.error('Error deleting post:', error);
            });
    }
}

// function commentPost(){
//     document.getElementById("comment-on-post-popup").style.display = "block";
// }

// function submitComment(postId) {
//     event.preventDefault();  // Prevent the default form submission behavior

//     const commentDescription = document.getElementById("comment_description").value;

//     // Create an object with form data
//     const formData = {
//         postId: postId,
//         comment_description: commentDescription,
//     };

//     // Use Axios to send a POST request to the server with application/json content type
//     axios.post('/comment-post', formData, {
//         headers: {
//             'Content-Type': 'application/json',
//         },
//     })
//     .then(function (response) {
//         // Handle the response if needed
//     })
//     .catch(function (error) {
//         console.error('Error commenting on post:', error);
//     });

//     document.getElementById("comment-on-post-popup").style.display = "none";
// }

// function editPost(postId) {
//     document.getElementById('edit-post-id').value = postId;
//     document.getElementById("edit-post-popup").style.display = "block";
// }

// function submitEdit() {
//     var editPostForm = document.getElementById("edit-post-form");
//     if (editPostForm.checkValidity()) {
//         alert("Post edited!");
//         document.getElementById("edit-post-popup").style.display = "none";
//     } else {
//         editPostForm.reportValidity();
//         return false;
//     }
// }

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