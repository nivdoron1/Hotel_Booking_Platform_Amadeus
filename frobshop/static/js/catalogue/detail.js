// Wrap the code inside DOMContentLoaded event
    document.addEventListener('DOMContentLoaded', (event) => {
        // Parse the JSON description
        let description = JSON.parse('{{ product.description|escapejs }}');
        let title_of_child_product = ''; // Define the variable

        function formatKeyOrValue(str) {
            return str.toLowerCase().replace(/_/g, ' ');
        }

        function traverseObject(obj, result = '') {
            for (let key in obj) {
                let formattedKey = formatKeyOrValue(key);
                let formattedValue;

                if (typeof obj[key] === 'object' && obj[key] !== null) {
                    // Convert object or array into a JSON string, remove the opening and closing braces or brackets,
                    // replace any inner double quotes with single quotes, and replace underscores with spaces
                    formattedValue = JSON.stringify(obj[key], null, 2)
                        .slice(1, -1)
                        .replace(/"/g, "'")
                        .replace(/_/g, ' ');
                } else {
                    formattedValue = typeof obj[key] === 'string' ? formatKeyOrValue(obj[key]) : obj[key];
                }

                result += formattedKey + ': ' + formattedValue + '<br>';

                // Check if key is 'room description' or 'room type category'
                if (formattedKey === 'room description' || formattedKey === 'room type category') {
                    title_of_child_product += formattedValue + ' ';
                }
            }
            return result;
        }

        // Generate the formatted description
        let formatted_description = traverseObject(description);
        document.querySelector('h1').textContent = title_of_child_product;

        // Insert the formatted description into the HTML
        document.getElementById('formatted_description').innerHTML = formatted_description;
    });



    window.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('#child-product-title').forEach((el) => {
       let titleParts = el.dataset.title.split(",");  // Split the title into an array of parts
       let title = titleParts.slice(1).join(",");  // Join all parts starting from the second one
       if (title) {
            title=title.replace(/_/g, ' ')
            el.innerText = title;  // Set the second part as the link text
       }
    });
});

    $(document).ready(function() {
      $('.btn-primary').click(function(e) {
        e.preventDefault();

        let selectedRatings = [];
        $('input[type=checkbox]:checked').each(function() {
          selectedRatings.push($(this).attr('id'));
        });

        $.ajax({
          url: '/filter_products/',  // Update with your endpoint
          type: 'get',
          data: {
            'ratings': selectedRatings
          },
          success: function(response) {
            // Update your product list with the returned data
          }
        });
      });
    });