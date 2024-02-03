# Generated by Django 4.2.8 on 2024-01-24 16:57

from django.db import migrations, models

def add_rule_tables(apps, schema_editor):
    RuleTable = apps.get_model('wiki', 'RuleTable')

    RuleTable.objects.get_or_create(
        topic="bound_ghost_modifier",
        csv_data="""Geister/Attribute;SCH;Angriff;MA;WK;ST;Schadenswiderstand;Reaktion;Bonus-Schaden;Fix-Bonus-Schadenswiderstand;Initiative
Gebundener Geist;+1;+2;+1;+1;+1;+2;+2;+3;+3;+3"""
    )
    RuleTable.objects.get_or_create(
        topic="ghost_zauber_maxtier",
        csv_data="""Stufe des Geistes;Maximaler Tier
1 und 2;0
3 und 4;I
5 und 6;II
7 und 8;III
9 bis 12;IV
13 bis 15;V
16 bis 19;VI
20 und höher;VII"""
    )

def add_ghosts(apps, schema_editor):
    Ghost = apps.get_model('wiki', 'Ghost')

    Ghost.objects.create(
        titel  = "Poltergeist",
        sch  = "2+X",
        angriff  = "5+X",
        ma  = "2+X",
        wk  = "1+X",
        st  = "X",
        schaWI  = "14+X",
        reaktion  = "8",
        schaden_pro_erfolg  = "1W8 K Stumpf",
        initiative  = "10+2X",
        astralschaden  = "x3",
        eigenschaft = """Alle im 5m-Umkreis erleiden pro IR X HP an Schaden. Kann als kH verängstigen. Ist materialisiert. Verursacht körperlichen Schaden. Beherrscht Telekinese. Kann die Spruchzauber Trugbild, Höllenschrei, Brecher, Windhose, Astrales Rauschen und Feger."""
    )
    Ghost.objects.create(
        titel  = "Elementargeist",
        sch  = "X",
        angriff  = "4+X",
        ma  = "5+X",
        wk  = "1+X",
        st  = "2+X",
        schaWI  = "8+X",
        reaktion  = "2",
        schaden_pro_erfolg  = "1W10 K Elementar",
        initiative  = "4+2X",
        astralschaden  = "x4",
        eigenschaft = """Ist materialisiert. Kann eines der folgenden Elemente annehmen;
Luft → nicht im Fernkampf angreifbar
Feuer → alle Nahkämpfer erleiden jedes Mal 2W6 HP Feuerschaden, immun gegen Feuer, schwer anfällig gegen Wasser
Erde → erleidet generell immer 2X HP Schaden weniger, immun gegen Elektrizität
Wasser → Immun gegen Feuer, immun gegen Fernkampfwaffen
Beherrscht die Spruchzauber Elementar-Emitter, Elementar-Schild, Feuerball, Windhose, Inferno, Sandsturm und Wetterkontrolle."""
    )
    Ghost.objects.create(
        titel  = "Seele",
        sch  = "2+X",
        angriff  = "X",
        ma  = "6+X",
        wk  = "4+X",
        st  = "X",
        schaWI  = "6+X",
        reaktion  = "7",
        schaden_pro_erfolg  = "1W6 G",
        initiative  = "12+4X",
        astralschaden  = "x5",
        eigenschaft = """Ist dematerialisiert. Kann physisch angreifen. Schaden, den der Geist verursacht, ist geistig. Erleidet doppelten Schaden durch Spruchzauber. Regeneriert X HP pro IR. Beherrscht die Spruchzauber Heiliung, Heilkreis, Offenes Buch, Statusbrecher, Freie Zunge und Extraktor."""
    )
    Ghost.objects.create(
        titel  = "Kampfgeist",
        sch  = "3+X",
        angriff  = "9+X",
        ma  = "4+X",
        wk  = "3+X",
        st  = "2+X",
        schaWI  = "10+X",
        reaktion  = "6",
        schaden_pro_erfolg  = "1W12 K waffl. Kampf",
        initiative  = "8+3X",
        astralschaden  = "x5",
        eigenschaft = """Ist materialisiert. Verursacht körperlichen Schaden. Kann alle volle 3 Stufen für 6 Initiative pro KR einen Angriff mit einer beliebigen Waffe durchführen, die im Besitz des Beschwörers ist. Beherrscht die Spruchzauber Brecher, Dampfgarer, Sprengball, Energieball, Feuerball, Manablitz, Todesfluch, Toxin und Parasit."""
    )
    Ghost.objects.create(
        titel  = "menschlicher Geist",
        sch  = "2+X",
        angriff  = "X",
        ma  = "1+X",
        wk  = "2+X",
        st  = "1+X",
        schaWI  = "16+X",
        reaktion  = "4",
        schaden_pro_erfolg  = "1W6 K waffl. Kampf",
        initiative  = "5+2X",
        astralschaden  = "x3",
        eigenschaft = """Ist materialisiert. Kann nicht verbannt werden. Verschwindet automatisch nach 1 Stunde. Erleidet passiv Schaden bei Anwesenheit antiheiliger Lebewesen (pro Lebewesen 2 HP Schaden pro IR). Beherrscht die Spruchzauber Attributsschub, Visionär, Reparator und Freie Zunge."""
    )
    Ghost.objects.create(
        titel  = "Watcher",
        sch  = "1+X",
        angriff  = "",
        ma  = "X",
        wk  = "X",
        st  = "",
        schaWI  = "20+X",
        reaktion  = "7",
        schaden_pro_erfolg  = "",
        initiative  = "10+3X",
        astralschaden  = "x1",
        eigenschaft = """Ist dematerialisiert. Kann nicht verbannt werden. Verschwindet automatisch nach 4 Stunden. Kann durch Wände sehen. Kann mit 4X Wahrnehmen. Beherrscht die Zauber Späher, Trugbild, Hologramm, Astrales Rauschen, Astrale Ohren und Astrale Projektion."""
    )
    Ghost.objects.create(
        titel  = "Homunkulus",
        sch  = "X",
        angriff  = "5+X",
        ma  = "X",
        wk  = "1+X",
        st  = "5+X",
        schaWI  = "14+X",
        reaktion  = "8",
        schaden_pro_erfolg  = "1W10 K waffl. Kampf",
        initiative  = "12+3X",
        astralschaden  = "x3",
        eigenschaft = """Ist materialisiert. Besitzt ein UM-Attribut in Höhe der Stufe. Immun gegen Spruchzauberei und andere magische Angriffe. Beherrscht die Spruchzauber Molekularsicht, Molekularbearbeitung, Schrumpfen und Vergrößern."""
    )
    Ghost.objects.create(
        titel  = "Tiergeist",
        sch  = "2+X",
        angriff  = "2+X",
        ma  = "X",
        wk  = "X",
        st  = "1+X",
        schaWI  = "16+X",
        reaktion  = "6",
        schaden_pro_erfolg  = "1W8 K waffl. Kampf",
        initiative  = "6+2X",
        astralschaden  = "x4",
        eigenschaft = """Ist materialisiert. Kann sein Aussehen in verschiedene Tiergestalten ändern. Kann fliegen. Ist immun gegen soziale Interaktion und Manipulation. Ein Angriff verursacht bei einem Treffer den Statuseffekt blutend oder vergiftet (je nach Wunsch). Beherrscht keine Spruchzauber."""
    )
    Ghost.objects.create(
        titel  = "Schutzgeist",
        sch  = "X",
        angriff  = "X",
        ma  = "X",
        wk  = "4+X",
        st  = "6+X",
        schaWI  = "24+X",
        reaktion  = "4",
        schaden_pro_erfolg  = "1W4 K waffl. Kampf",
        initiative  = "4+2X",
        astralschaden  = "x3",
        eigenschaft = """Ist materialisiert. Addiert seinen Schadenswiderstandspool pro KR bei beliebigen Zielen (aufgeteilt, nicht jeder den vollen Pool) hinzu. Erleidet keinen Schaden durch Terrain- oder Statuseffekte. Beherrscht die Spruchzauber Manablockade, Astrales Rauschen, Elementar-Schild und Projektilschild. Beherrscht Antimagie mit einem Würfelpool von 4X."""
    )


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0007_remove_ghost_schnelligkeit_ghost_eigenschaft_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RuleTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=128, unique=True)),
                ('csv_data', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Regel-Tabelle',
                'verbose_name_plural': 'Regel-Tabellen',
                'ordering': ['topic'],
            },
        ),
        migrations.RunPython(add_rule_tables),
        migrations.RunPython(add_ghosts),
    ]