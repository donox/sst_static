function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function checkCookie() {
    var user = getCookie("username");
    if (user != "") {
        $("body").show();
    } else {
        user = prompt("You must log in the first time you visit \n    the new Sunnyside-Times\n\n    Please enter your name:", "");
        if (user != "" && user != null) {
            var un = CryptoJS.MD5(user);
            if (user_logins[un]) {
                pswd = user_logins[un];
                pswdtry = prompt("Please enter your password: \n(temporary reminder: Sunny)", "");
                if (CryptoJS.MD5(pswdtry) == pswd) {
                    setCookie("username", user, 365);
                    $("body").show();
                } else {
                    alert("Unrecognized Password");
                }
            } else {
                alert("Unrecognized User")
            }
        }
    }
}

/* REMOVE WHEN PATHNAME PROBLEM IS FIXED -
   THIS IS NOT USED EXCEPT WHEN EDITING IN DEVELOPER TOOLS
 */
function vrfy() {
    let loc = window.location.href;
    alert(loc);
}

