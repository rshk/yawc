const TOKEN_KEY_NAME = 'api-auth-token';
const LOGIN_PAGE_URL = '/login';
const AFTER_LOGIN_PAGE = '/';


export function doLogin(token, newLocation = AFTER_LOGIN_PAGE) {
    localStorage.setItem(TOKEN_KEY_NAME, token);
    window.location.href = newLocation;
}

export function doLogout() {
    _clearAccessToken();

    // Prevent infinite redirection loop
    if (window.location.pathname !== LOGIN_PAGE_URL) {
        // Redirect to login page; also, ensures all the js-side state
        // is flushed by refreshing the page (as opposed to using
        // pushState).
        window.location.href = LOGIN_PAGE_URL;
    }
}

export function getToken() {
    return localStorage.getItem(TOKEN_KEY_NAME);
}


function _clearAccessToken() {
    localStorage.removeItem(TOKEN_KEY_NAME);
    localStorage.clear();
}
