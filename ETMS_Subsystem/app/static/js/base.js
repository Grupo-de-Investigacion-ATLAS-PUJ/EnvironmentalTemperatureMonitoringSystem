function changeContent(buttonId) {
    // Change the page title in the top bar
    const pageTitle = document.getElementById('page-title');
    pageTitle.innerText = capitalizeFirstLetter(buttonId);

    // Update the active button style
    const activeButton = document.querySelector('.menu-item.active');
    if (activeButton) {
        activeButton.classList.remove('active'); // Remove active class from previous button
    }

    const newActiveButton = document.getElementById(buttonId);
    newActiveButton.classList.add('active'); // Add active class to the new button
}

// Capitalize the first letter of a string
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

setTimeout(() => {
    const flashMessages = document.querySelector('.flash-messages');
    if (flashMessages) {
        flashMessages.remove();
    }
}, 5000); // Remove flash messages after 5 seconds
