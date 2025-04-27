//------------------------------------------------------------------------
// --------- for generate query page ------------------------------

// Function to copy the generated query to the clipboard
function copyToClipboard() {
    const queryTextElement = document.getElementById('generated-query');
    
    if (queryTextElement) {
        const queryText = queryTextElement.innerText.trim();
        
        if (queryText) {
            navigator.clipboard.writeText(queryText).then(() => {
                alert('Copied to clipboard!');
            }).catch(err => {
                alert('Failed to copy text: ' + err);
            });
        } else {
            alert('No query to copy!');
        }
    } else {
        alert('No query found!');
    }
}

// Function to perform a Google search with the generated query
function googleSearch() {
    const queryTextElement = document.getElementById('generated-query');

    if (queryTextElement) {
        const queryText = queryTextElement.innerText.trim();

        if (queryText) {
            const googleUrl = `https://www.google.com/search?q=${encodeURIComponent(queryText)}`;
            window.open(googleUrl, '_blank'); // Open in a new tab
        } else {
            alert('No query to search!');
        }
    } else {
        alert('No query found!');
    }
}

//------------------------------------------------------------------------
// --------- for generate query page ends here ------------------------------

// ----------------- for home page ---------------------------------
document.addEventListener("DOMContentLoaded", function () {
    const cardContainer = document.querySelector(".card-container");
    const cards = document.querySelectorAll(".card");

    // Duplicate cards to create an infinite loop effect
    cards.forEach((card) => {
        let clone = card.cloneNode(true);
        cardContainer.appendChild(clone);
    });

    // Start automatic scrolling
    let scrollSpeed = 2; // Speed of scrolling
    function scrollCards() {
        cardContainer.scrollLeft += scrollSpeed;
        if (cardContainer.scrollLeft >= cardContainer.scrollWidth / 2) {
            cardContainer.scrollLeft = 0; // Reset scroll when it reaches halfway
        }
        requestAnimationFrame(scrollCards);
    }

    scrollCards();
});

// --------------------------- home page ends hear-----------------------------

//---------------- contact page starts here ------------------------------

document.getElementById("contactForm").addEventListener("submit", function(event) {
    event.preventDefault();
    let name = document.getElementById("name").value.trim();
    let email = document.getElementById("email").value.trim();
    let message = document.getElementById("message").value.trim();
    let successMessage = document.getElementById("successMessage");
    let errorMessage = document.getElementById("errorMessage");

    if (name && email && message) {
        successMessage.style.display = "block";
        errorMessage.style.display = "none";
        setTimeout(() => successMessage.style.display = "none", 3000);
    } else {
        errorMessage.style.display = "block";
        successMessage.style.display = "none";
    }
});

// ------------------contact page ends here ---------------------------------

// ------------------ dashboard page -----------------------------------------

// Add event listeners to buttons
document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.btn-custom');
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            alert('This feature is under development. Coming soon!');
        });
    });
});


// Function to show alerts dynamically
function showAlert(message, category) {
    const alertContainer = document.getElementById('alert-container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertContainer.appendChild(alertDiv);

    // Automatically remove the alert after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Example usage (you can replace this with dynamic data from your backend)
showAlert('Welcome to the dashboard!', 'success');
showAlert('Your subscription is about to expire.', 'warning');
showAlert('Error loading data. Please try again.', 'danger');
//-------------------------------------------------------------------------



// Function to handle form submission for generating dork

document.querySelector("form").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent page reload

    let formData = new FormData(this);

    fetch("/generate_dork", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error); // Show error
        } else {
            // Update the page dynamically
            let queryDiv = document.getElementById("generated-query");
            queryDiv.innerText = data.query_text; // Show generated query
            queryDiv.style.display = "block"; // Ensure visibility
        }
    })
    .catch(error => console.error("Error:", error));
});




// ------------------ save query page -----------------------------------

