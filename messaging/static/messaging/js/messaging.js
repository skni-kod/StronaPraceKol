const GetMessageInterval = 1000;

let MessagesArray = [];
let LastMessageId = -1;
let OwnMessageHTML = '';
let ForeignMessageHTML = '';
let CanGetMessage = true;

function SendMessage() {
    $.post(send_message_url,
        {
            review_id: ReviewId,
            message_text: $('#input_message').val(),
        },
        function (data, status) {
            if (status == 'success') {
                GetMessage();
                $('#input_message').val('');
                last_message = 0;
            }
        });
}


function GetMessage() {
    if(CanGetMessage == false)
        return;

    CanGetMessage = false;
    $.post(get_messages_url,
        {
            review_id: ReviewId,
            last_message_id: LastMessageId,
        },
        function (data, status) {
            if (status == 'success') {
                let temporary = Object.values(data);
                let array_len = temporary.length;
                if (array_len > 0) {
                    let last_message = temporary[array_len - 1];
                    LastMessageId = parseInt(last_message.id);
                    MessagesArray = temporary
                    RenderMessages();
                }
            }
            CanGetMessage = true;
        });
}

function RenderMessages() {
    let tmpStr = '';
    let div = document.getElementById('messages_box');
    let scroll = div.scrollHeight - Math.abs(div.scrollTop) === div.clientHeight;

    MessagesArray.forEach(function (item, index, array) {
        if (item.author == username) {
            tmpStr = OwnMessageHTML;
        } else {
            tmpStr = ForeignMessageHTML;
        }
        tmpStr = tmpStr.replace('[author]', item.author_name);
        tmpStr = tmpStr.replace('[text]', item.text);
        tmpStr = tmpStr.replace('[date]', item.date);
        $("#messages_box").append(tmpStr);
    });

     if (MessagesArray.length > 0 && scroll == true) {
        scrollSmoothToBottom('messages_box');
    }
    MessagesArray = [];
}

function scrollSmoothToBottom(id) {
    let div = document.getElementById(id);
     $('#' + id).animate({
         scrollTop: div.scrollHeight - div.clientHeight
     }, 350);
}

$().ready(function () {

    $("#send_message_button").click(function () {
        if ($('#input_message').val().length > 0) {
            SendMessage();
        }
    })

    $.post(render_message_url,
        {
            type: 'own',
        },
        function (data, status) {
            if (status == 'success') {
                OwnMessageHTML = data;
            }
        });

    $.post(render_message_url,
        {
            type: 'foreign',
        },
        function (data, status) {
            if (status == 'success') {
                ForeignMessageHTML = data;
            }
        });


    GetMessage();
    RenderMessages();
    setTimeout(function () {
        scrollSmoothToBottom('messages_box');
    }, 500);

    setInterval(GetMessage, GetMessageInterval);
    setInterval(RenderMessages, GetMessageInterval);
});
