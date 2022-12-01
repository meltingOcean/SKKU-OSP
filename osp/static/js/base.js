function message_box_builder(msg, is_receive) {
    var msg_date = new Date(msg.send_date);
    var msg_box = $('<div></div>').append(
            $('<div></div>')
            .addClass('chat-text')
            .append(
                $('<div></div>')
                .addClass('chat-text-body')
                .html(msg.body)
            )
            .append(
                $('<div></div>')
                .addClass(msg.read == 'True' ? '' : 'chat-unread')
            )
        ).append(
            $('<div></div>')
            .addClass('chat-date')
            .html(msg_date.toLocaleString(
                'en-US', {
                    month: 'numeric',
                    day: 'numeric',
                    hour: 'numeric',
                    hour12: true,
                    minute: 'numeric'
                }
            ))
        ).addClass('chat-box')
        .addClass(is_receive ? 'receive' : 'send')
        .attr('id', 'message-' + msg.id);
    return msg_box;
}

function LoadMoreMessage() {
    var oppo_id = $($('.opponent-item.selected')[0]).attr('value');
    var oldest_date = $('#chat-view').attr('oldest')
    // $('#chat-view').prepend(
    //     $('<div></div>')
    //     .addClass('spinner-grow')
    //     .addClass('m-auto')
    //     .attr('id', 'chat-load')
    //     .attr('role', 'status')
    //     .append(
    //         $('<span></span>')
    //         .addClass('visually-hidden')
    //         .html('Loading')
    //     )
    // );
    $.ajax({
        url: '/message/chat/' + oppo_id,
        data: {
            'oldest': oldest_date
        },
        method: 'GET',
        dataType: 'JSON'
    }).done(function (data) {
        for (msg of data['data']) {
            is_receive = (msg.sender_id == oppo_id);
            var new_chat_box = message_box_builder(msg, is_receive)
            $('#chat-view').prepend(new_chat_box)
            $('#chat-view').scrollTop($('#chat-view').scrollTop() + new_chat_box.height())
            $('#chat-view').attr('oldest', msg.send_date)
        }
        // $('#chat-load').remove()
    });
}

function RefreshNewMessage() {

}


function refreshChatroom(oppo_id) {
    console.log(oppo_id);
    $('#chat-view').html('')
        .append(
            $('<div></div')
            .addClass('spinner-border')
            .addClass('m-auto')
            .append(
                $('<span></span>')
                .addClass('visually-hidden')
                .html('Loading...')
            )
        );

    $.ajax({
        url: '/message/chat/' + oppo_id,
        method: 'GET',
        dataType: 'JSON'
    }).done(function (data) {
        $('#chat-view').html('');
        $('#chat-input').removeAttr('disabled');
        for (msg of data['data']) {
            is_receive = (msg.sender_id == oppo_id);
            $('#chat-view').prepend(message_box_builder(msg, is_receive))
            $('#chat-view').attr('oldest', msg.send_date)
        }
        $('#chat-view').scrollTop($('#chat-view').height());
    });
}


function select_oppo() {
    $('.opponent-item').each(function () {
        $(this).removeClass('selected');
    });
    var tmp, unread_count;

    unread_count = $(this)[0].children[0].children[2];
    if (unread_count) {
        unread_count.remove();
    }

    $(this).addClass('selected');
    console.dir($(this));
    var oppo_id = $(this).attr('value');

    refreshChatroom(oppo_id);
}

function send_msg(event) {
    event.preventDefault();
    if(!$('#chat-input').val()) return;
    var form_data = new FormData($('#chat-input-form')[0]);
    var oppo_id = $($('.opponent-item.selected')[0]).attr('value');
    var random_id = Math.random().toString(36).substring(2, 11);
    $.ajax({
        url: '/message/chat/' + oppo_id,
        method: 'POST',
        data: form_data,
        dataType: 'JSON',
        processData: false,
        contentType: false,
        beforeSend: function () {
            msg = {
                'id': random_id,
                'body': $('#chat-input').val(),
                'send_date': Date.now(),
                'read': 'False',
            }
            $('#chat-view').append(message_box_builder(msg, false).addClass('pending'));
            $('#chat-view').scrollTop($('#chat-view').height());
            $('#chat-input').val('')
        }
    }).done(function (data) {
        console.log(data);
        if (data.status == 'success') {
            $('#message-' + random_id)
                .removeClass('pending')
                .attr('id', 'message-' + data.msg_id)
        } else {
            alert(data.message);
        }
    }.bind(random_id))
    return false;
}

