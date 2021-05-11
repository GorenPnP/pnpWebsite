
// Collisions

function collides(x, y, r, b, x2, y2, r2, b2) {
    return !(r <= x2 || x >= r2 ||
             b <= y2 || y >= b2);
}

function boxCollides(pos1, pos2) {
    return collides(pos1.x, pos1.y,
                    pos1.x + pos1.w, pos1.y + pos1.h,
                    pos2.x, pos2.y,
                    pos2.x + pos2.w, pos2.y + pos2.h);
}
