$(document).ready(function () {
    var fixtures_spans = $('.fixtures-description')
    $(fixtures_spans).each(function(){
        $(this).click(function(){
            $(this).parent().next().toggle()
        })
    })
});

