var HEADERS = {'defensive': [ 'Tackles','Clearances', 'Interceptions', 'Passes Blocks', 'Shots Blocks', 'Fouls'],
            'passing': ['Short Passes', 'Long Passes',  'Cross Passes', 'Short Key Passes', 'Long Key Passes'],
            'control': ['Dribbles', 'Fouled', 'Aerials','Dispossessed' , 'Unsuccessful Touches'],
            'attack': ['Out Of Box Shots','Penalty Area Shots', 'Head Shots', 'Counter Shots', 'Open Play Shots']},
    TABLE_HEADERS = ['Name', 'Team', 'Season', 'Type'],
    radarColors = d3.scale.category10().range(),
    maxValue = 0.7,
    noTable = true,
    clusters, radarData = {},
    playerData, selectedPlayers = [];

Object.keys(HEADERS).forEach(function(key, i) {
  d3.text('../cluster_result/kmeans_' + key + '_league_data.csv', function (error, text) {
  		playerData = d3.csv.parseRows(text);
  		radarData[key] = parsePlayerRadarData(playerData,key);
  		drawComparedPlayer(key);
      if (i == 3) {drawTable();};
      noTable = false;
  });
});

function searchBy(event) {
        if (event.keyCode == 13) {
            var playerName = document.getElementById("playerSearch").value.toLowerCase();
            var teamName = document.getElementById("teamSearch").value.toLowerCase();
            var table = document.getElementsByClassName("playerTable")[0];
            var tr = table.getElementsByClassName("player-row");
            // Loop through all table rows, and hide those who don't match the search query
            for (var i = 0; i < tr.length; i++) {
                var td = tr[i].getElementsByTagName("td");
                if (td) {
                    var playerMatch = playerName && td[0].innerHTML.toLowerCase().indexOf(playerName) > -1,
                        teamMatch = teamName && td[1].innerHTML.toLowerCase().indexOf(teamName) > -1,
                        bothMatch = playerName && teamName && playerMatch && teamMatch,
                        noInput = !playerName && !teamName,
                        onlyOneMatch = (!playerName && teamMatch) || (!teamName && playerMatch)
                    if (bothMatch || noInput || onlyOneMatch) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        }
    }

function drawComparedPlayer(key) {
    var size = 600,
        _top = 80,
        right = 100,
        bottom = 80,
        left = 100;
    var data = [],
        names = [];
    var i = 0;
    selectedPlayers.slice(Math.max(0, selectedPlayers.length - 10)).forEach(function (id) {
        data.push(radarData[key][id]);
        names.push("<strong><span class='selected-player' id='selected-player-" + String(id) + "' style='color:" + radarColors[i] + "'>" + radarData[key][id][0].name + "</span></strong>");
        i += 1;
    });
    document.getElementsByClassName('comparedPlayersTitle')[0].innerHTML = 'Compare: ' + names.join(', ');
    document.getElementsByClassName('comparedPlayersTitle')[1].innerHTML = 'Compare: ' + names.join(', ');
    document.getElementsByClassName('comparedPlayersTitle')[2].innerHTML = 'Compare: ' + names.join(', ');
    document.getElementsByClassName('comparedPlayersTitle')[3].innerHTML = 'Compare: ' + names.join(', ');
    $(document).on('click', '.selected-player', function () {
        var id = parseInt($(this).attr('id').replace('selected-player-', ''));
        d3.select('#player-' + String(i)).style('background-color', '#fff');
        delete selectedPlayers[selectedPlayers.indexOf(id)];
        Object.keys(HEADERS).forEach(function(key) {
            drawComparedPlayer(key);
        });
    });
    drawDashboard(data, key, size, _top, right, bottom, left, maxValue);
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
            Object.keys(HEADERS).forEach(function(key) {
              drawComparedPlayer(key);
            });
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

function parsePlayerRadarData(originalData, key) {
    var radarData = [];
    originalData.forEach(function (playerData, index) {
        radarData.push([]);
        for (var j = TABLE_HEADERS.length; j < playerData.length; j++) {
            var combinedValue = playerData[j].split('(');
            var originalValue = combinedValue[0];
            var value = combinedValue[1].split(')')[0];
            radarData[index].push({
                axis: HEADERS[key][j - TABLE_HEADERS.length],
                value: value,
                originValue: originalValue,
                type: parseInt(playerData[3]),
                name: playerData[0] + "(" + playerData[2] + ")",
                team: playerData[1],
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
