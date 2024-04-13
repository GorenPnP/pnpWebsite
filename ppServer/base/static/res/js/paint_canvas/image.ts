///////////////////////////////////////////////////////////////////////
const img_src = JSON.parse(document.querySelector("#canvas-image-src")?.innerHTML || "") || null;

// init bg image
reset_bgImage(img_src?.bg || undefined).then(() => {

    // init previously drawn stuff
    if (img_src?.drawn) {
        const image = new Image();
        image.onload = function() {
            context.drawImage(image, 0, 0, canvas.width, canvas.height);
        };
        image.src = img_src?.drawn;
    }
});


///////////////////////////////////////////////////////////////////////


// handle bg-image upload
container.querySelector<HTMLInputElement>("#bg-image-btn")!.addEventListener("change", function() {
    if (this.files?.[0]) {
        const reader = new FileReader();
        reader.onload = function (e: any) {
            reset_bgImage(e.target.result);
        };
        reader.readAsDataURL(this.files[0]);
    }
});

async function reset_bgImage(src?: string): Promise<void> {
    return new Promise<void>(function(resolve, reject) {
        bg_image?.remove();

        if (src) {
    
            bg_image = new Image();
            bg_image.onload = function() {
                canvas.width = bg_image.width;
                canvas.height = bg_image.height;
                bg_canvas.width = bg_image.width;
                bg_canvas.height = bg_image.height;
                bg_context.drawImage(bg_image, 0, 0, bg_canvas.width, bg_canvas.height);
    
                // set scale to 100% original image size
                scale = 1;
                changeScale(0.0);

                resolve();
            };
            bg_image.src = src;
        } else {
            bg_context.fillStyle = "#fff";
            bg_context.fillRect(0, 0, bg_canvas.width, bg_canvas.height);

            resolve();
        }

    });
}
