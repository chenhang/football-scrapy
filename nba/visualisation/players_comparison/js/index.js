var graph;
var dataSet;
//https://bl.ocks.org/jasondavies/1341281
var descriptions = {
    'shot_freq': 'Shot Frequency: Percentage of times the given shot type is executed',
    'play_freq': 'Play Frequency: Percentage of times the given play type is executed',
    'defender_range_out': 'Closest Defenders Distance when shot outside (>= 10 feets)',
    'defender_range': 'Closest Defenders Distance when shot inside (< 10 feets)',
    'touch_time_range': 'Touch time of shots',
    'dribbles_range': 'Dribbles count of shots',
    'base_per_36': 'Base stats Per 36 minutes',
    'base_defense': 'Base defence stat',
    'speed_distance': 'Speed and Distance',
    'passing': 'Passing and Assists stats',
    'transition': 'Transition: When the possession-ending event comes before the defense sets following a possession change and a transition from one end of the court to the other.',
    'isolation': 'Isolation: When the possession-ending event is created during a “one-on-one” matchup. The defender needs to be set and have all of his defensive options at the initiation of the play.',
    'pr_ball_handler': 'Pick & Roll: Ball Handler: A screen is set on the ball handler’s defender out on the perimeter. The offensive player can use the screen or go away from it and as long as the play yields a possession-ending event, it is tagged as a pick and roll.',
    'pr_rollman': 'Pick & Roll: Roll Man: When a screen is set for the ball handler, and the screen setter then receives the ball for a possession-ending event. This action can include: pick and rolls, pick and pops and the screener slipping the pick.',
    'postup': "Post-Up: When an offensive player receives the ball with their back to the basket and is less than 15' from the rim when the possession-ending event occurs.",
    'spotup': 'Spot-Up: When the possession-ending event is a catch-and-shoot or catch-and-drive play.',
    'handoff': 'Hand-Off: The screen setter starts with the ball and hands the ball to a player cutting close by. This enables the player handing the ball off to effectively screen off a defender creating space for the player receiving the ball.',
    'cut': 'Cut: An interior play where the finisher catches a pass while moving toward, parallel to or slightly away from the basket. This will include back screen and flash cuts as well as times when the player is left open near the basket.',
    'off_screen': 'Off Screen: Identifies players coming off of screens (typically downs screens) going away from the basket toward the perimeter. This includes curl, fades, and coming off straight.',
    'off_rebound': 'Rebound (Putbacks): When the rebounder attempts to score before passing the ball or establishing themselves in another play type.',
    'rim_defense': 'Rim defense',
    'defense_diff': 'Defense Diff: The difference between the normal field goal percentage of a shooter throughout the season and the field goal percentage when the defensive player is guarding the shooter. A good defensive number will be negative because the defensive player holds their opponent to a lower field goal percentage than normal',
    'player_style': '球员进攻风格'
};
d3.select('#shot-freq').on('click', function () {

    draw('shot_freq');
});

d3.select('#player-style').on('click', function () {

    draw('player_style');
});

d3.select('#play-freq').on('click', function () {
    draw('play_freq');
});

d3.select('#defender-range-out').on('click', function () {
    draw('defender_range_out');
});

d3.select('#defender-range').on('click', function () {
    draw('defender_range');
});

d3.select('#touch-time-range').on('click', function () {
    draw('touch_time_range');
});

d3.select('#dribbles-range').on('click', function () {
    draw('dribbles_range');
});

d3.select('#base-per-36').on('click', function () {
    draw('base_per_36');
});

d3.select('#base-defense').on('click', function () {
    draw('base_defense');
});

d3.select('#speed-distance').on('click', function () {
    draw('speed_distance');
});

d3.select('#passing').on('click', function () {
    draw('passing');
});

d3.select('#transition').on('click', function () {
    draw('transition');
});

d3.select('#isolation').on('click', function () {
    draw('isolation');
});

d3.select('#pr-ball-handler').on('click', function () {
    draw('pr_ball_handler');
});

d3.select('#pr-rollman').on('click', function () {
    draw('pr_rollman');
});

d3.select('#postup').on('click', function () {
    draw('postup');
});

d3.select('#spotup').on('click', function () {
    draw('spotup');
});

d3.select('#handoff').on('click', function () {
    draw('handoff');
});

d3.select('#cut').on('click', function () {
    draw('cut');
});

d3.select('#off-screen').on('click', function () {
    draw('off_screen');
});

d3.select('#off-rebound').on('click', function () {
    draw('off_rebound');
});

d3.select('#rim-defense').on('click', function () {
    draw('rim_defense');
});

d3.select('#defense-diff').on('click', function () {
    draw('defense_diff');
});


function draw(fileName) {
    d3.csv('data/' + fileName + '.csv', function (data) {
        d3.select('#wrapper').selectAll("*").remove();
        d3.select('#grid').selectAll("*").remove();
        d3.select('#title').text(descriptions[fileName] || fileName);
        dataSet = data;
        var cellWidthPct = 100.0/(Object.keys(dataSet[0]).length) + '%';
        graph = d3.parcoords()('#wrapper')
            .data(data)
            .alpha(0.4)
            .mode("queue")
            .rate(5)
            .render()
            .interactive()
            .brushable();


        graph.svg
            .selectAll(".dimension")
            .on("click", change_color);

        var grid = d3.divgrid();
        d3.select("#grid")
            .datum(data.slice(0, 400))
            .call(grid)
            .selectAll(".row")
            .on({
                "click": function (d) {
                    graph.highlight([d])
                }
            });

        graph.on("brush", function (d) {
            d3.selectAll('.cell').style('width', cellWidthPct);
            d3.select("#grid")
                .datum(d.slice(0, 400))
                .call(grid)
                .selectAll(".row")
                .on({
                    "click": function (d) {
                        graph.highlight([d])
                    },
                });
        });
        graph.on("render", function () {
            d3.selectAll('.cell').style('width', cellWidthPct);
        })
        d3.selectAll('.cell').style('width', cellWidthPct);

    });

    d3.select("#keep-data")
        .on("click", function () {
            new_data = graph.brushed();
            if (new_data.length == 0) {
                alert("Please do not select all the data when keeping/excluding");
                return false;
            }
            callUpdate(new_data);
        });

    d3.select("#exclude-data")
        .on("click", function () {
            new_data = _.difference(dataSet, graph.brushed());
            if (new_data.length == 0) {
                alert("Please do not select all the data when keeping/excluding");
                return false;
            }
            callUpdate(new_data);
        });


    d3.select("#reset-data")
        .on("click", function () {
            callUpdate(dataSet);
        });
    d3.select("#reset-highlight")
        .on("click", function () {
            graph.unhighlight()
        });

    var color_scale = d3.scale.linear()
        .domain([-2, -0.5, 0.5, 2])
        .range(["#DE5E60", "steelblue", "steelblue", "#98df8a"])
        .interpolate(d3.interpolateLab);

    function change_color(dimension) {
        graph.svg.selectAll(".dimension")
            .style("font-weight", "normal")
            .filter(function (d) {
                return d == dimension;
            })
            .style("font-weight", "bold");
        graph.color(zcolor(graph.data(), dimension)).render()
    }

    function zcolor(col, dimension) {
        var z = zscore(_(col).pluck(dimension).map(parseFloat));
        return function (d) {
            var value = d[dimension] || 0;
            return color_scale(z(value))
        }
    };

    function zscore(col) {
        var _col = col.filter(function(e){ return e === 0 || e });
        var n = _col.length,
            mean = _(_col).mean(),
            sigma = _(_col).stdDeviation();

        return function (d) {
            return (d - mean) / sigma;
        };
    };

    function callUpdate(data) {
        graph.data(data).brush();
    }
}
