var api_url = "http://10.104.154.107:8088";
var token = "";
var current_user = "";

// login handling
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
            //$("#mainContentDiv").html(JSON.stringify(result));
            
            
            // svuoto campi form username e password
            $('#username').val('');
            $('#password').val('');
            openSession(result.auth_token, current_user);
        },
        error: function(msg) {
            $("#loginError").html('Login error');
            setTimeout(function() { $("#loginError").html(''); }, 3000);
        }
    });
}

function openSession(t, u) {
	token = t;
	current_user = u;
    sessionStorage.setItem('token', token);
    sessionStorage.setItem('current_user', current_user);
	$('#favorites').show('slow');
	$('#loginDiv').hide('slow');
	$('#welcomeDiv').show('slow');
	getAllFavorites( );
}

function logout( ) {
	alert("Successfully logged out!");
	closeSession();
}

function closeSession( ) {
	token = "";
    current_user = "";
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('current_user');
    myFavorites = new Array();
    $('#favorites').hide('slow');
	$('#loginDiv').show('slow');
	$('#welcomeDiv').hide('slow');
    getMovieList();
}

function checkSession( ) {
    if (sessionStorage.getItem('token')) {
        openSession(sessionStorage.getItem('token'), sessionStorage.getItem('current_user'));
    }
}

// movie db handling
var maxResults = 20; //number of movies expected from the backend

function getMovieList(start) {
    var url = api_url + "/getlist";
    if (start) url += "?start=" + start;

    var myTemplate = $.templates("#mainDivTmpl");
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
        	//$("#mainTitleDiv").html("<b>Best Movies</b>");
        	if (!start) {
        		$("#mainContentDiv").empty();
        		result.title = "Best Movies";
        	}
        	//se result.movies ha dim maxResults: result.showmore = true; e result.start = start ? start+maxResults : maxResults;
        	if (result.movies.length === maxResults) {
        		result.showmore = true;
        		result.start = start ? start+maxResults : maxResults;
        	}
        	if (start) $('#showMoreButton'+start).hide();
        	//il pulsante showmore chiama getMovieList(result.start)
        	//la funzione deve fare append in maincontentdiv se e solo se start e' valorizzato
        	//se result.movies ha dim < maxResults nascondo pulsante (nel senso di display none)

        	//idea, da capire: metto pulsante nel template con id "showMoreButton"+result.start
        	//quando chiamo la getMovieList con start valorizzato nascondo il pulsante corrispondente
            $("#mainContentDiv").append(myTemplate.render(result));
        },
        error: function(msg) {
            console.log(JSON.stringify(msg));
        }
    })
}

function infoMovie(id) {
    //$("#mainContentDiv").html(id);
    //console.log('infoMovie called');
    var url = api_url + "/movie/" + id;
    //console.log(id)
    var myTemplate = $.templates("#movieInfoTmpl");
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
        	if (token) {
        		if (myFavorites.includes(result.info.id)) {
	        		result.info.isfavorite = "delete";
	        	}
	        	else {
	        		result.info.isfavorite = "add";
	        	}
        	}
        	
            $("#mainContentDiv").html(myTemplate.render(result.info));
        },
        error: function(msg) {
            $("#mainContentDiv").html('error' + JSON.stringify(msg));
        }
    });

}

function searchMovie( ) {
    var title = $('#searchMovieInput').val();
    var url = api_url + "/search?title=" + encodeURI(title);
    //console.log(url);
    var myTemplate = $.templates("#mainDivTmpl");
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
            // $("#mainContentDiv").html(JSON.stringify(result));
            result.title = "Search results";
            $("#mainContentDiv").html(myTemplate.render(result));
        },
        error: function() {
            $("#mainContentDiv").html('error');
        }
    });

}

function getMoviesByIds(idlist) {
	// idlist deve essere un array javascript di id, es. quello dei favoriti
	//chiamo al solito il backend con questo elenco e mostro risultati
	var url = api_url + "/search?id=" + idlist.join();
	var myTemplate = $.templates("#mainDivTmpl");
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
           // $("#mainContentDiv").html(JSON.stringify(result));
            result.title = "My favorites";
            $("#mainContentDiv").html(myTemplate.render(result));
        },
        error: function() {
            $("#mainContentDiv").html('error');
        }
    });
}

function getPoster(movieId) {
    var url = api_url + "/function/getposters?movieid=" + movieId;
    //console.log(url);
    $.ajax({
        type: "GET",
        url: url,
        success: function(result){
            document.getElementById("poster"+movieId).src = result.url;
        },
        error: function(msg) {
            //$("#mainContentDiv").html('error');
            console.log(msg);
        }
    });
}

//favorites handling
var myFavorites = new Array( );

function getAllFavorites( ) {
	//da chiamare (forse) al login per precaricare array con i preferiti
	//da chiamare anche ogni volta che aggiungo/tolgo un preferito

	if (!token) return;

	var url = api_url + "/getfavorites";    
    $.ajax({
        type: "GET",
        url: url,
        beforeSend: function(request) {
			request.setRequestHeader("Authorization", "Bearer " + token);
		},
        success: function(result){
        	// valorizzo myFavorites (array)
        	myFavorites = result;
        	console.log(JSON.stringify(result));
        },
        error: function(msg) {
            console.log('error: ' + msg);
        }
    });

}

function showFavorites( ) {
	//chiamata dal link della pagina "i miei preferiti"
	//legge elenco myFavorites, se vuoto mostra direttamente scritta no preferiti
	//altrimenti chiamo la getMoviesByIds
    if (!token) return;

	if (typeof myFavorites !== 'undefined' && myFavorites.length > 0) {
    // the array is defined and has at least one element
        getMoviesByIds(myFavorites);
    } else {
    	$("#mainContentDiv").html("Your list is empty!");
    }
}

function toggleFavorite(movieid) {
	if (!token) return;

	//if non e' preferito:
	if (!myFavorites.includes(movieid)) {
        if (myFavorites.length > 5) {
        	alert("You have already chosen 5 favorites!");
        	return;
        }
        else {
        	var url = api_url + "/addfavorite?movieid=" + movieid;    
		    $.ajax({
		        type: "GET",
		        url: url,
		        beforeSend: function(request) {
					request.setRequestHeader("Authorization", "Bearer " + token);
				},
		        success: function(result){
		        	myFavorites.push(movieid);
		        	$("#favoriteIcon").attr("src", "images/deletefavorite.png");
		        },
		        error: function(msg) {
		            console.log('error: ' + msg);
		        }
		    });
        }
	}

    //film gia' tra i preferiti -> da rimuovere
	else {
       	var url = api_url + "/deletefavorite?movieid=" + movieid;    
	    $.ajax({
	        type: "GET",
	        url: url,
	        beforeSend: function(request) {
				request.setRequestHeader("Authorization", "Bearer " + token);
			},
	        success: function(result){
	        	//myFavorites.splice(myFavorites.indexOf(movieid,1));
                myFavorites = $.grep(myFavorites, function(value) { return value != movieid; });
	        	$("#favoriteIcon").attr("src", "images/addfavorite.png");
	        },
	        error: function(msg) {
	            console.log('error: ' + msg);
	        }
	    });
    }
}
