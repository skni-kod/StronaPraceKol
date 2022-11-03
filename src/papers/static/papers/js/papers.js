$().ready(function () {
    CanGetMessage = false;
    setInterval(GetMessage, GetMessageInterval);

    $(".message_link").on('click', function (event) {
        $("#messages_box").html('');
        ReviewerId = $(this).attr('data-reviewer');
        CanGetMessage = true;
        LastMessageId = -1;
        GetMessage();
        RenderMessages();
    });

    $(".review-tab").click(function () {
        $.get('review/' + $(this).attr('data-reviewer'), {},
            function (data, status) {
                if (status == 'success') {
                    $('#review-'+$(this).attr('data-reviewer')+', .review-box').html(data);
                }
            });
    });

    if (is_staff == true) {
        $.get('review/assign/', {},
            function (data, status) {
                if (status == 'success') {
                    $('#admin-assign-reviewers-div').html(data);
                }
            });
    };


    $('#admin-assign-reviewers-submit').click(function () {
        var fd = new FormData(document.getElementById('admin-assign-reviewers-form'));
        $.ajax({
            url: 'review/assign/',
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                $('#admin-assign-reviewers-div').html(data);
            }
        });
    });

    $('#admin-assign-reviewers-clear').click(function () {
        $('#admin-assign-reviewers-select').val([]);
    });



});
