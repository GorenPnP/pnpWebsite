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
    constructor(pos, sprite, layer, material) {
        this.pos = pos;
        this.sprite = sprite;
        this.layer = layer;

        this.rigidity = material?.rigidity;
        this.lost_rigidity = 0;
    }

    updateSprite(dt) {
        this.sprite.update(dt);
    }

    render(ctx) {
        ctx.save();
        ctx.translate(this.pos.x, this.pos.y);
        this.sprite.render(ctx);
        ctx.restore();
    }

    static reset(layers, materials) {
        entities = [];
    
        for (const layer of layers) {
            const field = layer.field;
    
            for (let y = 0; y < field.length; y++) {
                for (let x = 0; x < field[y].length; x++) {
                    const material_id = field[y][x];
    
                    if (!material_id) { continue; }

                    const material = materials.find(material => material.id === material_id)
                    const sprite_url = material.icon;
                    const rigidity = material.rigidity;
                    const pos = new Rectangle(x * tile_size, y * tile_size, tile_size, tile_size);

                    entities.push(new Entity(
                        pos,
                        new Sprite(sprite_url, new Rectangle(0, 0, tile_size, tile_size)),
                        layer,
                        material
                    ));
                }
            }
        }
        return entities;
    }
}