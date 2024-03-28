/**
 * header scrolls to the top offscreen when the person scrolls down.
 * header scrolls back when the person scrolls up.
 * 
 * Needs:
 *  <link rel="stylesheet" type="text/css" href="{% static 'base/css/textarea.css' %}" />
 *  id="scrolling-header" on the header
 *  id="after-header" on the sibling after the header (sets margin-top)
 * 
*/

let lastScrollTop = 0;

const class_name = "hidden-header";
const header = document.querySelector("#scrolling-header");

function set_afterheader_margin() {
    const header_height = header.getBoundingClientRect().height + "px";
    document.querySelector("#after-header").style.setProperty("margin-top", header_height);

    // FULLSCREEN MD-EDITOR: stay under header

    document.querySelectorAll(".EasyMDEContainer:has(.editor-toolbar.fullscreen) > *").forEach(element =>
        element.style.setProperty("margin-top", header_height)
    );
    document.querySelectorAll(".EasyMDEContainer:has(.editor-toolbar:not(.fullscreen)) > *").forEach(element =>
        element.style.setProperty("margin-top", "unset")
    );
}

function scroll_header() {
    const st = window.scrollY;
    const body = document.querySelector('body');

    if (st > lastScrollTop && st > 0) {
        body.classList.add(class_name);
    } else {
        body.classList.remove(class_name);
    }

    lastScrollTop = st;
}

window.addEventListener("scroll", scroll_header);

set_afterheader_margin();
new ResizeObserver(set_afterheader_margin).observe(header);
