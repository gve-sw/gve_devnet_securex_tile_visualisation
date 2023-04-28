$(document).ready(function () {
    // Get all 'select-all' checkboxes
    const selectAllCheckboxes = document.querySelectorAll('.select-all');

    // Add event listeners to each 'select-all' checkbox
    selectAllCheckboxes.forEach(function (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const tilesWrapper = selectAllCheckbox.parentElement;
            const tileCheckboxes = tilesWrapper.querySelectorAll('input[name="tiles"]');

            tileCheckboxes.forEach(function (tileCheckbox) {
                tileCheckbox.checked = selectAllCheckbox.checked;
            });
        });
    });
});

$(function() {
    /* Show corresponding tile list as soon as the module is chosen in the dropdown */
    $('#module_select').on('change', function() {
        var selectedModule = $("#module_select option:selected").val();
        updateTileCheckboxes(selectedModule);
    });

    function updateTileCheckboxes(selectedModule) {
        // Reset the tile checkboxes
        $(".tile-checkboxes").empty();

        // Populate the tile checkboxes with the appropriate options
        if (selectedModule) {
            var moduleData = window.dropdownContent.find(module => module.modulename === selectedModule);
            if (moduleData) {
                moduleData.tiles.forEach(tile => {
                    const checkboxId = 'tile-' + tile['tile'];
                    const checkboxElement = document.createElement('input');
                    checkboxElement.type = 'checkbox';
                    checkboxElement.name = 'tiles';
                    checkboxElement.value = tile['tile'];
                    checkboxElement.id = checkboxId;

                    const labelElement = document.createElement('label');
                    labelElement.htmlFor = checkboxId;
                    labelElement.textContent = tile['tile'];

                    $(".tile-checkboxes").append(checkboxElement);
                    $(".tile-checkboxes").append(labelElement);
                    $(".tile-checkboxes").append(document.createElement('br')); // Add a line break for better formatting
                });
            }
        }
    }

    // Initialize the tile checkboxes based on the selected module on page load
    var initialSelectedModule = $("#module_select option:selected").val();
    if (initialSelectedModule) {
        updateTileCheckboxes(initialSelectedModule);
    }
});
