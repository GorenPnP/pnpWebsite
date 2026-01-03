/**
 * header scrolls to the top offscreen when the person scrolls up.
 * header scrolls back when the person scrolls down.
 * 
 * Is a reverse to base/js/scrolling_header.js!
 * 
 * Needs:
 *  <link rel="stylesheet" type="text/css" href="{% static 'base/css/textarea.css' %}" />
 *  <link rel="stylesheet" type="text/css" href="{% static 'httpChat/css/textarea.css' %}" />
 *  id="scrolling-header" on the header
 *  id="after-header" on the sibling after the header (sets margin-top)
 * 
*/

let lastScrollTop;

const class_name = "hidden-header";

const body = document.querySelector('body');
const header = document.querySelector("#scrolling-header");
const scroll_indicator = document.querySelector("#scroll-indicator");

function set_afterheader_margin() {
    // rules for scrolling content
    scroll_indicator.style.setProperty("--visible-header-height", header.getBoundingClientRect().height + "px");
}

function scroll_header() {
    const st = Math.round(scroll_indicator.getBoundingClientRect().top);

    // stay the same
    if (lastScrollTop === st) { return; }

    // change
    if (lastScrollTop !== undefined && st > lastScrollTop) {
        body.classList.add(class_name);
    } else {
        body.classList.remove(class_name);
    }

    lastScrollTop = st;
}

document.querySelector("#message-container").addEventListener("scroll", scroll_header);

set_afterheader_margin();
new ResizeObserver(set_afterheader_margin).observe(header);