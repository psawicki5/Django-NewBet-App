$(document).ready(function(){
    var plot_div = $('#team-standings');
    var competition_id = $(plot_div).data('competition-id');
    var team_id = $(plot_div).data('team-id');

    var ajax_function = function(competition_id, team_id){
        var url = competition_id + "/" + team_id;
        $.ajax({
            url: "http://127.0.0.1:8000/team_standings/" + url,
            data: {},
            type: "GET",
            dataType: "json"
        })
        .done(function(json) {
            plotting_function(json);
        })
        .fail(function() {
            console.log( "error" );
        })
        .always(function() {
            console.log( "complete" );
        });
    };
    var plotting_function = function(json){
        var trace = {
            x: json['matchday_list'],
            y: json['standing_list'],
            type: 'scatter'
        };
        var layout = {
            xaxis: {
                title: 'MATCHDAY',
                autotick: false,
                ticks: 'outside',
                tick0: 0,
                dtick: 1,
                ticklen: 8,
                tickwidth: 2,
                tickcolor: '#000'
            },
            yaxis: {
                title: 'STANDING',
                range: [20, 0.5],
                autotick: false,
                ticks: 'outside',
                tick0: 0,
                dtick: 1,
                ticklen: 8,
                tickwidth: 2,
                tickcolor: '#000'
            },
            margin: {
                l: 100,
                r: 100,
                b: 100,
                t: 100,
                pad: 4
            }
        };
        var data = [trace];
        Plotly.newPlot('team-standings', data, layout)
    };
    ajax_function(competition_id, team_id)
});

