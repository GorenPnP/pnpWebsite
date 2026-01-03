/**
 * Need to register a user-device pair for web-pushies by calling registerForWebPush() somewhere on the site.
 *
 * registers a service worker to handle web-pushies automatically
 */

/********* Constants **************/
const applicationServerKey = JSON.parse(document.querySelector("#PUSH_NOTIFICATION_KEY").innerHTML);
const endpoint_url = JSON.parse(document.querySelector("#PUSH_SUBSCRIBE_USER_ENDPOINT").innerHTML);
const csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;

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
    const requestOptions = {
        method: 'POST',
        headers: new Headers({
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify(data),
    };
  
    return fetch(endpoint_url, requestOptions)
        .then((response) => response.json())
        .then((res) => res?.message === "success");
}


/** register a user's device for web pushies */
async function registerForWebPush(show_alerts=true) {
    if (!('Notification' in window) ||  !('serviceWorker' in navigator)) { return; }

    
    // subscribe to push service
    navigator.serviceWorker.ready
        .then(reg =>
            reg.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(applicationServerKey),
            })
        )
        // get connection credentials via PushSubscription
        .then(sub => {
            const string_transform = key => btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey(key))));

            // create (or update) PushDevice @ backend
            return requestPOSTToServer({
                p256dh: string_transform('p256dh'),
                auth: string_transform('auth'),
                registration_id: sub.endpoint,
            })
        })
        // notify user (probably success)
        .then(success => {
            if (success) {
                show_alerts && alert(`Erfolgreich registriert`);
                console.log("webpush-registration was successful");
            }
            else {
                console.error('Unable to subscribe to push', "Registrierungsdaten falsch oder unvollständig")
                show_alerts && alert(`Ein Fehler ist aufgetreten: Registrierungsdaten sind falsch oder unvollständig`);
            }
        })
        // notify user (error)
        .catch(function (e) {
            if (Notification.permission === 'denied') {
                console.warn('Permission for notifications was denied');
                // alert('Berechtigung für Nachrichten wurde nicht erteilt');
            } else {
                console.error('Unable to subscribe to push', e)
                show_alerts && alert(`Ein Fehler ist aufgetreten: ${e}`);
            }
        });
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