// Function to show notification alerts for future updates
document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.btn-custom');
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            alert('This feature is under development. Coming soon!');
        });
    });
});

// Function for deleting queries
document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.delete-query-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const queryId = this.getAttribute('data-query-id');
            const queryElement = document.getElementById(`query-${queryId}`);

            // Show a confirmation dialog
            const confirmDelete = confirm("Are you sure you want to delete this query?");
            if (confirmDelete && queryElement) {
                // Send the query ID to the backend to mark it as deleted
                fetch('/delete_query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query_id: queryId }),
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Remove the query element from the DOM
                            queryElement.remove();
                        } else {
                            alert(`Error: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting query:', error);
                    });
            }
        });
    });
});



// <!-- JavaScript for Dynamic Copyright Year -->

document.getElementById("current-year").textContent = new Date().getFullYear();
