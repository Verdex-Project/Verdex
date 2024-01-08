// function addDay() {
//     var isConfirmedAdd = confirm(`Are you sure you want to add a day?`);
//     if (isConfirmedAdd) {
//         $.ajax({ 
//             url: '/editor', 
//             type: 'POST', 
//             data2: { 'data2':true, 'addDay': ''}
//         })
//         alert(`Day added successfully`);     
//     }
// }

function deleteDay(day) {
    var deleteDay = day;
    var isConfirmedDelete = confirm(`Are you sure you want to delete day ${deleteDay}`);
    if (isConfirmedDelete){
        $.ajax({ 
            url: '/editor', 
            type: 'POST', 
            data: { 'data':true,'deleteDay': deleteDay}
        })
        alert(`Day ${day} delete successfully!`);
        return isConfirmedDelete
    };
}

function toggleAddActivity(day) {
    var newActivityForm = document.getElementById('newActivityForm_' + day);
    newActivityForm.style.display = (newActivityForm.style.display === 'none') ? 'block' : 'none';
}

function showEditForm(day, activity_number) {
    document.getElementById("editForm_" + day + "_" + activity_number).style.display = "block";
    document.getElementById("editButton_" + day + "_" + activity_number).style.display = "hidden";
}

// function confirmEdit(day, activity_number) {

//     var confirmChanges = confirm("Valid changes will be saved. Confirm?");
//     if (confirmChanges == true) {
//         // Reset the form and hide the edit box
//         document.getElementById("editForm_" + day + "_" + activity_number).reset();
//         document.getElementById("editForm_" + day + "_" + activity_number).style.display = "none";
//         document.getElementById("editButton_" + day + "_" + activity_number).style.display = "block";
//         alert("Valid changes saved.");
//         return false;
//     }
//     return true
// }


function deleteItinerary() {
    var isConfirmedDeleteItinerary = confirm(`Are you sure you want to delete your itinerary?`);
    if (isConfirmedDeleteItinerary) {
        $.ajax({ 
            url: '/editor', 
            type: 'POST', 
            data: { 'confirmDeleteItinerary': true},
        })
        alert(`Your Itinerary delete successfully!`);
        location.href('/')
    };
}
