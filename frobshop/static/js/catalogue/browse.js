 let amenities = [
        { id: "swimming_pool", name: "SWIMMING_POOL", icon: "fas fa-swimming-pool" },
        { id: "spa", name: "SPA", icon: "fas fa-spa" },
        { id: "fitness_center", name: "FITNESS_CENTER", icon: "fas fa-dumbbell" },
        { id: "air_conditioning", name: "AIR_CONDITIONING", icon: "fas fa-fan" },
        { id: "restaurant", name: "RESTAURANT", icon: "fas fa-utensils" },
        { id: "parking", name: "PARKING", icon: "fas fa-parking" },
        { id: "pets_allowed", name: "PETS_ALLOWED", icon: "fas fa-dog" },
        { id: "airport_shuttle", name: "AIRPORT_SHUTTLE", icon: "fas fa-shuttle-van" },
        { id: "business_center", name: "BUSINESS_CENTER", icon: "fas fa-briefcase" },
        { id: "disabled_facilities", name: "DISABLED_FACILITIES", icon: "fas fa-wheelchair" },
        { id: "wifi", name: "WIFI", icon: "fas fa-wifi" },
        { id: "meeting_rooms", name: "MEETING_ROOMS", icon: "fas fa-users" },
        { id: "no_kid_allowed", name: "NO_KID_ALLOWED", icon: "fas fa-child" },
        { id: "tennis", name: "TENNIS", icon: "fas fa-baseball-ball" },
        { id: "golf", name: "GOLF", icon: "fas fa-golf-ball" },
        { id: "kitchen", name: "KITCHEN", icon: "fas fa-sink" },
        { id: "animal_watching", name: "ANIMAL_WATCHING", icon: "fas fa-binoculars" },
        { id: "baby-sitting", name: "BABY-SITTING", icon: "fas fa-baby-carriage" },
        { id: "beach", name: "BEACH", icon: "fas fa-umbrella-beach" },
        { id: "casino", name: "CASINO", icon: "fas fa-dice" },
        { id: "jacuzzi", name: "JACUZZI", icon: "fas fa-hot-tub" },
        { id: "sauna", name: "SAUNA", icon: "fas fa-hot-tub" },
        { id: "solarium", name: "SOLARIUM", icon: "fas fa-sun" },
        { id: "massage", name: "MASSAGE", icon: "fas fa-spa" },
        { id: "valet_parking", name: "VALET_PARKING", icon: "fas fa-parking" },
        { id: "bar_or_lounge", name: "BAR_or_LOUNGE", icon: "fas fa-beer" },
        { id: "kids_welcome", name: "KIDS_WELCOME", icon: "fas fa-child" },
        { id: "no_porn_films", name: "NO_PORN_FILMS", icon: "fas fa-film" },
        { id: "minibar", name: "MINIBAR", icon: "fas fa-wine-glass" },
        { id: "television", name: "TELEVISION", icon: "fas fa-tv" },
        { id: "wi-fi_in_room", name: "WI-FI_IN_ROOM", icon: "fas fa-wifi" },
        { id: "room_service", name: "ROOM_SERVICE", icon: "fas fa-concierge-bell" },
        { id: "guarded_parkg", name: "GUARDED_PARKG", icon: "fas fa-shield-alt" },
        { id: "serv_spec_menu", name: "SERV_SPEC_MENU", icon: "fas fa-clipboard-list" }
    ];

    let amenitiesHTML = amenities.map(amenity => {
        let id_with_spaces = amenity.id.replace(/_/g, ' ');
        return `
            <div class="form-check">
                <input class="form-check-input amenities-checkbox" type="checkbox" id="${amenity.id}" value="${amenity.name}">
                <label class="form-check-label" for="${amenity.id}"><i class="${amenity.icon}"></i> ${id_with_spaces}</label>
            </div>
        `;
    }).join("");

    document.querySelector(".amenities").innerHTML += amenitiesHTML;


function findCommonAmenities(selectedAmenities, amenities) {

                return selectedAmenities.filter(item => amenities.includes(item));
            }
          function filters() {
            returnData();
            // Get all product elements
            let selectedRatings = Array.from(document.getElementsByClassName('rating-checkbox'))
                .filter(checkbox => checkbox.checked)
                .map(checkbox => checkbox.value);
            let selectedAmenities = Array.from(document.getElementsByClassName('amenities-checkbox'))
                .filter(checkbox => checkbox.checked)
                .map(checkbox => checkbox.value);
            let selectedDistance = Array.from(document.getElementsByClassName('distance-checkbox'))
                .filter(checkbox => checkbox.checked)
                .map(checkbox => checkbox.value);
            // Get all product elements
            const productElements = document.querySelectorAll('.product_pod');

            // Iterate over product elements
            productElements.forEach((productElement) => {
                // Get product rating from data attribute
                let rating = productElement.getAttribute('data-rating');
                let description = JSON.parse(productElement.getAttribute('product-description'));
                let amenities = description.amenities.split(', ').map(amenity => amenity.trim().toUpperCase());
                let distance = description.distance;
                let distanceNumber = parseFloat(distance.substring(0, distance.indexOf('K')).trim());
                let isDistanceNumberBigger = selectedDistance.every(selectedDis => distanceNumber > selectedDis);
                if (!selectedRatings.includes(rating) && !selectedRatings.length == 0) {
                    productElement.parentElement.style.display = 'none'; // Hide the product
                }
                if(findCommonAmenities(selectedAmenities,amenities).length < selectedAmenities.length && !selectedAmenities.length == 0 ) {
                    productElement.parentElement.style.display = 'none'; // Hide the product
                }

                if (isDistanceNumberBigger && !selectedDistance.length == 0) {
                    productElement.parentElement.style.display = 'none'; // Hide the product
                }
            });
        }
        function resetFilters() {
        returnData();
        // Uncheck all rating checkboxes
        let ratingCheckboxes = document.getElementsByClassName('rating-checkbox');
        let amenities = document.getElementsByClassName('amenities-checkbox');
        let distance = document.getElementsByClassName('distance-checkbox');

        for(let checkbox of ratingCheckboxes) {
            checkbox.checked = false;
        }
        for(let checkbox of amenities) {
            checkbox.checked = false;
        }
        for(let checkbox of distance) {
            checkbox.checked = false;
        }
    }
    function returnData() {
            // Get all product elements
        const productElements = document.querySelectorAll('.product_pod');

        // Iterate over product elements
        productElements.forEach((productElement) => {
            // Show all products
            productElement.parentElement.style.display = 'block';
        });
    }