{% load static %}
// Example navigatorPush.service.js file
  
self.addEventListener('install', function () { self.skipWaiting(); });

self.addEventListener('push', function (event) {
    // Push as simple text
    let title = "";
    let message = event.data.text();
    let tag = "";
    let url = "/";

    try {
        // Push as JSON
        ({title, message, tag, url} = event.data.json());
    } catch (err) {
        // Push really is simple text :o
    }

    const options = {
        body: message,
        icon: "{% static 'res/img/goren_logo.png' %}",
        tag,
        vibrate: [200, 100, 200, 100, 200, 100, 200],
        data: { url }
    }
    self.registration.showNotification(title || "Hallo", options)
        .catch(e => console.error(e));
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

                // no url specified. Don't open browser tab
                if (!event.notification.data.url) { return; }

                // get url
                const url = [
                    event.target.registration.scope.replace(/\/*$/, ""),
                    (event.notification.data.url || "").replace(/^\/*/, ""),
                ].join("/");

                // Check if there is already a window/tab open with the target URL
                const client = windowClients.find(c => c.url === url && 'focus' in c);
                if (client) { return client.focus(); }

                // If not, then open the target URL in a new window/tab.
                if (clients.openWindow) { return clients.openWindow(url); }


                // // open any tab of this scope (which is the full domain in this case)
                // const client = windowClients.find(c => 'focus' in c);
                // return client?.focus();
            })
    );
});