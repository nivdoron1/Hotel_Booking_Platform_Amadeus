async function handleFormSubmit(event) {
            event.preventDefault();

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                let response = await fetch('{% url "complete_purchase" %}', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({})
                });

                let data = await response.json();

                if (data.status === 'success') {
                    // If the complete_purchase function is successful, submit the form normally
                    event.target.submit();
                } else {
                    console.error('Error:', data);
                    // Display an error message to the user
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }