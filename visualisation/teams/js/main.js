d3.json('data/team_summary.json', function(data) {

    var keys = data['headers'];
    var bounds = data['bounds'];
    var data = data['data'];
    var diffSize = true;
    var teams = _.keys(data);
    var xAxis = 'Win Percent', yAxis = 'Diff Goals';
    var xReverse = false, yReverse = true;
    var team = teams[0];

    var svg = d3.select("#chart")
        .append("svg")
        .attr("width", 2000)
        .attr("height", 1000);
    var xScale, yScale;

    svg.append('g')
        .classed('chart', true)
        .attr('transform', 'translate(80, 60)');

    d3.select('#team-menu')
        .selectAll('li')
        .data(teams)
        .enter()
        .append('li')
        .text(function(d) {return d;})
        .classed('selected', function(d) {
            return d === team;
        })
        .on('click', function(d) {
            if (team === d) {
                diffSize = !diffSize;
            }
            team = d;
            generateChart();
            updateMenus();
        });

    d3.select('#x-axis-menu')
        .selectAll('li')
        .data(keys)
        .enter()
        .append('li')
        .text(function(d) {return d;})
        .classed('selected', function(d) {
            return d === xAxis;
        })
        .on('click', function(d) {
            if (xAxis === d) {
                xReverse = !xReverse;
            }
            xAxis = d;
            generateChart();
            updateMenus();
        });

    d3.select('#y-axis-menu')
        .selectAll('li')
        .data(keys)
        .enter()
        .append('li')
        .text(function(d) {return d;})
        .classed('selected', function(d) {
            return d === yAxis;
        })
        .on('click', function(d) {
            if (yAxis === d) {
                yReverse = !yReverse;
            }
            yAxis = d;
            generateChart();
            updateMenus();
        });

    d3.select('svg g.chart')
        .append('text')
        .attr({'id': 'countryLabel', 'x': 0, 'y': 60})
        .style({'font-size': '20px', 'font-weight': 'bold', 'fill': '#ddd'});

    d3.select('svg g.chart')
        .append('text')
        .attr({'id': 'xLabel', 'x': 400, 'y': 670, 'text-anchor': 'middle'})
        .text(xAxis);

    d3.select('svg g.chart')
        .append('text')
        .attr('transform', 'translate(-60, 330)rotate(-90)')
        .attr({'id': 'yLabel', 'text-anchor': 'middle'})
        .text(yAxis);

    updateScales();
    generateChart();

    updateChart();
    updateMenus();

    d3.select('svg g.chart')
        .append("g")
        .attr('transform', 'translate(0, 630)')
        .attr('id', 'xAxis')
        .call(makeXAxis);

    d3.select('svg g.chart')
        .append("g")
        .attr('id', 'yAxis')
        .attr('transform', 'translate(-10, 0)')
        .call(makeYAxis);


    function generateChart(init) {
        var pointColour = d3.scale.category20b();
        d3.select('svg g.chart')
            .selectAll('circle')
            .data(data['All Teams'])
            .enter()
            .append('circle')
            .style('opacity', function(d) {
                if (d.LEAGUE === team || team == 'All Teams') {
                  return 0.5;
                } else {
                  return 0;
                }
            })
            .attr('cx', function(d) {
                return isNaN(d[xAxis]) ? d3.select(this).attr('cx') : xScale(d[xAxis]);
            })
            .attr('cy', function(d) {
                return isNaN(d[yAxis]) ? d3.select(this).attr('cy') : yScale(d[yAxis]);
            })
            .attr('fill', function(d, i) {return 'steelBlue';})
            .style('cursor', 'pointer')

            .on('mouseover', function(d) {

                if (d.LEAGUE === team || team == 'All Teams') {
                    d3.select('svg g.chart #countryLabel')
                        .text(d.NAME)
                        .transition()
                        .style('opacity', 1);
                }
            })
            .on('mouseout', function(d) {
                d3.select('svg g.chart #countryLabel')
                    .transition()
                    .duration(1500)
                    .style('opacity', 0);
            });
        updateChart();
    }

    function updateChart() {
        updateScales();

        d3.select('svg g.chart')
            .selectAll('circle')
            .transition()
            .duration(500)
            .ease('quad-out')
            .attr('cx', function(d) {
                return isNaN(d[xAxis]) ? d3.select(this).attr('cx') : xScale(d[xAxis]);
            })
            .attr('cy', function(d) {
                return isNaN(d[yAxis]) ? d3.select(this).attr('cy') : yScale(d[yAxis]);
            })
            .attr('r', function(d) {
                return isNaN(d[xAxis]) || isNaN(d[yAxis]) ? 0 : (diffSize ? 20 * (d['Total Games']/bounds['Total Games'].max) : 12);
            })
            .style('opacity', function(d) {
                return (d.LEAGUE === team || team == 'All Teams') ? (diffSize ? (d['Total Games']/bounds['Total Games'].max) : 1) : 0;
            });

        d3.select('#xAxis')
            .transition()
            .call(makeXAxis);

        d3.select('#yAxis')
            .transition()
            .call(makeYAxis);

        d3.select('#xLabel')
            .text(xAxis);

        d3.select('#yLabel')
            .text(yAxis);
    }

    function getDomain(key, reverse) {
        return reverse ? [bounds[key].min, bounds[key].max].reverse() : [bounds[key].min, bounds[key].max]
    }

    function updateScales() {
        xScale = d3.scale.linear()
            .domain(getDomain(xAxis, xReverse))
            .range([20, 780]);

        yScale = d3.scale.linear()
            .domain(getDomain(yAxis, yReverse))
            .range([600, 100]);
    }

    function makeXAxis(s) {
        s.call(d3.svg.axis()
            .scale(xScale)
            .orient("bottom"));
    }

    function makeYAxis(s) {
        s.call(d3.svg.axis()
            .scale(yScale)
            .orient("left"));
    }

    function updateMenus() {
        d3.select('#team-menu')
            .selectAll('li')
            .classed('selected', function(d) {
                return d === team;
            });
        d3.select('#x-axis-menu')
            .selectAll('li')
            .classed('selected', function(d) {
                return d === xAxis;
            });
        d3.select('#y-axis-menu')
            .selectAll('li')
            .classed('selected', function(d) {
                return d === yAxis;
            });
    }

})
