
(() => {
    let pressedKeys = {};

    function setKey(event, status) {

        const keyMap = {
            32: 'SPACE',
            37: 'LEFT',
            38: 'UP',
            39: 'RIGHT',
            40: 'DOWN'
        }

        const code = event.keyCode;
        const key = keyMap[code] || String.fromCharCode(code);    // Default: Convert ASCII codes to letters

        pressedKeys[key] = status;
    }

    document.addEventListener('keydown', e => {
        setKey(e, true);
    });

    document.addEventListener('keyup', e => {
        setKey(e, false);
    });

    window.addEventListener('blur', () => {
        pressedKeys = {};
    });

    window.input = {
        isDown: (key) => pressedKeys[key.toUpperCase()]
    };
})();