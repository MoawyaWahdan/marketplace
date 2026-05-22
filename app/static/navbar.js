
async function loadNavbar() {
    try {
        const response = await fetch('/static/navbar.html');
        const data = await response.text();
        document.getElementById('nav_placeholder').innerHTML = data;

    } catch (error) {
        console.error('Error loading the navbar:', error);
    }
}