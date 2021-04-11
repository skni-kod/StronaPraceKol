$().ready(function () {
    $(".message_link").on('click', function(event){
        ReviewerId = $(this).attr('data-reviewer');
        GetMessage();
        CanGetMessage = true;
    });
});
