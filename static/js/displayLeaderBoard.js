$(document).ready(function() {
    $("input[type = 'radio']").on('click', function() {
        $.ajax({
            url : '/Leaderboard_process',
            data : {
                route : $("#{{route['ROUTE_ID']}}").val()
            },
            type : 'POST',
        })
        .done(function(data) {
            // Create HTML table
            var table = document.createElement("TABLE");
            table.border = "1";
            // Get the count of columns
            var columnCount  = 3;
            // Add the header row
            var row = table.insertRow(-1);
            var headerCell = document.createElement("TH");
            var headerCell1 = document.createElement("TH");
            var headerCell2 = document.createElement("TH");

            headerCell.innerHTML = "Position";
            row.appendChild(headerCell);

            headerCell1.innerHTML = "Team Name";
            row.appendChild(headerCell1);

            headerCell2.innerHTML = "Score";
            row.appendChild(headerCell2);

            function getTeamName(item) {
                var name = item.TEAM_NAME;
                return name;
            }
            function getValue(item) {
                var value = item.VALUE;
                return value;
            }
            // Add the data rows
            // Number of rows
            for (var i = 1; i < data.length; i++) {
                row = table.insertRow(-1);
                // Number of columns
                for (var j = 0; j < columnCount; j++) {
                    if(j == 0) {
                        var cell = row.insertCell(-1);
                        cell.innerHTML = i;
                    } else if (j > 0) {
                        var cell = row.insertCell(-1);
                        cell.innerHTML = Object.values(data[i])[j-1];
                    }
                }
            }
            var dvTable = document.getElementById("groups_list_container");
            dvTable.innerHTML = "";
            dvTable.appendChild(table);
        });
    });
});
