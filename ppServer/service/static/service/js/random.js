function roll(num, faces) {
    var solution = Array.from({length: faces.length}, () => 0);
    for (var i = 0; i < num; i++) solution[Math.floor(Math.random() * faces.length)]++;

    return solution;
}

document.addEventListener("DOMContentLoaded", function() {

    [...document.getElementsByClassName("btn")].forEach(tag => tag.addEventListener("click", function() {
        var section = this.parentNode;
        const faces = JSON.parse(section.querySelector("[data-faces]").dataset.faces);
        var num = section.querySelector(".num").value;
        num = num === "" ? 0 : parseInt(num);

        const solution = roll(num, faces);
        var sum = solution.reduce((acc, count, i) => acc + (count * faces[i]), 0);
        section.getElementsByClassName("result")[0].innerHTML = sum;

        // if dice is ordinary w6, show individual faces
        if (faces.length == 6 && section.querySelector(".num").id.toLowerCase().includes("w6")) {
            var details = [];
            solution.forEach((number, index) => { if (number) details.push(` ${number}x${index+1}`) })

            section.querySelector(".result-details").innerHTML = details.join(",")
        }
    }))
})
