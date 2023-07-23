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

        // show individual faces

        // combine faces with same number
        const reduced_solution = solution
            .reduce((acc, amount, face_index) => {
                if (!amount) return acc;

                const face = faces[face_index];
                acc[face] = (acc[face] || 0) + amount;
                return acc;
            }, {});

        const details = 
            Object.entries(reduced_solution)
                .sort(([a], [b]) => parseInt(a) - parseInt(b))
                .map(([face, amount]) => ` ${amount}x ${face}`)
                .join(", ");

        section.querySelector(".result-details").innerHTML = details;
    }))
})
