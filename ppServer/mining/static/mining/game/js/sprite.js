class Sprite {
    constructor (url, pos, speed = 0, frames = [0], dir = 'horizontal', once = false) {
        this.url = url;
        this.pos = pos;

        this.speed = speed;
        this.frames = frames;
        this.dir = dir;
        this.once = once;
        
        this._index = 0;
        this.done = false;
    }

    update(dt) {
        this._index += this.speed * dt;
    }

    render(ctx) {
        var frame;

        if (this.speed <= 0) { frame = 0; }
        else {
            var max = this.frames.length;
            var idx = Math.floor(this._index);
            frame = this.frames[idx % max];

            if (this.once && idx >= max) {
                this.done = true;
                return;
            }
        }

        if (this.dir == 'vertical') { this.pos.y += frame * this.pos.h; }
        else { this.pos.x += frame * this.pos.w; }

        ctx.drawImage(resources.get(this.url),
                    this.pos.x, this.pos.y, this.pos.w, this.pos.h,
                    0,          0,          this.pos.w, this.pos.h);
    }
}
