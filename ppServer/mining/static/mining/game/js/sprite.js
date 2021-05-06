(() => {
    function Sprite(url, pos, size, speed, frames, dir, once) {
        this.pos = pos;
        this.size = size;
        this.speed = typeof speed === 'number' ? speed : 0;
        this.frames = frames;
        this._index = 0;
        this.url = url;
        this.dir = dir || 'horizontal';
        this.once = once;
    };

    Sprite.prototype = {
        update: function(dt) {
            this._index += this.speed*dt;
        },

        render: function(ctx) {
            var frame;

            if (this.speed > 0) {
                var max = this.frames.length;
                var idx = Math.floor(this._index);
                frame = this.frames[idx % max];

                if (this.once && idx >= max) {
                    this.done = true;
                    return;
                }
            }
            else { frame = 0; }


            let [x, y] = this.pos;
            const [w, h] = this.size;

            if (this.dir == 'vertical') { y += frame * h; }
            else { x += frame * w; }

            ctx.drawImage(resources.get(this.url),
                          x, y, w, h,
                          0, 0, w, h);
        }
    };

    window.Sprite = Sprite;
})();