 $(document).ready(function() {
        $.ajax({
            url: "{% url 'add_elements_to_order' %}",
            type: "POST",
            data: {
                order_number: "{{ order.number }}",
                csrfmiddlewaretoken: "{{ csrf_token }}"
            },
            success: function(response) {
                console.log("Order updated successfully");
            },
            error: function(response) {
                console.log("Failed to update order");
            }
        });
    });