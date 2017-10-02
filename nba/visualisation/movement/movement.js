var API_PATH;
API_PATH = function (eventID) {
    return 'json/' + eventID + '.json'
};
var eventID = 2;
var pause = false;
var withShadow = true;

var court = d3.select("svg");
var width = 94 * 10;
var height = 50 * 10;
var updatePeriod = 25;
var transitionTime = 10 / 25;
var home_color = 'steelBlue';
var visitor_color = 'Black';
var ball_color = 'DarkOrange';
var next = false;
var prev = false;
var player_radius = 14;
var ball_radius = 6;

function clickPlay() {
    if (d3.selectAll('.item')[0].length == 0) {
        drawWithAPI(API_PATH(eventID));
    }
}

function clickNext() {
    next = true;
    pause = true;
    prev = false;
}

function clickPrev() {
    prev = true;
    pause = true;
    next = false;
}

function clickPause() {
    pause = !pause
}
function drawWithAPI(url) {
    d3.json(url, function (error, data) {
        if (error) {
            console.log(error);
            eventID++;
            if (eventID > 55) { eventID = 2};
            drawWithAPI(API_PATH(eventID));
        } else {
            console.log(data)
            drawMovement(data)
        }
    });
}

function drawMovement(data) {
    var dataSet = parseData(data);
    var players = dataSet.players;
    var movements = dataSet.moments;
    var max_ball_height = 0;
    movements.map
    (function (m) {
        if (max_ball_height < m.ball[0].z) {
            max_ball_height = m.ball[0].z;
        }
    });
    var movement = movements[0];
    var index = 1;
    var home = movement.home;
    var visitor = movement.visitor;
    var ball = movement.ball;
    var r = d3.scale.linear()
        .domain([0, max_ball_height])
        .range([1, 2 * ball_radius]);

    court.selectAll('.item').remove();
    newPoint(home, 'home', player_radius, home_color);
    newPoint(visitor, 'visitor', player_radius, visitor_color);
    newPoint(ball, 'ball', ball_radius, ball_color, 1);

    function newPoint(data, className, radius, color, stroke_width) {
        var point = court.selectAll('.dataCircle')
            .data(data)
            .enter();
        var circle = point.append('circle')
            .attr('cx', function (d, i) {
                return d.x;
            })
            .attr('cy', function (d, i) {
                return d.y;
            })
            .attr('stroke', 'white')
            .attr('stroke-width', stroke_width || player_radius / 5)
            .attr('r', function (d) {
                return Math.max(radius, r(d.z))
            })
            .style("fill-opacity", 1)
            .style('fill', color)
            .style("stroke-opacity", radius / 5)
            .attr("result", "offsetBlur")
            .attr("class", 'item')
            .attr("id", function (d) {
                var elementId = className;
                var player = players[d.playerid];
                if (player) {
                    elementId += '-' + player.jersey
                }
                return elementId
            })
            .classed(className, true);

        var text = court.selectAll('.dataText')
            .data(data)
            .enter()
            .append('text')
            .attr('x', function (d, i) {
                return d.x;
            })
            .attr('y', function (d, i) {
                return d.y;
            })
            .text(function (d) {
                var player = players[d.playerid]
                if (player) {
                    return player.jersey// + '-' + player.position
                } else {
                    return ''
                }
            })
            .attr("class", 'item')
            .classed(className + '-text', true)
            .attr({
                "alignment-baseline": "middle",
                "text-anchor": "middle",
                "font-family": "'Oswald', sans-serif",
                "fill": "white",
                "font-size": 10
            });

        if (withShadow) {
            circle
                .attr('stroke-width', stroke_width || 0)
                .transition()
                .duration(100)
                .ease('linear')
                .attr("r", function (d) {
                    return Math.max(radius, r(d.z))
                })
                .style("fill-opacity", 0)
                .style("stroke-opacity", 1e-6)
                .remove();
            text.transition()
                .duration(40)
                .ease('linear')
                .remove();
        }
    }

    function movePoints(data, className, radius) {
        court.selectAll("." + className)
            .data(data)
            .style("fill-opacity", 1)
            .style("stroke-opacity", 1)
            .transition()
            .duration(transitionTime)
            .attr('cx', function (d) {
                return d.x;
            })
            .attr('cy', function (d) {
                return d.y;
            })
            .attr('r', function (d) {
                return Math.max(radius, r(d.z))
            });
        court.selectAll('.' + className + '-text')
            .data(data)
            .transition()
            .duration(transitionTime)
            .attr('x', function (d, i) {
                return d.x;
            })
            .attr('y', function (d, i) {
                return d.y;
            });
    }

    var intervalId = setInterval(function () {
        if (next && index < movements.length - 1) {
            index++;
            next = false;
        }
        if (prev && index > 1) {
            index--;
            prev = false;
        }
        var dataset = movements[index];
        var home = dataset.home;
        var visitor = dataset.visitor;
        var ball = dataset.ball;
        if (withShadow) {
            newPoint(home, 'home', player_radius, home_color);
            newPoint(visitor, 'visitor', player_radius, visitor_color);
            newPoint(ball, 'ball', ball_radius, ball_color, 1);

        } else {
            movePoints(home, 'home', player_radius);
            movePoints(visitor, 'visitor', player_radius);
            movePoints(ball, 'ball', ball_radius);
        }
        if (pause) {
            return
        }
        index++;
        d3.timer.flush();
        if (index >= movements.length) {
            index = 0;
            clearInterval(intervalId);
            eventID++;
            drawWithAPI(API_PATH(eventID));
        }
    }, updatePeriod);

    function parseData(data) {
        data.teams = {};
        data.players = {};
        var teamkeys = ["home", "visitor"];
        for (var i in teamkeys) {
            var key = teamkeys[i];
            var team = data[key];
            var teamid = team.teamid;
            data.teams[teamid] = team;
            data.teams[teamid].type = key;
            for (var j in team.players) {
                var player = team.players[j];
                player.name = player.firstname + " " + player.lastname;
                player.teamid = team.teamid;
                player.teamname = team.name;
                player.teamtype = team.type;
                data.players[player.playerid] = player
            }
        }
        data.moments = data.moments.map(parseMoment.bind(data));
        return data;
    }

    function parseMoment(moment, index) {
        var info = {
            period: moment[0],
            timestamp: moment[1],
            gameclock: moment[2],
            shotclock: moment[3],
            eventid: moment[4]
        };
        var ps = moment[5].map(function (n, i) {
            var obj = {
                teamid: n[0],
                playerid: n[1],
                x: n[2] * 10,
                y: n[3] * 10,
                z: n[4] * 10,
                hide: false
            };
            return obj
        });
        var obj = {
            info: info,
            ball: [ps[0]],
            home: ps.slice(1, 6),
            visitor: ps.slice(6, 11)
        };
        return obj
    }
}