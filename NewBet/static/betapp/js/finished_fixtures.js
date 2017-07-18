$(document).ready(function () {
    var matchday_input = $('#matchday-filter');
    var team_name_input = $('#team-name-filter');
    $(matchday_input).keyup(function (){
        var lists = $('.list');
        var matchday_value = matchday_input.val();
        lists.toggle(display = true);
        if (matchday_value === "") {
            lists.toggle(display = true)
        } else {
            for (var i = 0; i < lists.length; i++){
                if ($(lists[i]).find('.matchday').text() !== matchday_value){
                    $(lists[i]).toggle(display = false);
                }
            }
        }
    });
    $(team_name_input).keyup(function () {
        var name_value = team_name_input.val();
        if(name_value === "1"){
            console.log("cokolwiek")
        }
    })
});