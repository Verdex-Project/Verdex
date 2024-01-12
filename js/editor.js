function allowDrop(event) {
    event.preventDefault();
}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id);
}

function drop(event) {
    event.preventDefault();
    var fetchData = event.dataTransfer.getData("text");
    event.target.appendChild(document.getElementById(fetchData));
}

function saveItinerary() {
    
}


// // Get the button element by its ID
// const myButton = document.getElementById('myButton');

// // Add a click event listener to the button
// myButton.addEventListener('click', function() {
//   alert('Button clicked!');
// });