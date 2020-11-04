// get class of row
function getClass(tag, prefix = "row") {

    var classes = tag.classList
    for (var c = 0; c < classes.length; c++) {
        if (classes[c].startsWith(prefix)) return classes[c];
    }
    return null
}


function submit(e) {
    var row_class = getClass(e.currentTarget)

    var num = document.getElementsByClassName("num " + row_class)[0].value

    var stufe = document.getElementsByClassName("stufe " + row_class)
    stufe = stufe.length ? stufe[0].value : null

    var selected_index = document.getElementsByClassName("character " + row_class)[0].selectedIndex
    var char = document.getElementsByTagName("option")[selected_index].value
    var notizen = document.getElementsByClassName("notizen " + row_class)[0].value
    var price = /extra/.test(row_class) ? document.getElementsByClassName("price " + row_class)[0].value : null

    var firma_shop = document.getElementsByClassName("firma_shop_id " + row_class)
    firma_shop = firma_shop.length ? firma_shop[0].innerHTML : null

    post({
            "num": num,
            "stufe": stufe,
            "char": char,
            "notizen": notizen,
            "firma_shop": firma_shop,
            "extra": /extra/.test(row_class),
            "price": price
        }, (data) => {
            alert(data["character"] + " hat für " + data["preis"].toLocaleString("de-DE") + " Dr. eingekauft. Von " +
                data["old"].toLocaleString("de-DE") + " Dr. sind noch  " + data["new"].toLocaleString("de-DE") + " Dr. übrig.")
        }
    )
}
