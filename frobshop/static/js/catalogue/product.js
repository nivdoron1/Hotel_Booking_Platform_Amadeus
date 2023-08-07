window.addEventListener('DOMContentLoaded', (event) => {
                document.querySelectorAll('#product_title').forEach((el) => {
                   let titleParts = el.dataset.title.split(",");  // Split the title into an array of parts
                   let title = titleParts.slice(1).join(",");  // Join all parts starting from the second one
                   if (title) {
                        title=title.replace(/_/g, ' ')
                        el.innerText = title;  // Set the second part as the link text
                   }
                });
            });