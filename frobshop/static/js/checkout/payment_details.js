 let form = document.querySelector('form');
                    let continueButton = document.getElementById('view_preview');

                    form.addEventListener('input', function() {
                        let fields = form.querySelectorAll('input[required]');
                        let allFilled = Array.from(fields).every(function(field) {
                            return field.value !== '';
                        });

                        continueButton.disabled = !allFilled;
                    });
let expiryDateInput = document.getElementById('expiry_date');

            expiryDateInput.min = new Date().toISOString().substring(0,7);

            expiryDateInput.addEventListener('input', function() {
                let chosenDate = new Date(this.value + '-01');
                let now = new Date();

                if (chosenDate < now) {
                    this.setCustomValidity('Expiry date cannot be in the past');
                } else {
                    this.setCustomValidity('');
                }
            });
function luhnCheck(val) {
            let sum = 0;
            for (let i = 0; i < val.length; i++) {
                let intVal = parseInt(val.substr(i, 1));
                if (i % 2 == 0) {
                    intVal *= 2;
                    if (intVal > 9) {
                        intVal = 1 + (intVal % 10);
                    }
                }
                sum += intVal;
            }
            return (sum % 10) == 0;
        }

document.querySelector('form').addEventListener('submit', function(e){
            let cardNumber = document.querySelector('.card-number').value;
            if(!luhnCheck(cardNumber)){
                alert('Invalid Card Number');
                e.preventDefault();
            }
        });

function updateProductName() {
            // Select the paragraph element by id
            let productTitleElement = document.getElementById("product_name");

            // Get the text content of the paragraph
            let productTitle = productTitleElement.textContent;

            // Find the index of the first comma in the string
            let commaIndex = productTitle.indexOf(',');

            // If there is a comma in the string
            if(commaIndex !== -1) {
                // Take all elements before the first comma
                let productName = productTitle.slice(commaIndex+1);

                // Update the text content of the paragraph
                productTitleElement.textContent = productName;
            }
        }

// Call the function
updateProductName();
    let productTitleElement = document.querySelector('#product_title');
    let titleParts = productTitleElement.innerText.split(",");  // Split the title into an array of parts
    let title = titleParts.slice(1).join(",");  // Join all parts starting from the second one
    if (title) {
        title = title.replace(/_/g, ' ');
        productTitleElement.innerText = title;  // Set the second part as the link text
    }