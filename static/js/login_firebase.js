$(document).ready(function(){
    firebase.initializeApp(firebase_config);
    var googleLogin=document.getElementById("googleLogin");
 
    function sendDatatoServer(login_type, uid, email)
    {
        var param = {}
        param['uid'] = uid
        param['login_type'] = login_type
        param['email'] = email
        $.ajax({
            type: 'POST',
            url: "/firebase-save",
            dataType:'json',
            data: param,
            success: function (data, abc) {
                var form = '';
                var redirect = '/firebase-login-redirect';
                $.each( data, function( key, value ) {
                    form += '<input type="hidden" name="'+key+'" value="'+value+'">';
                });
                $('<form action="' + redirect + '" method="POST">' + form + '</form>').appendTo($(document.body)).submit();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log(errorThrown);
            }
        });
    }
    // Login by Google
    googleLogin.onclick=function(){
        firebase.auth().signInWithPopup(new firebase.auth.GoogleAuthProvider()).then(function(response){
            console.log(response)
            /** @type {firebase.auth.OAuthCredential} */
            var credential = response.credential;
            // This gives you a Google Access Token. You can use it to access the Google API.
            var token = credential.accessToken;
            // The signed-in user info.
            var user = response.user;
            sendDatatoServer(1, user.uid, user.email);
        }).catch(function(error){
            console.log(error);
        })
    }
    // Login by facebook
    var facebooklogin=document.getElementById("facebooklogin");
    facebooklogin.onclick=function(){
        firebase.auth().signInWithPopup(new firebase.auth.FacebookAuthProvider()).then(function(response){
            /** @type {firebase.auth.OAuthCredential} */
            var credential = response.credential;
            // This gives you a Google Access Token. You can use it to access the Google API.
            var token = credential.accessToken;
            // The signed-in user info.
            var user = response.user;
            sendDatatoServer(1, user.uid, user.email);
        }).catch(function(error){
            console.log(error);
        })
    }
    // Login by otp
    var get_otp_btn=document.getElementById("get_otp");
    get_otp_btn.onclick=function(){
        var phone_number = document.getElementById("phone_number").value
        if (phone_number == '') {
            $('#error').text('Enter phone number.')
        } else if(!phone_number.match("^\\+[0-9]{12}$")) {
            $('#error').text('Enter correct phone number.')
        } else {
            $('#error').text('')
            document.getElementById("phone_number").disabled = true
            firebase.auth().signInWithPhoneNumber(phone_number, window.recaptchaVerifier) 
            .then(function(confirmationResult) {
                window.confirmationResult = confirmationResult;
                console.log(confirmationResult);
            });
        }
    };
    var submit_btn=document.getElementById("sign-in-button");
    submit_btn.onclick=function(){
        window.confirmationResult.confirm(document.getElementById("verification_code").value)
        .then(function(result) {
            var user = result.user;
            sendDatatoServer(2, user.uid, '')
        }).catch(function(error) {
            if (error.code == 'auth/invalid-verification-code') {
                $('#error').text('Please enter correct otp.')
            }
            console.log(error);
        });
    };
});
