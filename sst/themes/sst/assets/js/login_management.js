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
    if (user == "") {
        while (true) {
            user = prompt("Please enter your name to login:", "");
            pswd = prompt("Please enter your password:", "")
            if (checkNameAndPassword(user, pswd)) {
                setCookie("username", user, 365);
                return;
            }
        }
    }
}


document.addEventListener("DOMContentLoaded", function () {
    checkCookie();
});

function checkNameAndPassword(username, password) {
    let un = CryptoJS.MD5(username).toString();
    let ps = CryptoJS.MD5(password).toString();

    if (user_logins[un] == ps) {
        return true
    } else {
        return false
    }
}