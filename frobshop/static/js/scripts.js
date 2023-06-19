function searchLocation(query) {
    if(query.length >= 3) {
        $.ajax({
            url: 'http://localhost:5000/search',
            type: 'GET',
            data: {
                query: query
            },
            success: function(data) {
                $('#results').empty(); // clear previous results
                if (data.features.length > 0) {
                    data.features.forEach(function(item) {
                        $('#results').append('<li onclick="selectLocation(this)">' + item.properties.label + '</li>');
                    });
                    $('#results').show(); // show the results
                } else {
                    $('#results').hide(); // hide the results
                }
            }
        });
    } else {
        $('#results').hide(); // hide the results
    }
}

function selectLocation(li) {
    $('#location').val(li.textContent); // set the input to the selected result
    $('#results').hide(); // hide the results
}
