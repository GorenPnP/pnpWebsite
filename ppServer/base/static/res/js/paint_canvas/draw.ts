///////////////////////////////////////////////////////////////////////
// set DOM: color buttons
const colors_container = container.querySelector(".colors")!;
const eraser = colors_container.querySelector(".eraser")!;
ms_colors.forEach(color => {
    const tag = document.createElement("button");
    tag.type = "button";
    tag.style.setProperty("--brush-color", color);
    colors_container.insertBefore(tag, eraser);
});


// set DOM: brush-buttons
const brushes_container = container.querySelector(".brushes")!;
brushes.forEach(brush => {
    const tag = document.createElement("button");
    tag.type = "button";
    tag.style.setProperty("--brush-size", `${brush}px`);
    brushes_container.appendChild(tag);
});

canvas_container.style.width = `${canvas.width * scale}px`;
canvas_container.style.height = `${canvas.height * scale}px`;



///////////////////////////////////////////////////////////////////////


// Handle Colors
container.querySelector<HTMLDivElement>('.colors')!.addEventListener('click', function (event: any) {
    this.querySelectorAll('.selected').forEach(color => color.classList.remove("selected"));
    const button = event.target.closest("button");
    if (button) {
        button.classList.add("selected");
        
        context.strokeStyle = button.style.getPropertyValue("--brush-color") || 'pink';
        context.globalCompositeOperation = button.classList.contains("eraser") ? 'destination-out' : 'source-over';
    }
});

// Handle Brushes
container.querySelector<HTMLDivElement>('.brushes')!.addEventListener('click', function (event: any) {
    this.querySelectorAll('.selected').forEach(color => color.classList.remove("selected"));
    event.target.classList.add("selected");
    
    context.lineWidth = parseInt(event.target.style.getPropertyValue("--brush-size")) || 1;
});


// Pointer Down Event
canvas.addEventListener('pointerdown', function (event) {
    setPointerCoordinates(event);
    isDrawing = true;

    // Start Drawing
    context.beginPath();
    context.moveTo(pointerX, pointerY);
});

// Pointer Move Event
canvas.addEventListener('pointermove', function (event) {
    setPointerCoordinates(event);

    if (isDrawing) {
        context.lineTo(pointerX, pointerY);
        context.stroke();
    }
});

// Pointer Up Event
document.addEventListener('pointerup', function (event) {
    setPointerCoordinates(event);
    isDrawing = false;
});

// Pointer Out Event
canvas.addEventListener('pointerout', function (event) {
    setPointerCoordinates(event);
});

// Pointer Enter Event
canvas.addEventListener('pointerenter', function (event) {
    setPointerCoordinates(event);
    if (isDrawing) {
        // Start Drawing
        context.beginPath();
        context.moveTo(pointerX, pointerY);
    }
});


// Handle Pointer Coordinates
function setPointerCoordinates(event: PointerEvent) {
    const boundings = canvas.getBoundingClientRect();
    pointerX = (event.clientX - boundings.left) / scale;
    pointerY = (event.clientY - boundings.top) / scale;
}


// set initial values & stuff
container.querySelector<HTMLButtonElement>('.clear')?.click();  // initially draw background (img or just white)
container.querySelector<HTMLButtonElement>(".colors button")?.click();
container.querySelector<HTMLButtonElement>(".brushes button")?.click();
