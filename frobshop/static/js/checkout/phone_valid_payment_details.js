 let phoneInputField = document.querySelector("#phone");
            const phoneInput = window.intlTelInput(phoneInputField, {
                utilsScript:
                    "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
                    // allowDropdown: false,
                        // autoHideDialCode: false,
                        // autoPlaceholder: "off",
                        // dropdownContainer: document.body,
                        // excludeCountries: ["us"],
                        // formatOnDisplay: false,
                        // geoIpLookup: function(callback) {
                        //   $.get("http://ipinfo.io", function() {}, "jsonp").always(function(resp) {
                        //     var countryCode = (resp && resp.country) ? resp.country : "";
                        //     callback(countryCode);
                        //   });
                        // },
                        // hiddenInput: "full_number",
                        initialCountry: "auto",
                        // localizedCountries: { 'de': 'Deutschland' },
                        // nationalMode: false,
                        //onlyCountries: ['us', 'gb', 'ch', 'ca', 'do'],
                        // placeholderNumberType: "MOBILE",
                        preferredCountries: ['il','us', 'gb', 'ch', 'ca', 'do'],
                        separateDialCode: true,
            });

            document.querySelector('form').addEventListener('submit', function(e) {
                if(!phoneInput.isValidNumber()) {
                    alert('Invalid Phone Number');
                    e.preventDefault();
                }
            });
