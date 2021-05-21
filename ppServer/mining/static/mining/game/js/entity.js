function renderMarkForBreakables() {
    const breaking = breakables.filter(b => b.breaking);
    for (el of breaking) {
        ctx.fillStyle = `rgba(255, 255, 255, ${(el.lost_rigidity) / el.rigidity})`;
        ctx.fillRect(el.pos.x, el.pos.y, el.pos.w, el.pos.h)
    }


    const in_reach = breakables.filter(b => b.is_in_reach);
    for (el of in_reach) {

        ctx.strokeStyle = 'black';
      
        // Define clickable area
        ctx.beginPath();
        ctx.rect(el.pos.x, el.pos.y, el.pos.w, el.pos.h);
      
        // Draw focus ring, if appropriate
        ctx.stroke();
    }
}


class Entity {
    constructor(id, pos, sprite, layer, material, rotation_angle, mirrored) {
        this.id = id;
        this.pos = pos;
        this.sprite = sprite;
        this.layer = layer;
        this.material = material;
        this.rotation_angle = rotation_angle;
        this.mirrored = mirrored;

        this.rigidity = material?.rigidity;
        this.lost_rigidity = 0;
    }

    updateSprite(dt) {
        this.sprite.update(dt);
    }

    render(ctx) {
        ctx.save();



        //----- canvas pos -------
        let x = this.pos.x;
        let y = this.pos.y;
        let w = this.pos.w;
        let h = this.pos.h;
        
        // rotate
        ctx.translate(x + w/2, y + h/2);
        ctx.rotate(this.rotation_angle/2 * Math.PI);
        
        // mirror with y-axis. Because canvas is rotated previously, choose x-axis if rotation is 90° or 270°
        if (this.mirrored) {
            if (this.rotation_angle % 2) {
                ctx.scale(1, -1);
                h *= -1;
            } else {
                ctx.scale(-1, 1);
                w *= -1;
            }
        }


        // x, y = 0 would be the center of the entity. compute offset for upper left corner
        // in respect to rotation & mirroring
        x = -w/2;
        y = -h/2;

        //----- sprite ------
        this.sprite.updateAnimation();
    
        // translate & scale
        ctx.drawImage(resources.get(this.sprite.url),
            this.sprite.pos.x, this.sprite.pos.y, this.sprite.pos.w, this.sprite.pos.h,
            x, y, w, h);

        ctx.restore();
    }

    static reset(layers) {
        entities = [];
    
        for (const layer of layers) {
            for (const entity of layer.entities) {

                    const rigidity = entity.material.rigidity;
                    const pos = new Rectangle(entity.x, entity.y, entity.w * entity.scale, entity.h * entity.scale);

                    entities.push(new Entity(
                        entity.id,
                        pos,
                        new Sprite(entity.material.icon, new Rectangle(0, 0, entity.w, entity.h)),
                        layer,
                        entity.material,
                        entity.rotation_angle,
                        entity.mirrored
                    ));
                }
        }
        return entities;
    }
}