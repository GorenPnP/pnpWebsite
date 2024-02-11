const endpoint_url = document.querySelector("#endpoint").innerHTML;
const applicationServerKey = JSON.parse(document.querySelector("#app_server_key").innerHTML);

// Utils functions:

function urlBase64ToUint8Array (base64String) {
    var padding = '='.repeat((4 - base64String.length % 4) % 4)
    var base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/')
  
    var rawData = window.atob(base64)
    var outputArray = new Uint8Array(rawData.length)
  
    for (var i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i)
    }
    return outputArray;
}

function subscribeUser() {
    console.log("will register")
    if (!('Notification' in window) ||  !('serviceWorker' in navigator)) { return; }
    console.log("here")

    navigator.serviceWorker.ready.then(function (reg) {
console.log("service worker registration", reg, applicationServerKey, endpoint_url)
        reg.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(applicationServerKey),
        })
        .then(function (sub) {
            var data = {
                p256dh: btoa(
                    String.fromCharCode.apply(null, new Uint8Array(sub.getKey('p256dh')))
                ),
                auth: btoa(
                    String.fromCharCode.apply(null, new Uint8Array(sub.getKey('auth')))
                ),
                registration_id: sub.endpoint,
            };

console.log("send", data)
            requestPOSTToServer(data)
        })
        .catch(function (e) {
            if (Notification.permission === 'denied') {
                console.warn('Permission for notifications was denied')
            } else {
                console.error('Unable to subscribe to push', e)
            }
        })
    })
}
  
// Send the subscription data to your server
function requestPOSTToServer (data) {
    const headers = new Headers();
    headers.set('X-CSRFToken', document.querySelector("[name=csrfmiddlewaretoken]").value);
    headers.set('Content-Type', 'application/json');

    const requestOptions = {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
    };
  
    return fetch(endpoint_url, requestOptions)
        .then((response) => response.json())
        .then((res) => document.querySelector("result").innerHTML = res?.message || "");
}