document.addEventListener("DOMContentLoaded", function () {
    // Add event listener for the Save Query button
    const saveButton = document.querySelector(".btn[type='submit']");
    const generatedQueryElement = document.getElementById("generated-query");

    saveButton.addEventListener("click", function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Get the generated query text
        const queryText = generatedQueryElement ? generatedQueryElement.textContent.trim() : "";

        if (!queryText) {
            alert("No query to save!");
            return;
        }

        // Send an AJAX POST request to save the query
        fetch("/save_query", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `query=${encodeURIComponent(queryText)}`,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Query saved successfully!");
                } else if (data.error) {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An unexpected error occurred. Please try again.");
            });
    });
});











// ------------------ dashboard page ends here -------------------------------

// ------------------ generate dork page -----------------------------------

document.addEventListener("DOMContentLoaded", function () {
    const generateForm = document.querySelector("form[action='/generate_dork']");
    const resultContainer = document.getElementById("result-container");
    const generatedQueryElement = document.getElementById("generated-query");
    const errorContainer = document.getElementById("error-container");
    const errorMessageElement = document.getElementById("error-message");

    generateForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the default form submission

        const userInput = document.getElementById("user_input").value.trim();

        if (!userInput) {
            errorContainer.style.display = "block";
            errorMessageElement.innerText = "Please enter a query!";
            return;
        }

        // Send an AJAX POST request to generate the query
        fetch("/generate_dork", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `user_input=${encodeURIComponent(userInput)}`,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    // Display the generated query
                    resultContainer.style.display = "block";
                    generatedQueryElement.innerText = data.query_text;

                    // Hide the error container if it was displayed
                    errorContainer.style.display = "none";
                } else if (data.error) {
                    // Display the error message
                    errorContainer.style.display = "block";
                    errorMessageElement.innerText = data.error;
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                errorContainer.style.display = "block";
                errorMessageElement.innerText = "An unexpected error occurred. Please try again.";
            });
    });
});


// ------------------ generate dork page ends hear ---------------------------





// ------------------ chatbot page -----------------------------------


function toggleChatbot() {
    let chatbotBody = document.getElementById("chatbot-body");
    chatbotBody.style.display = chatbotBody.style.display === "none" ? "block" : "none";
}

function sendChatbotMessage() {
    let userMessage = document.getElementById("chatbot-input").value;
    if (!userMessage) return;

    // Display user message
    let messageContainer = document.getElementById("chatbot-messages");
    messageContainer.innerHTML += `<div class="user-message">You: ${userMessage}</div>`;

    // Send request to Flask API
    fetch("/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        messageContainer.innerHTML += `<div class="bot-message">Bot: ${data.response}</div>`;
        document.getElementById("chatbot-input").value = "";
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendChatbotMessage();
    }
}


document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_chat_history")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chatContainer = document.getElementById("chat-container");
                chatContainer.innerHTML = ""; // Clear existing chat

                data.chat_history.forEach(chat => {
                    const userMessage = document.createElement("div");
                    userMessage.className = "user-message";
                    userMessage.textContent = chat.query;

                    const botMessage = document.createElement("div");
                    botMessage.className = "bot-message";
                    botMessage.textContent = chat.response;

                    chatContainer.appendChild(userMessage);
                    chatContainer.appendChild(botMessage);
                });
            } else {
                console.error("Failed to fetch chat history:", data.error);
            }
        })
        .catch(error => console.error("Error fetching chat history:", error));
});

fetch("/clear_chat_history", { method: "POST" })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(data.message);
        } else {
            console.error("Failed to clear chat history:", data.error);
        }
    })
    .catch(error => console.error("Error clearing chat history:", error));


// ------------------ chatbot page ends here ---------------------------






//------------------ notification function ----------------------------
// ---------------------------save query----------------


function showNotification(message, type = "success") {
    const notification = document.createElement("div");
    notification.className = `alert alert-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

//------------------save_query----------------------------




