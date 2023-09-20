from django.db.models import F, Max

from character.models import Charakter, RelFertigkeit


def get_required_aktuellerWert(char: Charakter, attr_titel: str) -> int:
    ''' get min aktuellerWert of attr__titel by current fp '''

    # check with fp
    return RelFertigkeit.objects\
        .prefetch_related("fertigkeit__attribut").filter(char=char)\
        .filter(fertigkeit__attribut__titel=attr_titel).annotate(sum=F("fp") + F("fp_temp"))\
        .aggregate(Max("sum"))["sum__max"] or 0

