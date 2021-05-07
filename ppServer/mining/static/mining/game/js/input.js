
(() => {
    const keyMap = {
        32: 'UP',
        37: 'LEFT',
        38: 'UP',
        39: 'RIGHT',
        40: 'DOWN',
        65: 'LEFT',
        68: 'RIGHT',
        83: 'DOWN',
        87: 'UP',
    }

    let pressedKeyCodes = new Set();

    function setKey(keyCode, is_pressed) {
        is_pressed ? pressedKeyCodes.add(keyCode) : pressedKeyCodes.delete(keyCode);
    }

    document.addEventListener('keydown', e => {
        setKey(e.keyCode, true);
    });

    document.addEventListener('keyup', e => {
        setKey(e.keyCode, false);
    });

    window.addEventListener('blur', () => {
        pressedKeyCodes.clear();
    });

    window.input = {
        isDown: (keyName) => {
            if (!Object.values(keyMap).some(k => k === keyName)) {
                throw Error(`Key '${keyName}' not defined in keyMap`)
            }

            // get related keyCodes to direction / key name
            const keyCodes = [...pressedKeyCodes].filter(keyCode => keyMap[keyCode] === keyName);

            // true if one of them is pressed currently
            return keyCodes.some(keyCode => pressedKeyCodes.has(keyCode));
        }
    };
})();