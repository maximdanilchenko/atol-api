
function reloadTree() {
$('.sortable').nestedSortable({
            handle: 'div',
            items: 'li',
            toleranceElement: '> div',
            listType: 'ul',
            disableNesting: 'hub',
            rootID: 'rootHub',
            protectRoot: true,
            delay: 150,
            placeholder: "ui-state-highlight",
            revert: 250,
            opacity: 0.7,
            helper: "clone",
            handle: "a",
            distance: 4,
//            containment: '.sortable',

            update: function (event, ui) {
                group_id = ui.item.parent().parent().children('div').attr('id');
                children_arr = [];
                ui.item.parent().children().each(function (i) {
                    $(this).children('div').attr("data-order_id", i);
                    children_arr[i] = {id: $(this).children('div').attr("id"),
                                       order_id: i,
                                       type: $(this).attr('class')
                                       };
                });
                $("#modal-wait").show();
                $.post( "/api/reorder", {access_token: localStorage.getItem("atol_access_token"),
                                parent_id: group_id,
                                children: children_arr,
                                },
                    function(response){
                        if (response.success == true){
                        console.log("success");
                        }
                        else {

                        };
                    $("#modal-wait").hide();
                    },
                'json' ).fail(function() {
                        $("#modal-wait").hide();
                        });
                },

    });
}

function openMenu() {
    $('#open-menu').toggle('fast');

}


function getUserInfo() {
$("#modal-wait").show();
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
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
        $("#modal-wait").hide();
//        $("#main").css("display","none");
        window.open("signin.html","_self");
  });

}


function getTree() {
$("#modal-wait").show();
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
                                    "<li class='hub'><div id='"+children[i].id+"' data-order_id='"+children[i].order_id+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>"
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
                var s = "<li class='tab'><div id = '"+elem.id+"' data-order_id='"+elem.order_id+"'><i class='fa fa-fw fa-folder' style='display:none;'></i><i class='fa fa-fw fa-folder-open'></i>&nbsp;<a>";
                s = s + elem.name + "</a></div><ul>";
                for (var i = 0; i < children.length; i++) {
                    console.log(children[i].id);
                        if (children[i].type == "hub")
                            s = s + "<li class='hub'><div id='"+children[i].id+"' data-order_id='"+children[i].order_id+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>";
                        else
                        if (children[i].type == "group")
                            s = s + parseTree(children[i]);
                }
                return (s + "</ul></li>");
            }
         $("#modal-wait").hide();
        },
    dataType='JSON' ).fail(function() {
        $("#modal-wait").hide();
  });
}


function addGroup(){
    $("#modal-wait").show();
    order = $('.active-elem').closest('li').children('ul').children('li').last().children('div').attr("data-order_id")+1;
    if (isNaN(order))
        order = 0;
    console.log(order);
    $.post( "/api/create_group", {access_token: localStorage.getItem("atol_access_token"),
                                name: $("#group-form input[name='name']").val(),
                                parent_id: $('.active-elem').attr('id'),
                                order_id: order
                                },
        function(response){
            if (response.success == true){
                $('.active-elem').parent().children("ul").append(
                "<li class='tab'><div id = '"+response.id+"' data-order_id='"+order+"'><i class='fa fa-fw fa-folder' style='display:none;'></i><i class='fa fa-fw fa-folder-open'></i>&nbsp;<a>"+response.name+"</a></div><ul></ul></li>"
                );
                $("#group-form input[name='device_id']").val('');
                $("#group-form input[name='name']").val('');
                $("#modal-group").hide();
                reloadTree();
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });
}


function addHub(){
//access_token, device_id, name, group_id
    $("#modal-wait").show();
    order = $('.active-elem').closest('li').children('ul').children('li').last().children('div').attr("data-order_id")+1;
    if (isNaN(order))
        order = 0;
    $.post( "/api/connect_hub", {access_token: localStorage.getItem("atol_access_token"),
                                device_id: $("#hub-form input[name='device_id']").val(),
                                name: $("#hub-form input[name='name']").val(),
                                group_id: $('.active-elem').attr('id'),
                                order_id: order
                                },
        function(response){
            if (response.success == true){
                $('.active-elem').parent().children("ul").append(
                "<li class='hub'><div id='"+response.id+"' data-order_id='"+order+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+response.name+"</a></div></li>"
                );
                $("#hub-form input[name='device_id']").val('');
                $("#hub-form input[name='name']").val('');
                $("#hub-label").html("Введите идентификатор Хаба");
                $("#modal-hub").hide();
                reloadTree();
                //response.type
            }
            else {
                $("#hub-form input[name='device_id']").val('');
                $("#hub-label").html("Неправильный идентификатор. Введите другой идентификатор Хаба");
            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
                $("#modal-wait").hide();
                $("#hub-form input[name='device_id']").val('');
                $("#hub-label").html("Ошибка. Введите другой идентификатор Хаба");
            });
}


function deleteGroup(){
$("#modal-wait").show();
    $.post( "/api/remove_group", {access_token: localStorage.getItem("atol_access_token"),
                                group_id: $('.active-elem').attr('id')
                                },
        function(response){
            if (response.success == true){
                el = $('.active-elem').closest('ul').parent().children('div');
                $('.active-elem').closest('li').remove();
                el.addClass("active-elem");
                $("#modal-delete-group").hide();
                if (el.hasClass('tab-root')) {
                    $('#panel-group').show("fast");
                    $('#panel-hub').show("fast");
                    $('#panel-rename-group').show("fast");
                    $('#panel-rename-hub').hide("fast");
                    $('#panel-delete-hub').hide("fast");
                    $('#panel-delete-group').hide("fast");
                }
                else{
                    $('#panel-group').show();
                    $('#panel-hub').show();
                    $('#panel-rename-group').show();
                    $('#panel-rename-hub').hide();
                    $('#panel-delete-hub').hide();
                    $('#panel-delete-group').show();
                }
                $('#dashboard-hub').hide();
                $('#dashboard-group').show();
                $('#dashboard-group').html(el.children("a").html());
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });
}


function deleteHub(){
    $("#modal-wait").show();
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
                $('#panel-group').show();
                $('#panel-hub').show();
                $('#panel-rename-group').show();
                $('#panel-rename-hub').hide();
                $('#panel-delete-hub').hide();
                $('#panel-delete-group').show();

                $('#dashboard-group').show();
                $('#dashboard-group').html(el.children("a").html());
                $('#dashboard-hub').hide();
                //response.type
                $("#modal-wait").hide();
            }
            else {

            };
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });
}


function renameGroup(){
    $("#modal-wait").show();
    $.post( "/api/rename_group", {access_token: localStorage.getItem("atol_access_token"),
                                group_id: $('.active-elem').attr('id'),
                                name: $("#rename-form-group input[name='name']").val(),
                                },
        function(response){
            if (response.success == true){
                $('.active-elem > a').html(response.name);
                $("#rename-form-group input[name='name']").val('');
                $("#modal-rename-group").hide();
                reloadTree();
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });

}


function renameHub(){
    $("#modal-wait").show();
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
                reloadTree();
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });

}
