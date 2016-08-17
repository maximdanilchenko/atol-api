//JS methods for Sign Page


// Tabs
function openLogTab(tabName) {
    $(".login").css("display","none");
    $(".snbtn").toggleClass("w3-theme-dark");
    $(".snbtn").toggleClass("w3-theme");
    $("#"+tabName).css("display","block");
}


// SignIn
function signIn() {
    $.post( "/api/signin", $("#signin-form").serialize(),
        function(response){
            if (response.success == true){
                window.open("index.html","_self");
            };
        },
    'json' ).fail(function() {
        $("#main").css("display","none");
        $("#error").css("display","block");
  });
}


// SignUp
function signUp() {
    pass = $("#signup-form input[name='password']");
    c_pass = $("#signup-form input[name='conf_password']");
    if (pass.val() == c_pass.val()){
        $.post( "api/signup", $("#signup-form").serialize(),
            function(response){
                if (response.success == true){
                    $("#main").css("display","none");
                    $("#final").css("display","block");
                };
            },
        'json' ).fail(function() {
            $("#main").css("display","none");
            $("#error").css("display","block");
      });
    }
    else{
      c_pass.val('');
    }
}

//Reload
function back() {
    location.reload();
}

function rec_pass(){
    $("#main").css("display","none");
    $("#recovery").css("display","block");
}

function recovery(){
    pass = $("#recovery-form input[name='password']");
    c_pass = $("#recovery-form input[name='conf_password']");
    if (pass.val() == c_pass.val()){
        $.post( "api/signup", $("#recovery-form").serialize(),
            function(response){
                if (response.success == true){
                    $("#recovery").css("display","none");
                    $("#final_rec").css("display","block");
                };
            },
        'json' ).fail(function() {
            $("#recovery").css("display","none");
            $("#error").css("display","block");
      });
    }
    else{
      c_pass.val('');
    }
}
