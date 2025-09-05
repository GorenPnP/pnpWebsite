const container = document.querySelector(".paint-canvas-container")!;

const canvas_container = container.querySelector<HTMLDivElement>(".canvas-container")!;

const canvas = canvas_container.querySelector<HTMLCanvasElement>(".paint-canvas")!;
const context = canvas.getContext("2d")!;

const bg_canvas = canvas_container.querySelector<HTMLCanvasElement>(".bg-canvas")!;
const bg_context = bg_canvas.getContext("2d")!;


let bg_image: HTMLImageElement;
let scale = 1.0;
let pointerX = 0;
let pointerY = 0;
let isDrawing = false;
let eraserActive = false;


const original_colors = [
    "#0000ff",
    "#009fff",
    "#0fffff",
    "#bfffff",
    "#000000",
    "#333333",
    "#666666",
    "#999999",
    "#ffcc66",
    "#ffcc00",
    "#ffff00",
    "#ffff99",
    "#003300",
    "#555000",
    "#00ff00",
    "#99ff99",
    "#f00000",
    "#ff6600",
    "#ff9933",
    "#f5deb3",
    "#330000",
    "#663300",
    "#cc6600",
    "#deb887",
    "#aa0fff",
    "#cc66cc",
    "#ff66ff",
    "#ff99ff",
    "#e8c4e8",
    "#ffffff",
];

const ms_colors = [
    "#000000",
    "#464646",
    "#787878",
    "#b4b4b4",
    "#dcdcdc",
    "#ffffff",
    "#990030",
    "#9c5a3c",
    "#ed1c24",
    "#ffa3b1",
    "#ff7e00",
    "#e5aa7a",
    "#ffc20e",
    "#f5e49c",
    "#fff200",
    "#fff9bd",
    "#a8e61d",
    "#d3f9bc",
    "#22b14c",
    "#9dbb61",
    "#00b7ef",
    "#99d9ea",
    "#4d6df3",
    "#709ad1",
    "#2f3699",
    "#546d8e",
    "#6f3198",
    "#b5a5d5",            
];
const brushes = Array.from({length: 5}, (_, i) => i+1);