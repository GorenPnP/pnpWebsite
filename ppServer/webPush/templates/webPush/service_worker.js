{% load static %}
// Example navigatorPush.service.js file
  
self.addEventListener('install', function () { self.skipWaiting(); });

self.addEventListener('push', function (event) {
    // Push as simple text
    let title = "";
    let message = event.data.text();
    let tag = "";

    try {
        // Push as JSON
        ({title, message, tag} = event.data.json());
    } catch (err) {
        // Push really is simple text :o
    }

    const options = {
        body: message,
        icon: "{% static 'res/img/goren_logo.png' %}",
        tag,
        vibrate: [200, 100, 200, 100, 200, 100, 200]
    }
    self.registration.showNotification(title || "Hallo", options)
        .catch(e => console.error(e));

    // Optional: Communicating with our js application. Send a signal
    self.clients.matchAll({includeUncontrolled: true, type: 'window'})
        .then(clients => clients.forEach(client =>
            client.postMessage({
                data: tag,
                data_title: title,
                data_body: message
            })
        ));
});
  
// Optional: Added to that the browser opens when you click on the notification push web.
self.addEventListener('notificationclick', (event) => {

    // Android doesn't close the notification when you click it
    // See http://crbug.com/463146
    event.notification.close();

    // Check if there's already a tab open with this URL.
    // If yes: focus on the tab.
    // If no: open a tab with the URL.
    event.waitUntil(
        clients.matchAll({type: 'window', includeUncontrolled: true})
            .then(windowClients => {
                const client = windowClients.find(c => 'focus' in c);
                return client?.focus();
            })
    );
});