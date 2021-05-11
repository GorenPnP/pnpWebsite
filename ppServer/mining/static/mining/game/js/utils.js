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
