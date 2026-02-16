from .models import Log

def render_number(num: int) -> str:
    try:
        return f"{num:,}".replace(",", ".")
    except:
        return num


def logShop(spieler, char, item):
    """Gekaufte Items"""
    """item = {"num": int,  "preis_ges": , "stufe": Optional<int>, "item": Shop", "firma_titel": }"""

    item_repr = item['item'].__str__()

    if item["num"] <= 0:
        raise ValueError(f"Item {item_repr}: die gekaufte Anzahl ist negativ")

    if item["preis_ges"] < 0:
        raise ValueError(f"Item {item_repr}: der bezahlte Preis ist negativ")

    notizen = f"{item['num']}x {item_repr}"
    if item["item"].stufenabhängig:
        notizen += f" (Stufe {item['stufe']})"
    notizen += f" von der Firma {item['firma_titel']} gekauft."

    kosten = f"{item['preis_ges']} Drachmen"

    Log.objects.create(art="s", spieler=spieler, char=char, notizen=notizen, kosten=kosten)


def logAuswertung(spieler, char, story, fields):
    """ fields: Dict["story", "ep", "sp", "prestige", "verzehr"] """

    notizen = ", ".join([f"+{render_number(v)} {k}" for k, v in fields.items() if v])

    Log.objects.create(art="u", spieler=spieler, char=char, notizen=notizen, kosten="Story " + story)


def logStufenaufstieg(spieler, char):

    Log.objects.create(art="i", spieler=spieler, char=char, notizen=f"Stufe {char.ep_stufe} -> {char.ep_stufe_in_progress}")
