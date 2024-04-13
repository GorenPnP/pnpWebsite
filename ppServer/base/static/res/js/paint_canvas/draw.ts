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


// Mouse Down Event
canvas.addEventListener('mousedown', function (event) {
    setMouseCoordinates(event);
    isDrawing = true;

    // Start Drawing
    context.beginPath();
    context.moveTo(mouseX, mouseY);
});

// Mouse Move Event
canvas.addEventListener('mousemove', function (event) {
    setMouseCoordinates(event);

    if (isDrawing) {
        context.lineTo(mouseX, mouseY);
        context.stroke();
    }
});

// Mouse Up Event
document.addEventListener('mouseup', function (event) {
    setMouseCoordinates(event);
    isDrawing = false;
});

// Mouse Out Event
canvas.addEventListener('mouseout', function (event) {
    setMouseCoordinates(event);
});

// Mouse Enter Event
canvas.addEventListener('mouseenter', function (event) {
    setMouseCoordinates(event);
    if (isDrawing) {
        // Start Drawing
        context.beginPath();
        context.moveTo(mouseX, mouseY);
    }
});


// Handle Mouse Coordinates
function setMouseCoordinates(event: MouseEvent) {
    const boundings = canvas.getBoundingClientRect();
    mouseX = (event.clientX - boundings.left) / scale;
    mouseY = (event.clientY - boundings.top) / scale;
}


// set initial values & stuff
container.querySelector<HTMLButtonElement>('.clear')?.click();  // initially draw background (img or just white)
container.querySelector<HTMLButtonElement>(".colors button")?.click();
container.querySelector<HTMLButtonElement>(".brushes button")?.click();
