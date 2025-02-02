// HTMX handlers
document.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-Requested-With'] = 'HTMx';
});

// Notification system
function showNotification(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    document.querySelector('#notifications').appendChild(alert);
}