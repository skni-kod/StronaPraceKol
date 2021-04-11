$().ready(function () {
    //setInterval(GetMessage, GetMessageInterval);
    $(".message_link").on('click', function(event){
         $("#messages_box").html('');
        ReviewerId = $(this).attr('data-reviewer');
        CanGetMessage = true;
        LastMessageId = -1;
        GetMessage();
        RenderMessages();
    });
});

/*  TODO: add get message interval*/
