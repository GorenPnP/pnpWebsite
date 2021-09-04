// A cross-browser requestAnimationFrame
// See https://hacks.mozilla.org/2011/08/animating-with-javascript-from-setinterval-to-requestanimationframe/
const requestAnimFrame = (() => {
    return window.requestAnimationFrame    ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame    ||
        window.oRequestAnimationFrame      ||
        window.msRequestAnimationFrame     ||
        function (callback) {
            window.setTimeout(callback, 1000 / 60);
        };
})();

class Vector {
    constructor(x = 0, y = 0) {
        this.x = x;
        this.y = y;
    }
}

class Rectangle {
    constructor(x = 0, y = 0, w = 0, h = 0) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
    }
}


// calc game dimensions
function get_level_dimensions(layers) {
    const max_coords = layers
        .filter(layer => layer.index !== char_layer_index)
        .reduce((entities, layer) => [...entities, ...(layer.entities || [])], [])
        .reduce((max, entity) => {
            max.x = Math.max(max.x, entity.x + entity.w);
            max.y = Math.max(max.y, entity.y + entity.h);
            return max;
        }, new Vector());
    return {x: 0, y : 0, w: max_coords.x, h: max_coords.y};
}

// pie chart (for progress of breaking blocks)
function drawPie(ctx, centerPoint, r, percentFilled) {

    var lastEnd = Math.PI * 3/2;

    var total = 100;
    var sectors = [
        {size: percentFilled, color: 'green'},
        {size: total - percentFilled, color: 'red'}
    ];
    
    for (const sector of sectors) {
      ctx.fillStyle = sector.color;
      ctx.beginPath();
      ctx.moveTo(centerPoint.x, centerPoint.y);
      // Arc Parameters: x, y, radius, startingAngle (radians), endingAngle (radians), antiClockwise (boolean)
      ctx.arc(centerPoint.x, centerPoint.y, r, lastEnd, lastEnd + (Math.PI * 2 * (sector.size / total)), false);
      ctx.lineTo(centerPoint.x, centerPoint.y);
      ctx.fill();
      lastEnd += Math.PI * 2 * (sector.size / total);
    }
}

function get_random_hash(length = 5) {
    return Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, length);
}