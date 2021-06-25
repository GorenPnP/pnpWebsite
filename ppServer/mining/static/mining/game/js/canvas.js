// CLASS
class Canvas {
    static canvas;
    static isHitting = false;
    static lastHit = Date.now();
    static lastPoint;
    static clicked_breakable;
    static hittingTimer;

    static renderOffset = new Vector();
    
    static reset() {
        Canvas.canvas = document.createElement("canvas");
        
        const main_container = document.querySelector(".main-container");
        main_container.innerHTML = null;
        main_container.appendChild(Canvas.canvas);
        Canvas.resize();

        Canvas.resetEvents();
        
        return Canvas.canvas;
    }

    static resetEvents() {
        window.addEventListener("resize", Canvas.resize);
    
        // Add the event listeners for mousedown, mousemove, and mouseup
        Canvas.canvas.addEventListener('mousedown', e => {
            Canvas.isHitting = true;
            const point = new Vector(e.clientX - Canvas.renderOffset.x, e.clientY - Canvas.renderOffset.y);
            hitBreakable(point);

            Canvas.hittingTimer = setInterval(() => hitBreakable(Canvas.lastPoint), miningCooldown / 2);
        });
        
        Canvas.canvas.addEventListener('mousemove', e => {
            if (Canvas.isHitting) {
                const point = new Vector(e.clientX - Canvas.renderOffset.x, e.clientY - Canvas.renderOffset.y);
                console.log(point)
                hitBreakable(point);
            }
        });
        
        window.addEventListener('mouseup', () => {
            Canvas.isHitting = false;
            clearInterval(Canvas.hittingTimer);
        });
        window.addEventListener('blur', () => {
            Canvas.isHitting = false;
            clearInterval(Canvas.hittingTimer);
        });
    }
    
    static resize() {
        const main_container = document.querySelector(".main-container");
        
        Canvas.canvas.width = main_container.offsetWidth;
        Canvas.canvas.height = main_container.offsetHeight;
        Canvas.canvas.style.width = `${main_container.offsetWidth}px`;
        Canvas.canvas.style.height = `${main_container.offsetHeight}px`;
    }

    static setRenderOffset() {
        Canvas.renderOffset = new Vector(
            Math.floor(-1* (player.pos.x - (canvas.width - player.pos.w) / 2)),
            Math.floor(-1* (player.pos.y - (canvas.height - player.pos.h) / 2))
        );
    }
}


// EVENT LISTENERS

/**
 * 
 * @param {x: number, y: number} clicked_point determined by (mouseEvent).clientX, (mouseEvent).clientY & renderOffset
 * @returns 
 */
function hitBreakable(clicked_point) {
    
    if (Canvas.lastHit + miningCooldown >= Date.now()) { return; }
    
    Canvas.lastHit = Date.now();
    
    Canvas.lastPoint = clicked_point;

    Canvas.clicked_breakable = breakables
        .filter(b => b.is_in_reach)
        .filter(b => {
            return b.pos.x <= clicked_point.x && b.pos.x + b.pos.w >= clicked_point.x &&
                b.pos.y <= clicked_point.y && b.pos.y + b.pos.h >= clicked_point.y
        })
        .reduce((acc, b) => acc.layer.index < b.layer.index ? b : acc, {layer: {index: Number.NEGATIVE_INFINITY}});

    breakables.forEach(b => {
        b.breaking = b === Canvas.clicked_breakable;
        b.lost_rigidity = b.breaking ? b.lost_rigidity + 1 : 0;
    });
}
