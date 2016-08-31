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
                    $('#dashboard-group').html(data.name);
                    localStorage.setItem("rootId", data.id);
                    var children = data.children.sort(function(a, b) {
                      return a.order_id - b.order_id  ||  a.name.localeCompare(b.name);
                    });
                    for (var i = 0; i < children.length; i++) {
                        console.log(children[i].id);
                            if (children[i].type == "hub")
                                $("#rootHub > ul").append(
                                    "<li id='"+children[i].id+"'><div class='hub'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>"
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
                var s = "<li id = '"+elem.id+"'><div class='tab'><i class='fa fa-fw fa-folder-o' style='display:none;'></i><i class='fa fa-fw fa-folder-open-o'></i>&nbsp;<a>";
                s = s + elem.name + "</a></div><ul>";
                for (var i = 0; i < children.length; i++) {
                    console.log(children[i].id);
                        if (children[i].type == "hub")
                            s = s + "<li id='"+children[i].id+"'><div class='hub'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>";
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


function addGroup(){}

function addHub(){}

function addGroup(){}

function renameHub(){}

function renameGroup(){}
