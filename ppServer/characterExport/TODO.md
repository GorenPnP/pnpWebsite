```py
def add_some_attrs(apps, schema_editor):
    Attribut = apps.get_model('character', 'Attribut')
    Gfs = apps.get_model('character', 'Gfs')
    GfsAttribut = apps.get_model('character', 'GfsAttribut')

    attrs = [
        ("MG", "Manergetik"),
        ("LB", "Leitungsbahn"),
        ("DM", "Die Macht"),
        ("11", "11"),
    ]

    for titel, beschreibung in attrs:
        attr = Attribut.objects.create(titel=titel, beschreibung=beschreibung)

        for gfs in Gfs.objects.all():
            GfsAttribut.objects.create(gfs=gfs, attribut=attr)
```