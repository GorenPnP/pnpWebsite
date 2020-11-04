function submit() {

    var select_tag = document.getElementsByTagName("select")[0]
    var gfs_id = parseInt(document.getElementById('option' + select_tag.selectedIndex).value)
    var larp = document.getElementsByClassName("checkbox")[0].classList.contains('checked')

    post({ gfs_id, larp })
}
