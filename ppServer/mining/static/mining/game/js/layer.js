class Layer {
    constructor(entities, index, is_collidable, is_breakable) {
        this.entities = entities;
        this.index = index;
        this.is_collidable = is_collidable;
        this.is_breakable = is_breakable;
    }

    static reset() {
        return JSON.parse(document.querySelector("#layers").innerHTML)
            .sort((a, b) => a.index - b.index);
    }
}
