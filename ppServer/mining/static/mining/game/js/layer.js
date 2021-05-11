class Layer {
    constructor(field, index, is_collidable, is_breakable) {
        this.field = field;
        this.index = index;
        this.is_collidable = is_collidable;
        this.is_breakable = is_breakable;
    }

    static reset() {
        return JSON.parse(document.querySelector("#layers").innerHTML)
            .sort((a, b) => a.index - b.index)
            .map(l => new Layer(l.field, l.index, l.is_collidable, l.is_mineable));
    }
}
