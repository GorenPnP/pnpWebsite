const endpoint_url = document.querySelector("#endpoint").innerHTML;
const applicationServerKey = JSON.parse(document.querySelector("#app_server_key").innerHTML);

/********* Utils functions *****************/

/** transform base64 into Uint8Array */
function urlBase64ToUint8Array(base64String) {
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

/** Send the subscription data to your server */
function requestPOSTToServer(data) {
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
        .then((res) => document.querySelector("result").textContent = res?.message || "");
}


/** register a user's device for web pushies */
function subscribeUser() {
    if (!('Notification' in window) ||  !('serviceWorker' in navigator)) { return; }

    
    /** subscribe to push service to get connection credentials via PushSubscription*/
    navigator.serviceWorker.ready.then(function (reg) {
        reg.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(applicationServerKey),
        })
        .then(sub => {
            const string_transform = key => btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey(key))));

            // create (or update) PushDevice @ backend
            return requestPOSTToServer({
                p256dh: string_transform('p256dh'),
                auth: string_transform('auth'),
                registration_id: sub.endpoint,
            })

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


/** register WebPush-ServiceWorker */
async function registerServiceWorker() {
    if (!("serviceWorker" in navigator)) { return; }

    try {
        const registration = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
        if (registration.installing) {
            console.log("Service worker installing");
        } else if (registration.waiting) {
            console.log("Service worker installed");
        } else if (registration.active) {
            console.log("Service worker active");
        }
    } catch (error) {
        console.error(`Registration failed with ${error}`);
    }
}

registerServiceWorker();