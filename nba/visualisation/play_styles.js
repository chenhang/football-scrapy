var PLAY_STYLES_DATA_PATH = 'play_styles.csv',
    HEADERS = ["Post-Up", "Putbacks", "Cut", "P&R Roll Man", "Spot-Up", "Handoff", "Offscreen", "Transition", "Miscellaneous", "Isolation", "P&R Ball Handler", "Restricted Area", "Paint Area", "Mid Range", "3P"]
var TABLE_HEADERS = ['Name'],
    radarColors = d3.scale.category10().range(),
    maxValue = 0.9,
    playerData, displayedData, radarData,
    selectedPlayers = [];

d3.text(PLAY_STYLES_DATA_PATH, function (error, text) {
		playerData = d3.csv.parseRows(text);
		radarData = parsePlayerRadarData(playerData);
		displayedData = playerData;
		drawComparedPlayer();
		drawTable();
});

function searchBy(event) {
    if (event.keyCode == 13) {
        var playerName = document.getElementById("playerSearch").value.toLowerCase();
        var table = document.getElementsByClassName("playerTable")[0];
        var tr = table.getElementsByClassName("player-row");
        // Loop through all table rows, and hide those who don't match the search query
        for (var i = 0; i < tr.length; i++) {
            var td = tr[i].getElementsByTagName("td");
            if (td) {
                var playerMatch = playerName && td[0].innerHTML.toLowerCase().indexOf(playerName) > -1,
                    noInput = !playerName;
                if (noInput || playerMatch) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }
}

function drawComparedPlayer() {
    var size = 1000,
        _top = 100,
        right = 100,
        bottom = 100,
        left = 100;
    var data = [],
        names = [];
    var i = 0;
    selectedPlayers.slice(Math.max(0, selectedPlayers.length - 10)).forEach(function (id) {
        data.push(radarData[id]);
        names.push("<strong><span class='selected-player' id='selected-player-" + String(id) + "' style='color:" + radarColors[i] + "'>" + radarData[id][0].name + "</span></strong>");
        i += 1;
    });
    document.getElementsByClassName('comparedPlayersTitle')[0].innerHTML = 'Compare: ' + names.join(', ');
    $(document).on('click', '.selected-player', function () {
        var id = parseInt($(this).attr('id').replace('selected-player-', ''));
        d3.select('#player-' + String(i)).style('background-color', '#fff');
        delete selectedPlayers[selectedPlayers.indexOf(id)];
        drawComparedPlayer();
    });
    drawDashboard(data, 'comparedPlayers', size, _top, right, bottom, left, maxValue);
}
function drawTable() {
    var table = d3.select('.playerTable');
    var tHead = table.append('tr').attr('class', 'header');
    tHead.selectAll('th')
        .data(TABLE_HEADERS).enter()
        .append('th')
        .text(function (column) {
            return column;
        });
    var rows = table.selectAll('tr').filter('.player-row')
        .data(playerData)
        .enter()
        .append('tr').attr('class', 'player-row').attr('id', function (d, i) {
            return 'player-' + String(i);
        })
        .on("mouseover", function (d, i) {
            d3.select('#player-' + String(i)).style('background-color', '#f1f1f1');
        })
        .on("mouseout", function (d, i) {
            if (selectedPlayers.indexOf(i) < 0) {
                d3.select('#player-' + String(i)).style('background-color', '#fff');
            }
        })
        .on("click", function (d, i) {
            if (selectedPlayers.indexOf(i) < 0) {
                d3.select('#player-' + String(i)).style('background-color', '#f1f1f1');
                selectedPlayers.push(i);
            } else {
                d3.select('#player-' + String(i)).style('background-color', '#fff');

                delete selectedPlayers[selectedPlayers.indexOf(i)];
            }
            drawComparedPlayer();
        });
    rows.selectAll('td')
        .data(function (row) {
            return TABLE_HEADERS.map(function (column, index) {
                return {column: column, value: row[index]};
            });
        })
        .enter()
        .append('td')
        .text(function (d) {
            return d.value;
        });
}

function parsePlayerRadarData(originalData) {
    var radarData = [];
    originalData.forEach(function (playerData, index) {
        radarData.push([]);
        for (var j = TABLE_HEADERS.length; j < playerData.length; j++) {
            var combinedValue = playerData[j].split('(');
            var originalValue = combinedValue[0];
            var value = combinedValue[1].split(')')[0];
            radarData[index].push({
                axis: HEADERS[j - TABLE_HEADERS.length],
                value: value,
                originValue: originalValue,
                type: parseInt(playerData[2]),
                name: playerData[0],
            });
        }
    });
    return radarData
}

function drawDashboard(data, className, size, _top, right, bottom, left, maxValue) {
    var margin = {top: _top, right: right, bottom: bottom, left: left},
        width = Math.min(size, window.innerWidth - 10) - margin.left - margin.right,
        height = Math.min(width, window.innerHeight - margin.top - margin.bottom - 20);
    var radarChartOptions = {
        w: width,
        h: height,
        margin: margin,
        maxValue: maxValue,
        levels: 10,
        roundStrokes: false,
        desc: true
    };
    RadarChart(className, data, radarChartOptions);
}
