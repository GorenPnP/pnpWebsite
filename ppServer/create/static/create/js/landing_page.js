function persönlichkeitChange(e) {

    var p_id = parseInt(document.getElementById('option' + e.currentTarget.selectedIndex).value)

    post({ 'p_ids': [p_id] }, () => {
        document.getElementsByClassName("checkbox")[0].classList.add("checked")
    })
}
