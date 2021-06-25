// event listeners
document.addEventListener('keydown', e => Input.pressedKeyCodes.add(e.keyCode));
document.addEventListener('keyup',   e => {
    Input.pressedKeyCodes.delete(e.keyCode);
    Input.blockedKeyCodes.delete(e.keyCode);
});

window.addEventListener('blur', () => {
    Input.pressedKeyCodes.clear();
    Input.blockedKeyCodes.clear();
});

// CLASS / NAMESPACE
class Input {

    static keyMap = {
        32: 'UP',
        37: 'LEFT',
        38: 'UP',
        39: 'RIGHT',
        40: 'DOWN',
        65: 'LEFT',
        68: 'RIGHT',
        83: 'DOWN',
        87: 'UP',
        16: 'SHIFT',

        // transforms in editor
        82: 'R',
        84: 'T',
        77: 'M',
        16: 'SHIFT'

    }
    static pressedKeyCodes = new Set();
    static blockedKeyCodes = new Set();

    static isDown(keyName) {
        if (!Object.values(Input.keyMap).some(k => k === keyName)) {
            throw Error(`Key '${keyName}' not defined in keyMap`)
        }

        // get related keyCodes to direction / key name
        const keyCodes = [...Input.pressedKeyCodes].filter(keyCode => Input.keyMap[keyCode] === keyName);

        // true if one of them is pressed currently
        return keyCodes.some(keyCode => Input.pressedKeyCodes.has(keyCode)) && keyCodes.every(keyCode => !Input.blockedKeyCodes.has(keyCode));
    }

    static isEmpty() {
        return !Input.pressedKeyCodes.size;
    }

    static blockKey(keyname) {
        const keycode = Object.entries(Input.keyMap).reduce((keycode, [curr_keycode, curr_keyname]) => keyname === curr_keyname ? parseInt(curr_keycode) : keycode, undefined);
        
        if (keycode !== undefined) { Input.blockedKeyCodes.add(keycode); }
    }
}



// FUNCTIONS
function handleInput(dt, player) {

    if (( Input.isDown('DOWN') && !Input.isDown('UP')) ||
    (!Input.isDown('DOWN') &&  Input.isDown('UP'))) {
        
        // move/accelerate y
        if (Input.isDown('DOWN') && !Input.isDown('UP')) { player.speed.y += playerFallAcceleration * dt; }
        
        const now = Date.now();
        if (Input.isDown('UP') && !Input.isDown('DOWN')) {
            // check if on ground
            if (player.speed.y === 0) { player.lastJump = now; }
            
            // start jumping
            if (player.lastJump === now) {
                player.speed.y = -0.1 * dt;
            
            // continue jumping
            } else if (player.lastJump + playerJumpDuration >= now) {
                const jump_time = now - player.lastJump;
                const remaining_time = playerJumpDuration - jump_time;
                const speed_y = -1 * playerJumpDamping * jump_time * remaining_time * dt;
                player.speed.y = Math.min(speed_y, -0.1);
            }
        }
    }
    if (!Input.isDown('DOWN') && player.lastJump + playerJumpDuration < now) player.speed.y = 0;
    
    if (( Input.isDown('LEFT') &&  Input.isDown('RIGHT')) ||
    (!Input.isDown('LEFT') && !Input.isDown('RIGHT'))) {
        
        // slow down x
        player.speed.x *= (1 - playerFriction) * dt;
    } else {
        // move/accelerate x
        const accDiff = playerXAcceleration * dt;
        player.speed.x += Input.isDown('RIGHT') ? accDiff  : (-1 * accDiff);
    }
    
    // apply gravity if player on ground
    if (player.speed.y >= 0) {
        player.speed.y += playerFallAcceleration * dt;
    }
    
    // not faster than max speed
    player.speed.x = Math.min( Math.abs(player.speed.x), playerMaxSpeed.x) * Math.sign(player.speed.x);
    player.speed.y = Math.min( Math.abs(player.speed.y), playerMaxSpeed.y) * Math.sign(player.speed.y);
}