function msgModalOpen(selected_oppo = 0) {
    $('#message-modal').modal('show');
    $.ajax({
        url: '/message/list/' + selected_oppo,
        method: 'GET',
        dataType: 'HTML'
    }).done(function (data) {
        $('#message-modal-body').html(data);
        $('.opponent-item').click(select_oppo);
        if (selected_oppo != 0) {
            $('#opo-id-' + selected_oppo).click();
        }
        $('#chat-submit').click(send_msg);
        $('#chat-view').scroll(function () {
            if ($(this).scrollTop() === 0) {
                LoadMoreMessage();
            }
            if ($(this).scrollTop() === $(this).height()) {
                RefreshNewMessage();
            }
        });
    })
}

function ApplyTeamModalOpen(isResult=false) {
    if (!$('#ApplyTeamModal').hasClass('ready')) {
        $.ajax({
            url: "/team/api/team-apply-list",
            type: "GET",
            dataType: 'HTML'
        }).done(function (data) {
            $('#ApplyTeamModal').addClass('ready').html(data)
            $('#ApplyTeamModal').modal('show');
            $('.bi-caret-down-fill').click(function () {
                if (this.style.transform == '') {
                    this.style.transform = 'rotate(180deg)';
                } else {
                    this.style.transform = '';
                }
            });
            if(isResult){
                console.log("applyteammodal");
                $("#apply-recv-tab").toggleClass("active");
                $("#apply-send-tab").toggleClass("active");
                $("#apply-recv").toggleClass("show active");
                $("#apply-send").toggleClass("show active");
            }
        })
    } else {
        $('#ApplyTeamModal').modal('show');
    }
}


$().ready(function () {
    $('#message').click(function () {
        msgModalOpen();
    })
    $('#team-apply-list').click(function (){
        ApplyTeamModalOpen();
    });
});

function ReadNotification(type, noti_id, target_id) {
    console.log(type, noti_id, target_id)
    $.ajax({
        url: '/message/noti-read/' + noti_id,
        dataType: 'JSON',
    }).done(function (data) {
        if (data['status'] == 'success') {
            if (type == 'comment' || type == 'articlelike') {
                window.location = '/community/article/' + target_id;
            }
            if(type=='team_invite'){
                window.location = target_id;
            }
            if (type == 'team_apply') {
                ApplyTeamModalOpen();
            }
            if (type == 'team_apply_result') {
                ApplyTeamModalOpen(isResult=true);
            }

            $('#noti-' + noti_id).addClass('read');
        } else {
            alert(data['message']);
        }
    })
}

function consentSignInOpen(){
    $('#consent-signin').modal('show');
    // set is_modal_open in register.html
    is_modal_open = 1;
    if($("#consentSignUp").hasClass("btn-secondary")){
        $("#consentSignUp").removeClass("btn-secondary");
        $("#consentSignUp").addClass("btn-primary");
    }
}

function consentWriteOpen(user){
    console.log("open_consent_write");
    $.ajax({
        url: `/user/${user}/api/consent-write`,
        type: "GET",
        data: null,
        dataType: 'HTML'
    }).done(function (data) {
        $('#consent-wirte').addClass('ready').html(data)
        $('#consent-wirte').modal('show');
    })
}

function submitWriteConsent(e, user){
    e.preventDefault();
    formHTML = $("#write-consent-form")[0]
    
    let form_data = new FormData(formHTML);
    let opt1 = form_data.get('radio-1')
    let opt2 = form_data.get('radio-2')

    if(Number(opt1[0])&Number(opt2[0])){
        $.ajax({
            url: `/user/${user}/api/consent-write`,
            method: 'POST',
            data: form_data,
            dataType: 'JSON',
            processData: false,
            contentType: false,
        }).done(function (data) {
            console.log(data);
            alert(data.msg);
            window.location.reload();
        });
    }else{
        alert("정보 공개에 동의하지 않아 글쓰기 작업이 제한됩니다.");
    }

    return false;
}

function consentUserOpen(user){
    console.log("open_consent_user");
    $.ajax({
        url: `/user/${user}/api/consent-open`,
        type: "GET",
        data: null,
        dataType: 'HTML'
    }).done(function (data) {
        $('#consent-open').addClass('ready').html(data)
        $('#consent-open').modal('show');
    })
}

function submitUserConsent(e, user){
    e.preventDefault();
    formHTML = $("#open-consent-form")[0]
    
    let form_data = new FormData(formHTML);
    let opt1 = form_data.get('radio-1')
    let opt2 = form_data.get('radio-2')

    if(Number(opt1[0])&Number(opt2[0])){
        $.ajax({
            url: `/user/${user}/api/consent-open`,
            method: 'POST',
            data: form_data,
            dataType: 'JSON',
            processData: false,
            contentType: false,
        }).done(function (data) {
            console.log(data);
            alert(data.msg);
            window.location.reload();
        });
    }else{
        alert("정보 공개에 동의하지 않아 유저 추천시스템에 대한 접근이 제한됩니다.");
    }

    return false;
}
