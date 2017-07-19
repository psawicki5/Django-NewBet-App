$(document).ready(function () {
    var fixture_a = $('.fixtures-description');
    $(fixture_a).each(function(){
        $(this).click(function(event){
            event.preventDefault();
            $(this).next().toggle();
        })
    })
});

