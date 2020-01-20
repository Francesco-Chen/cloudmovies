var api_url = "http://10.111.118.79:8088";
var token = "";
var current_user = "";

function getMovieList(start) {
    var url = api_url + "/getlist";
    if (start) url += "?start=" + start;

    var myTemplate = $.templates("#listMovieTmpl");
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
            $("#mainContentDiv").html(myTemplate.render(result.movies));
        },
        error: function() {
            $("#mainContentDiv").html('error');
        }
    })
}

function infoMovie(id) {
    //$("#mainContentDiv").html(id);
    console.log('infoMovie called');
    var url = api_url + "/movie/" + id;
    console.log(id)
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
            $("#mainContentDiv").html(JSON.stringify(result[0]));
        },
        error: function(msg) {
            $("#mainContentDiv").html('error' + JSON.stringify(msg));
        }
    })

}


function login( ) {
    var username = $('#username').val();
    var password = $('#password').val();

    var url = api_url + "/auth/login"
    data = "user=" + username + "&pwd=" + password;
    //console.log(data)
    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(result){
            $("#mainContentDiv").html(JSON.stringify(result));
            token = result.auth_token;
            current_user = username;
        },
        error: function(msg) {
            $("#loginError").html('Login error');
            setTimeout(function() { $("#loginError").html(''); }, 3000);
        }
    });
}


function searchMovie( ) {
    var title = $('#searchMovieInput').val();
    var url = api_url + "/search?title=" + encodeURI(title);
    console.log(url);
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
            $("#mainContentDiv").html(JSON.stringify(result));
        },
        error: function() {
            $("#mainContentDiv").html('error');
        }
    })

}

function getPoster(movieId) {
    var url = api_url + "/function/getposters?movieid=" + movieId;
    console.log(url);
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
            document.getElementById("poster"+movieId).src = result.url;
        },
        error: function() {
            $("#mainContentDiv").html('error');
        }
    })
}
