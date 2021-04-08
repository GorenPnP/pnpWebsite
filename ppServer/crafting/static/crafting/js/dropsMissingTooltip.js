/**
 * To future me:
 * This snippet is added when a Material model is displayed as inline on admin pages. Need a 3D form. Fun, huh?
 */

window.addEventListener("DOMContentLoaded", () => {
    console.log("HERE")
    setTimeout(() => {

        const tag = document.querySelector(".dynamic-material_set").parentNode;
        tag.innerHTML = "<tr><td colspan='8'><b style='color: red'>Achtung: Nachfolgende Materialien haben kein Feld 'drops/loot'!</b></td></tr>" + tag.innerHTML;
    }, 2000)
});
