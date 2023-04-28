$(document).ready(function () {
    $("#add-item-button").click(function () {
        var add_period = $("#period_select").val();
        if (add_period === null) {
            alert("Please select a period before adding the item.");
            return;
        }

        $(".tile-item input[type='checkbox']:checked").each(function () {
            var add_tile_id = $(this).val();
            var add_tile_name = $(this).data('tile-name');
            var add_module = $(this).data('module-name');
            var add_client = $(this).data('client-name');

            $("#item-table tbody").append(
                '<tr>' +
                '<td>' + add_client + '</td>' +
                '<td>' + add_module + '</td>' +
                '<td>' + add_tile_name + '</td>' +
                '<td>' + add_period + '</td>' +
                '</tr>'
            );
        });

        $("#period_select").val("0");
        $(".tile-item input[type='checkbox']").prop('checked', false);
    });
    $("#selected-items-form").submit(function (event) {
        event.preventDefault();
    
        // Prepare the data to be sent to the server
        var selectionTitle = $("#selection_name").val();
        var items = [];
    
        $("#item-table tbody tr").each(function () {
            var client = $(this).find("td:nth-child(1)").text().trim();
            var module = $(this).find("td:nth-child(2)").text()
            var tile = $(this).find("td:nth-child(3)").text();
            var period = $(this).find("td:nth-child(4)").text();
            items.push({
                client: client,
                module: module,
                tile: tile,
                period: period
            });
        });
    
        // Update the value of the hidden input field "json_data" with the correct JSON data
        var jsonData = JSON.stringify({ title: selectionTitle, items: items });
        $("#json-data").val(jsonData);
        // Debugging: Display JSON data in an alert before submitting the form
        alert("Generated JSON data: " + jsonData);
        // Submit the form
        this.submit();
    });
});
