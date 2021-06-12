// CLASS
class Player extends Entity {
    constructor(pos) {
        super(-1, pos, new Sprite('/static/res/img/mining/char_skin_front.png', new Rectangle(0, 0, tile_size, tile_size)), 0);

        this.speed = new Vector(0, 0);
        this.lastJump = Date.now();

        this.spriteMap = {
            UP: new Sprite('/static/res/img/mining/char_skin_front.png', new Rectangle(0, 0, tile_size, tile_size)),
            DOWN: new Sprite('/static/res/img/mining/char_skin_back.png', new Rectangle(0, 0, tile_size, tile_size)),
            LEFT: new Sprite('/static/res/img/mining/char_skin_left.png', new Rectangle(0, 0, tile_size, tile_size)),
            RIGHT: new Sprite('/static/res/img/mining/char_skin_right.png', new Rectangle(0, 0, tile_size, tile_size))
        };
    }

    resolveCollisions() {
        const playerXRect = new Rectangle(this.pos.x + Math.round(this.speed.x), this.pos.y, this.pos.w, this.pos.h);
        const playerYRect = new Rectangle(this.pos.x, this.pos.y + Math.round(this.speed.y), this.pos.w, this.pos.h);
        
        // resolve collisions
        for(const collidable of collidables) {
    
            // collide in x
            if (boxCollides(collidable.pos, playerXRect)) {
                while (boxCollides(collidable.pos, playerXRect) && this.speed.x) {
                    playerXRect.x -= Math.sign(this.speed.x);
                }
                this.speed.x = 0;
            }
            
            // collide in y
            if (boxCollides(collidable.pos, playerYRect)) {
                while (boxCollides(collidable.pos, playerYRect) && this.speed.y) {
                    playerYRect.y -= Math.sign(this.speed.y);
                }
                this.speed.y = 0;
            }
    
        }
        this.pos.x = playerXRect.x;
        this.pos.y = playerYRect.y;
    }

    stayInBounds(bounds) {
        // Check bounds
        const max_right = bounds.w - this.pos.w - Canvas.canvas.getBoundingClientRect().x;
        const max_down = bounds.h - this.pos.h - Canvas.canvas.getBoundingClientRect().y;

        this.pos.x = Math.max(0, Math.min(this.pos.x, max_right));
        this.pos.y = Math.max(0, Math.min(this.pos.y, max_down));

        // enable jumping from furthest bottom
        if (this.pos.y === max_down && this.speed.y > 0) { this.speed.y = 0; }
    }

    render(ctx) {
        const limit = 0.25;
        const speed_x = Math.abs(this.speed.x) < limit ? 0 : this.speed.x;
        const speed_y = Math.abs(this.speed.y) < limit ? 0 : this.speed.y;
    
        // look in x
        if (Math.abs(speed_x) > Math.abs(speed_y)) {
            this.sprite = speed_x > 0 ? this.spriteMap.RIGHT : this.spriteMap.LEFT;
        }
        // look in y
        else {
            this.sprite = speed_y > 0 ? this.spriteMap.DOWN : this.spriteMap.UP;
        }

        super.render(ctx);
    }

    static reset(player_layer) {
        // random position
        const pos = player_layer.entities[Math.floor(Math.random() * player_layer.entities.length)];
        const playerPos = new Rectangle(pos.x, pos.y, tile_size, tile_size);
        return new Player(playerPos);
    }
}
