
function getAccessToken() {
    return localStorage.getItem("token");

}

function isLoggedIn() {
    if (getAccessToken()) {
        return true;
    }
    return false;
}
function logout() {

    localStorage.removeItem("token");
    window.location.replace("/static/login.html");

}
