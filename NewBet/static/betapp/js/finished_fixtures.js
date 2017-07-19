$(document).ready(function () {

    var comparison_matchday = function(filter_value, matchday){
      return  filter_value === matchday;
    };
    var comparison_team_name = function(filter_value, home_team, away_team){
        console.log(home_team.includes(filter_value));
      return  (home_team.includes(filter_value) ||
      away_team.includes(filter_value));
    };
    var check_comparison = function(filter_value){
        if (isNaN(parseInt(filter_value))){
            return "name"
            } else {
            return "matchday"
            }
    };

    var filter_input = $('#match-filter');
    $(filter_input).keyup(function (){
        var lists = $('.list');
        var filter_value = filter_input.val();
        lists.toggle(display = false);
        if (filter_value === "") {
            lists.toggle(display = true)
        } else {
            var comparison_name = check_comparison(filter_value);

            for (var i = 0; i < lists.length; i++){
                var matchday = $(lists[i]).find('.matchday').text();
                var home_team = $(lists[i]).find('.home-team-name').text();
                var away_team = $(lists[i]).find('.away-team-name').text();
                if (comparison_name === "name"){
                    var comparison_function = comparison_team_name(filter_value,
                        home_team, away_team)
                } else if (comparison_name === "matchday"){
                    var comparison_function = comparison_matchday(filter_value,
                        matchday)
                }
                if (comparison_function){
                    $(lists[i]).toggle(display = true);
                }
            }
        }
    });
});

