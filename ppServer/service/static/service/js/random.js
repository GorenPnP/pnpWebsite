function roll(num, faces) {
    var solution = Array.from({length: faces.length}, () => 0)
    for (var i = 0; i < num; i++) solution[Math.floor(Math.random() * faces.length)]++

    return solution
}

document.addEventListener("DOMContentLoaded", function() {

    [...document.getElementsByClassName("btn")].forEach(tag => tag.addEventListener("click", ({ currentTarget }) => {
        var section = currentTarget.parentNode
        const faces = JSON.parse(section.getElementsByClassName("faces")[0].value)
        var num = section.getElementsByClassName("num")[0].value
        num = num === "" ? 0 : parseInt(num)

        const solution = roll(num, faces)
        var sum = 0
        for (var i = 0; i < faces.length; i++) sum += solution[i] * faces[i]
        section.getElementsByClassName("result")[0].innerHTML = sum

        if (faces.length == 6) {
            var details = []
            solution.forEach((number, index) => { if (number) details.push(` ${number}x${index+1}`) })

            section.getElementsByClassName("result-details")[0].innerHTML = details.join(",")
        }
    }))
})
