var playersData, playerNames, selectPlayer,
	TABLE_HEADERS = ['Name'];
d3.json("play_types_trend.json", function(error, json) {
	playersData = json;
	playerNames = [];
	Object.keys(playersData).forEach(function(key, index) {
		playerNames.push({id: index, nameUniq: key,  name: playersData[key].name })
	});
	selectPlayer = 'chris paul'
	drawTrendArea('playTypesTrend', playersData['chris paul'].values)
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
                    noInput = !playerName && !teamName;
                if (noInput || playerMatch) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }
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
        .data(playerNames)
        .enter()
        .append('tr').attr('class', 'player-row').attr('id', function (d, i) {
            return 'player-' + String(i);
        })
        .on("mouseover", function (d, i) {
            d3.select('#player-' + String(i)).style('background-color', '#f1f1f1');
        })
        .on("mouseout", function (d, i) {
            if (selectPlayer != d.nameUniq) {
                d3.select('#player-' + String(i)).style('background-color', '#fff');
            }
        })
        .on("click", function (d, i) {
            if (selectPlayer != d.nameUniq) {
                d3.select('#player-' + String(i)).style('background-color', '#f1f1f1');
                selectPlayer = d.nameUniq;
								document.getElementsByClassName('playTypesTrendTitle')[0].innerHTML = 'Player Type Trend:: ' + d.name;
								drawTrendArea('playTypesTrend', playersData[selectPlayer].values)
            }
        });
    rows.selectAll('td')
        .data(function (row) {
            return TABLE_HEADERS.map(function (column, index) {
                return {column: column, value: row.name};
            });
        })
        .enter()
        .append('td')
        .text(function (d) {
            return d.value;
        });
}
function drawTrendArea(className, data) {
	var margin = {top: 20, right: 100, bottom: 30, left: 50},
	    width = 800 - margin.left - margin.right,
	    height = 600 - margin.top - margin.bottom;

	var parseYear = d3.format(""),
	    formatPercent = d3.format(".0%");

	var x = d3.scale.linear()
	    .range([0, width]);

	var y = d3.scale.linear()
	    .range([height, 0]);

	// var color = d3.scale.category20c();
	var color = d3.scale.ordinal().range(["#3182bd", "#6baed6", "#9ecae1", "#c6dbef", "#e6550d", "#fd8d3c", "#fdae6b", "#fdd0a2", "F8DBBD", "#31a354", "#74c476", "#a1d99b", "#c7e9c0",
	 																			"#756bb1", "#9e9ac8", "#bcbddc", "#dadaeb", "#636363", "#969696", "#bdbdbd", "#d9d9d9"])
	var years = []
	var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom")
	    .tickFormat(function(year) {
				var nextYear = String(year+1)
				var year = String(year)[2] + String(year)[3] + "-" + nextYear[2] + nextYear[3]
				if (years.indexOf(year) >= 0) {
					return ""
				} else {
						years.push(year)
						return year
				}
			});

	var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left")
	    .tickFormat(formatPercent);

	var area = d3.svg.area()
	    .x(function(d) { return x(d.date); })
	    .y0(function(d) { return y(d.y0); })
	    .y1(function(d) { return y(d.y0 + d.y); });

	var stack = d3.layout.stack()
	    .values(function(d) { return d.values; });

	d3.select('.' + className).select('svg').remove()
	var svg = d3.select('.' + className).append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  	.append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  color.domain(d3.keys(data[0]).filter(function(key) { return key !== "date"; }));

  var browsers = stack(color.domain().map(function(name) {
    return {
      name: name,
      values: data.map(function(d) {
        return {date: d.date, y: d[name] / 100};
      })
    };
  }));

  x.domain(d3.extent(data, function(d) { return d.date; }));

  var browser = svg.selectAll(".browser")
      .data(browsers)
    .enter().append("g")
      .attr("class", "browser");

  browser.append("path")
      .attr("class", "area")
      .attr("d", function(d) {
        var ar =  area(d.values);
        return ar;
      })
      .style("fill", function(d) { return color(d.name); })
			.style('stroke-width', 1.5)
			.style('stroke', 'white')
			.style('stroke-opacity', 0.7);


  // browser.append("text")
  //     .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
  //     .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.y0 + d.value.y / 2) + ")"; })
  //     .attr("x", -50)
  //     .attr("dy", ".35em")
  //     .text(function(d) { return d.name; });

  var legendClassArray = []
  var legend = svg.selectAll(".legend")
        .data(color.domain().slice().reverse())
      	.enter().append("g")
        //.attr("class", "legend")
        .attr("class", function (d) {
          legendClassArray.push(d.replace(/\s/g, '')); //remove spaces
          return "legend";
        })
        .attr("transform", function(d, i) { return "translate(0," + i * 30 + ")"; });

    //reverse order to match order in which bars are stacked
    legendClassArray = legendClassArray.reverse();

    legend.append("rect")
        .attr("x", width + 5)
        .attr("width", 30)
        .attr("height", 18)
        .style("fill", color)
        .attr("id", function (d, i) {
          return "id" + d.replace(/\s/g, '');
        });

    legend.append("text")
        .attr("x", width + 40)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "start")
        .text(function(d) { return d; });

    function restorePlot(d) {

      state.selectAll("rect").forEach(function (d, i) {
        //restore shifted bars to original posn
        d3.select(d[idx])
          .transition()
          .duration(1000)
          .attr("y", y_orig[i]);
      })

      //restore opacity of erased bars
      for (i = 0; i < legendClassArray.length; i++) {
        if (legendClassArray[i] != class_keep) {
          d3.selectAll(".class" + legendClassArray[i])
            .transition()
            .duration(1000)
            .delay(750)
            .style("opacity", 1);
        }
      }

    }
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);
}
