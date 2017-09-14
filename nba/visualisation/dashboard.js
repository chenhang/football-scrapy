var CLUSTER_RESULT_PATH = '../cluster_result/centers.json',
    ALL_KMEANS_PLAYER_PATH = '../cluster_result/kmeans_league_data.csv',
    // HEADERS = ['Tackles', 'Clearances', 'Interceptions', 'Short Passes', 'Long Passes', 'Cross Passes', 'Dribbles', 'OutOfBox Shots', 'PenaltyArea Shots', 'Aerials'];
    // HEADERS = ["Post-Up","P&R Ball Handler", "Isolation", "Transition", "Offscreen", "Handoff", "Spot-Up", "P&R Roll Man", "Cut", "Putbacks"];
    HEADERS = ["背身","挡拆持球","面框单打","转换进攻","绕掩护","手递手","定点突投","挡拆接球", "空切","二次进攻"]
var TABLE_HEADERS = ['Name', 'Team', 'Type', 'Season'],
    radarColors = d3.scale.category10().range(),
    maxValue = 0.7,
    clusters, playerData, displayedData, radarData,
    selectedPlayers = [];

d3.json(CLUSTER_RESULT_PATH, function (error, data) {
    clusters = parseCenters(data);
    drawClusters('clusters');
    drawCompareClusters(undefined);
    d3.text(ALL_KMEANS_PLAYER_PATH, function (text) {
        playerData = d3.csv.parseRows(text);
        radarData = parsePlayerRadarData(playerData);
        displayedData = playerData;
        drawPlayerWithType(0);
        drawComparedPlayer();
        drawTable();
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
function drawPlayerWithType(i) {
    var size = 600,
        _top = 100,
        right = 100,
        bottom = 100,
        left = 100;
    var player = radarData[i];
    var playerInfo = "<strong><span style='color:" + radarColors[1] + "'>" + player[0].name + ', ' + player[0].team + '</strong></span>';
    var typeInfo = "<strong><span style='color:" + radarColors[0] + "'>Player Type: " + player[0].type + '</strong></span>';
    document.getElementsByClassName('playerClusterTitle')[0].innerHTML = playerInfo + ', ' + typeInfo;
    drawDashboard([clusters[player[0].type], player], 'playerCluster', size, _top, right, bottom, left, maxValue);
}

function drawComparedPlayer() {
    var size = 600,
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
            drawPlayerWithType(i);
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
                name: playerData[0] + "(" + playerData[3] + ")",
                team: playerData[1],
            });
        }
    });
    return radarData
}
function parseCenters(originalData) {
    var radarData = [];
    for (var i = 0; i < originalData.length; i++) {
        var axisData = originalData[i];
        while (radarData.length < axisData.length) {
            radarData.push([])
        }
        axisData.forEach(function (value, index) {
            radarData[index].push({axis: HEADERS[i], value: value, originValue: value});
        })
    }
    return radarData
}

function drawClusters(className) {
    var size = 300,
        _top = 50,
        right = 60,
        bottom = 50,
        left = 50;
    clusters.forEach(function (line, index) {
        d3.select('.' + className).append('span').attr('class', 'type-' + String(index));
        drawDashboard([line], 'type-' + String(index), size, _top, right, bottom, left, maxValue);
    });
}
function drawCompareClusters(event) {
    if (event == undefined || event.keyCode == 13) {
        var clusterIds = document.getElementById("clustersSearch").value.split(',');
        var size = 600,
            _top = 80,
            right = 100,
            bottom = 80,
            left = 100;
        var comparedClusters = [];

        var newTitle = [];
        var i = 0;
        clusterIds.forEach(function (id) {
            if (clusters[parseInt(id)]) {
                comparedClusters.push(clusters[parseInt(id)])
                var typeInfo = "<strong><span style='color:" + radarColors[i] + "'>Type " + id + '</strong></span>';
                i += 1;
                newTitle.push(typeInfo);
            }
        });
        if (newTitle.length == 0) {
            document.getElementsByClassName('clustersComparedTitle')[0].innerHTML = 'Types';
        } else {
            document.getElementsByClassName('clustersComparedTitle')[0].innerHTML = newTitle.join(', ');
        }
        drawDashboard(comparedClusters, 'comparedClusters', size, _top, right, bottom, left, maxValue);
    }
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
