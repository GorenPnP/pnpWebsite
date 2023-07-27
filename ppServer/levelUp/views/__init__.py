from django.db.models import F, Max

from character.models import Charakter, RelAttribut, RelFertigkeit


def get_required_aktuellerWert(char: Charakter, attr_titel: str) -> int:
    ''' get min aktuellerWert of attr__titel by current fp, fg '''

    # get attr aktuell
    attribute = {rel.attribut.titel: rel.aktuell for rel in RelAttribut.objects.filter(char=char).annotate(aktuell = F("aktuellerWert") + F("aktuellerWert_temp") + F("aktuellerWert_bonus"))}

    # check with fp
    base_relfert_qs = RelFertigkeit.objects.prefetch_related("fertigkeit__attr1", "fertigkeit__attr2").filter(char=char)

    one_attr_fert = base_relfert_qs.filter(fertigkeit__attr1__titel=attr_titel, fertigkeit__attr2=None).annotate(sum=F("fp") + F("fp_temp"))\
            .aggregate(Max("sum"))["sum__max"] or 0

    two_attr_fert_1 = base_relfert_qs.exclude(fertigkeit__attr2=None).filter(fertigkeit__attr1__titel=attr_titel).annotate(
        sum=F("fp") + F("fp_temp"),
        attr_titel=F("fertigkeit__attr2__titel")
    )
    two_attr_fert_2 = base_relfert_qs.exclude(fertigkeit__attr2=None).filter(fertigkeit__attr2__titel=attr_titel).annotate(
        sum=F("fp") + F("fp_temp"),
        attr_titel=F("fertigkeit__attr1__titel")
    )
    needed_in_two_attr_ferts = []
    for rel in list([*two_attr_fert_1, *two_attr_fert_2]):
        if (attribute[attr_titel] + attribute[rel.attr_titel]) % 2 == 0:
            needed_in_two_attr_ferts.append(2 * rel.sum - attribute[rel.attr_titel])
        else:
            needed_in_two_attr_ferts.append(2 * rel.sum - attribute[rel.attr_titel] -1)


    # check fg
    fg = RelAttribut.objects.filter(char=char, attribut__titel=attr_titel).annotate(sum=F("fg") + F("fg_temp")).values("sum")[0]["sum"]

    # calc max of all
    return max(one_attr_fert, fg, *needed_in_two_attr_ferts)
