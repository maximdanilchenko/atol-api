
function openMenu() {

    $('#open-menu').toggle('fast');
}


function getUserInfo() {

// getUserInfo
    $.get( "/api/get_user_info", {access_token: localStorage.getItem("atol_access_token")},
        function(response){
        console.log(response)
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
