
// Scale events
container.querySelector<HTMLDivElement>(".right-block")!.addEventListener("wheel", function (event) {
    event.preventDefault();
    changeScale(event.deltaY * -0.0005);
});


function changeScale(delta: number) {
    scale += delta;
    
    // Restrict scale
    scale = Math.min(Math.max(0.125, scale), 4);
    
    // Apply scale
    canvas_container.style.width = `${canvas.width * scale}px`;
    canvas_container.style.height = `${canvas.height * scale}px`;

    container.querySelector(".scale-display")!.innerHTML = `${(scale * 100).toFixed(0)}%`;
}

// Handle Clear Button
container.querySelector('.clear')?.addEventListener('click', function () {
    context.clearRect(0, 0, canvas.width, canvas.height);
    reset_bgImage();
});

// Handle Scale Buttons
container.querySelector('.scale-up')?.addEventListener('click', function () {
    changeScale(0.25);
});
container.querySelector('.scale-down')?.addEventListener('click', function () {
    changeScale(-0.25);
});
