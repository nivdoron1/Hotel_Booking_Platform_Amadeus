 $(document).ready(function(){
        let isLocationSelected = false;

        $("#location").on("input", function(){
            let searchQuery = $(this).val();

            // If search bar is empty, set isLocationSelected back to false
            if(searchQuery.length === 0){
                isLocationSelected = false;
            }

            if(searchQuery.length > 2 && !isLocationSelected) {
                $.ajax({
                    url: "/search",
                    method: "GET",
                    data: {
                        'query': searchQuery
                    },
                    success: function(data){
                        // Clear the list
                        $("#results").empty();

                        // Append new results
                        for(let feature of data.features){
                            $("#results").append(`<li><button class="location-button">${feature.properties.formatted}</button></li>`);
                        }
                    }
                });
            }
        });

        // When a location button is clicked
        $("body").on("click", ".location-button", function() {
            // Get the location text
            var locationText = $(this).text();

            // Put the location text in the search bar
            $("#location").val(locationText);

            // Clear the results
            $("#results").empty();

            // Stop new searches
            isLocationSelected = true;
        });
    });


    let today = new Date().toISOString().split('T')[0];
        let tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        let tomorrowDate = tomorrow.toISOString().split('T')[0];
        document.getElementById('checkInDate').setAttribute('min', today);
        document.getElementById('checkOutDate').setAttribute('min', tomorrowDate);
        document.getElementById('checkInDate').addEventListener('change', function() {
            let checkInDate = new Date(this.value);
            checkInDate.setDate(checkInDate.getDate() + 1);
            let minCheckOutDate = checkInDate.toISOString().split('T')[0];
            document.getElementById('checkOutDate').setAttribute('min', minCheckOutDate);
        });