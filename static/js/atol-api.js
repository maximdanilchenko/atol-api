
function reloadTree() {
$('.sortable').nestedSortable({
            handle: 'div',
            items: 'li',
            toleranceElement: '> div',
            listType: 'ul',
            disableNesting: 'hub',
            rootID: 'rootHub',
            protectRoot: true
    });
}

function openMenu() {
    $('#open-menu').toggle('fast');
}


function getUserInfo() {

// getUserInfo
    $.get( "/api/get_user_info", {access_token: localStorage.getItem("atol_access_token")},
        function(response){
            if (response.success == true){
                $('.body-title').append(response.name);
                //response.type
            }
            else {
            window.open("signin.html","_self");
            };
        },
    'json' ).fail(function() {
//        $("#main").css("display","none");
        window.open("signin.html","_self");
  });

}


function getTree() {
    $.post( "/api/get_tree", {access_token: localStorage.getItem("atol_access_token")},
        function(response){
            if (response.success == true){
                    data = response.tree;
                    $("#rootHub > div > a").html(data.name);
                    $("#rootHub > div").attr("id",data.id);
                    $('#dashboard-group').html(data.name);
                    localStorage.setItem("rootId", data.id);
                    var children = data.children.sort(function(a, b) {
                      return a.order_id - b.order_id  ||  a.name.localeCompare(b.name);
                    });
                    for (var i = 0; i < children.length; i++) {
                        console.log(children[i].id);
                            if (children[i].type == "hub")
                                $("#rootHub > ul").append(
                                    "<li class='hub'><div id='"+children[i].id+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>"
                                );
                            else
                            if (children[i].type == "group")
                                $("#rootHub > ul").append(
                                    parseTree(children[i])
                                );
                    }
            }
            else {
            };
            function parseTree(elem){
                var children = elem.children.sort(function(a, b) {
                return a.order_id - b.order_id  ||  a.name.localeCompare(b.name);
                });
                var s = "<li class='tab'><div id = '"+elem.id+"'><i class='fa fa-fw fa-folder' style='display:none;'></i><i class='fa fa-fw fa-folder-open'></i>&nbsp;<a>";
                s = s + elem.name + "</a></div><ul>";
                for (var i = 0; i < children.length; i++) {
                    console.log(children[i].id);
                        if (children[i].type == "hub")
                            s = s + "<li class='hub'><div id='"+children[i].id+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>";
                        else
                        if (children[i].type == "group")
                            s = s + parseTree(children[i]);
                }
                return (s + "</ul></li>");
            }
        },
    dataType='JSON' ).fail(function() {
  });
}


function addGroup(){
    $.post( "/api/create_group", {access_token: localStorage.getItem("atol_access_token"),
                                name: $("#group-form input[name='name']").val(),
                                parent_id: $('.active-elem').attr('id')
                                },
        function(response){
            if (response.success == true){
                $('.active-elem').parent().children("ul").append(
                "<li class='tab'><div id = '"+response.id+"'><i class='fa fa-fw fa-folder' style='display:none;'></i><i class='fa fa-fw fa-folder-open'></i>&nbsp;<a>"+response.name+"</a></div><ul></ul></li>"
                );
                $("#group-form input[name='device_id']").val('');
                $("#group-form input[name='name']").val('');
                $("#modal-group").hide();
                //response.type
            }
            else {

            };
        },
    'json' ).fail(function() {

            });

    reloadTree();
}

function addHub(){
//access_token, device_id, name, group_id
    $.post( "/api/connect_hub", {access_token: localStorage.getItem("atol_access_token"),
                                device_id: $("#hub-form input[name='device_id']").val(),
                                name: $("#hub-form input[name='name']").val(),
                                group_id: $('.active-elem').attr('id')
                                },
        function(response){
            if (response.success == true){
                $('.active-elem').parent().children("ul").append(
                "<li class='hub'><div id='"+response.id+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+response.name+"</a></div></li>"
                );
                $("#hub-form input[name='device_id']").val('');
                $("#hub-form input[name='name']").val('');
                $("#hub-label").html("Введите идентификатор Хаба");
                $("#modal-hub").hide();
                //response.type
            }
            else {
                $("#hub-form input[name='device_id']").val('');
                $("#hub-label").html("Неправильный идентификатор. Введите другой идентификатор Хаба");
            };
        },
    'json' ).fail(function() {
                $("#hub-form input[name='device_id']").val('');
                $("#hub-label").html("Ошибка. Введите другой идентификатор Хаба");
            });

    reloadTree();
}

function deleteGroup(){
    $.post( "/api/remove_group", {access_token: localStorage.getItem("atol_access_token"),
                                group_id: $('.active-elem').attr('id')
                                },
        function(response){
            if (response.success == true){
                el = $('.active-elem').closest('ul').parent().children('div');
                $('.active-elem').closest('li').remove();
                el.addClass("active-elem");
                $("#modal-delete-group").hide();
                $('#panel-folder').show();
                $('#panel-hub').show();
                $('#panel-rename-group').show();
                $('#panel-rename-hub').hide();
                $('#panel-delete-hub').hide();
                $('#panel-delete-group').show();

                $('#dashboard-group').show();
                $('#dashboard-group').html(el.children("a").html());
                $('#dashboard-hub').hide();
                //response.type
            }
            else {

            };
        },
    'json' ).fail(function() {

            });
}

function deleteHub(){
    $.post( "/api/disconnect_hub", {access_token: localStorage.getItem("atol_access_token"),
                                hub_id: $('.active-elem').attr('id'),
                                group_id: $('.active-elem').closest('ul').parent().children('div').attr('id')
                                },
        function(response){
            if (response.success == true){
                el = $('.active-elem').closest('ul').parent().children('div');
                $('.active-elem').closest('li').remove();
                el.addClass("active-elem");
                $("#modal-delete-hub").hide();
                $('#panel-folder').show();
                $('#panel-hub').show();
                $('#panel-rename-group').show();
                $('#panel-rename-hub').hide();
                $('#panel-delete-hub').hide();
                $('#panel-delete-group').show();

                $('#dashboard-group').show();
                $('#dashboard-group').html(el.children("a").html());
                $('#dashboard-hub').hide();
                //response.type
            }
            else {

            };
        },
    'json' ).fail(function() {

            });
}

function renameGroup(){
    $.post( "/api/rename_group", {access_token: localStorage.getItem("atol_access_token"),
                                group_id: $('.active-elem').attr('id'),
                                name: $("#rename-form-group input[name='name']").val(),
                                },
        function(response){
            if (response.success == true){
                $('.active-elem > a').html(response.name);
                $("#rename-form-group input[name='name']").val('');
                $("#modal-rename-group").hide();
                //response.type
            }
            else {

            };
        },
    'json' ).fail(function() {

            });

    reloadTree();
}

function renameHub(){
    $.post( "/api/rename_hub", {access_token: localStorage.getItem("atol_access_token"),
                                hub_id: $('.active-elem').attr('id'),
                                name: $("#rename-form-hub input[name='name']").val(),
                                group_id: $('.active-elem').closest('ul').parent().children('div').attr('id')
                                },
        function(response){
            if (response.success == true){
                $('.active-elem > a').html(response.name);
                $("#rename-form-hub input[name='name']").val('');
                $("#modal-rename-hub").hide();
                //response.type
            }
            else {

            };
        },
    'json' ).fail(function() {

            });

    reloadTree();
}
