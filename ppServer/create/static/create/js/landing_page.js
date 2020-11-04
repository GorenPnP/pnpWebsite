function professionChange(e) {

    var p_id = parseInt(document.getElementById('option' + e.currentTarget.selectedIndex).value)

    post({ 'p_id': p_id }, (data) => {

        // tell people if some points had to be decreased
        reaction(data)

        if (Object.keys(data).indexOf("redo") !== -1 && data["redo"]) {

            var redo = data["redo"]
            if (redo.some(sec => sec === "prof")) document.getElementsByClassName("checkbox")[0].classList.toggle("checked")
            if (redo.some(sec => sec === "attr")) {
                document.getElementsByClassName("checkbox")[1].classList.remove("checked")
                document.getElementById("ap").innerHTML = data["ap"]
            }
            if (redo.some(sec => sec === "fert")) {
                document.getElementsByClassName("checkbox")[2].classList.remove("checked")
                document.getElementById("fp").innerHTML = data["fp"]
                document.getElementById("fg").innerHTML = data["fg"]
            }
        }
    })
}
