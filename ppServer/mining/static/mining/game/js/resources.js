
(() => {
    var resourceCache = {};
    var readyCallbacks = [];

    // Load an image url or an array of image urls
    function load(...urls) {
        urls.forEach(url => _load(url));
    }

    function _load(url) {
        if(resourceCache[url]) {
            return resourceCache[url];
        }

        const img = new Image();
        img.onload = () => {
            resourceCache[url] = img;
            
            if(isReady()) { readyCallbacks.forEach(func => func()); }
        };
        resourceCache[url] = false;
        img.src = url;
    }

    function get(url) {
        return resourceCache[url];
    }

    function isReady() {
        return Object.keys(resourceCache).every(key => resourceCache[key]);
    }

    function onReady(func) {
        readyCallbacks.push(func);
    }

    window.resources = { 
        load,
        get,
        onReady,
        isReady
    };
})();