var url = 'position_locations.json'
var pause = false;
var withShadow = false;
var teams, home, away, players, home_players, away_players, events
var court = d3.select("svg");
var width = 458;
var height = 344;
var updatePeriod = 1;
var transitionTime = 10/25;
var ball_color = 'DarkOrange';
var next = false;
var prev = false;
var index = 0;
var player_radius = 10;
var ball_radius = 4;
function draw() {
    d3.json(url, function (error, data) {
        console.log(data)
        newPoint(data, 'home', player_radius, 'red');
    });

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
    function newPoint(data, className, radius, color, stroke_width) {
        var point = court.selectAll('.dataCircle')
            .data(data)
            .enter();
        var circle = point.append('circle')
            .attr('cx', function (d, i) {
                return d.x_loc/100 * width;
            })
            .attr('cy', function (d, i) {
                return d.y_loc/100 * height;
            })
            .attr('stroke', 'white')
            .attr('stroke-width', stroke_width || player_radius / 5)
            .attr('r', function (d) {
                return radius
            })
            .style("fill-opacity", function(d){
                return d.per * 2
            })
            .style("stroke-opacity", function(d){
                return d.per * 2
            })
            .style('fill', color)
            .attr("result", "offsetBlur")
            .attr("class", 'item')
            // .attr("id", function (d) {
            //     return className + '-' + players[d.id].shirt_num
            // })
            .classed(className, true);
    
        var text = court.selectAll('.dataText')
            .data(data)
            .enter()
            .append('text')
            .attr('x', function (d, i) {
                return d.x_loc/100 * width;
            })
            .attr('y', function (d, i) {
                return d.y_loc/100 * height;
            })
            .text(function (d) {
                return //d.per;
            })
            .attr("class", 'item')
            .classed(className + '-text', true)
            // .attr("id", function (d) {
            //     return className + '-' + players[d.id].shirt_num
            // })
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
                    return radius
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
}
function clickPlay() {
    draw()
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
