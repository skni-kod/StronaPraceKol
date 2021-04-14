$().ready(function () {
    setInterval(GetMessage, GetMessageInterval);

    $(".message_link").on('click', function(event){
         $("#messages_box").html('');
        ReviewerId = $(this).attr('data-reviewer');
        CanGetMessage = true;
        LastMessageId = -1;
        GetMessage();
        RenderMessages();
    });

    $.get('review/assign/',
        {
            paper_id: PaperId,
            reviewer_id: ReviewerId,
            last_message_id: LastMessageId,
        },
        function (data, status) {
            if (status == 'success') {
                $('#admin-assign-reviewers').html(data)
            }
            CanGetMessage = true;
        });
});
