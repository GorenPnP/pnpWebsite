import xlsxwriter, re
from typing import Any

from django.db.models.functions import Concat
from django.db.models import F, Subquery, OuterRef, Q, Value, CharField,  prefetch_related_objects
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView

from ppServer.mixins import VerifiedAccountMixin
from character.models import *


POSITION = {
    "SCH": "Werte!N3",
    "IN": "Werte!N4",
    "ST": "Werte!N5",
    "VER": "Werte!N6",
    "GES": "Werte!N7",
    "UM": "Werte!N8",
    "WK": "Werte!N9",
    "MA": "Werte!N10",
    "F": "Werte!N11",
    "N": "Werte!N12",

    "fg_SCH": "Werte!F3",
    "fg_IN": "Werte!F6",
    "fg_ST": "Werte!F9",
    "fg_VER": "Werte!F12",
    "fg_GES": "Werte!F15",
    "fg_UM": "Werte!F18",
    "fg_WK": "Werte!F21",
    "fg_MA": "Werte!F24",
    "fg_F": "Werte!F27",
    "fg_N": "Werte!F30",

    "Laufen": "Werte!G3",
    "Schwimmen": "Werte!G4",
    "Klettern": "Werte!G5",
    "Wahrnehmung": "Werte!G6",
    "Erinnern": "Werte!G7",
    "Orientieren": "Werte!G8",
    "Werfen": "Werte!G9",
    "Heben": "Werte!G10",
    "Konstitution": "Werte!G11",
    "Deckung": "Werte!G12",
    "Zähigkeit": "Werte!G13",
    "Kontern": "Werte!G14",
    "Fingerfertigkeit": "Werte!G15",
    "Zielen": "Werte!G16",
    "Schleichen": "Werte!G17",
    "Verhalten": "Werte!G18",
    "Verhandeln": "Werte!G19",
    "Täuschen": "Werte!G20",
    "Manipulation": "Werte!G21",
    "Entschlossenheit": "Werte!G22",
    "Resistenz": "Werte!G23",
    "Antimagie": "Werte!G24",
    "Kampfmagie": "Werte!G25",
    "Spruchzauberei": "Werte!G26",
    "Spannung": "Werte!G27",
    "Triebladung": "Werte!G28",
    "Elektrisch": "Werte!G29",
    "Klingen": "Werte!G30",
    "N.-Waffen": "Werte!G31",
    "Waffenloser Kampf": "Werte!G32",
    "Wissen": "Werte!G34",
    "Lernen": "Werte!G35",
    "Lehren": "Werte!G36",
    "Fliegen": "Werte!G37",
    "Erste Hilfe": "Werte!G38",
    "Technik": "Werte!G39",
    "Fahrzeuge": "Werte!G40",
    "Wesenkräfte": "Werte!G41",
    "Personenkenntnis": "Werte!G42",
    "Improvisieren": "Werte!G43",
}

COLOR = {
    "white": "#ffffff",
    "grau 1": "#eeeeee",
    "grau 2": "#dddddd",
    "grau 3": "#cccccc",
    "grau 4": "#b2b2b2",
    "grau 5": "#999999",
    "grau 6": "#808080",
    "grau 7": "#666666",
    "grau 8": "#333333",
    "grau 9": "#1c1c1c",
    "grau 10": "#111111",
    "black": "#000000",

    "green": "#66ff66",
    "red": "#ff9999",
    "red-font": "#fe3349",
    "orange-yellow": "#ffcc00",
    "light-blue": "#66ffff",
    "magenta": "#ff33ff",
    "lavender": "#e6e6ff",

    # diagram
    "diagram-red": "#ffa187",
    "diagram-blue": "#80a2c3",
}

def split_position(position):
    ws, cell = position.split("!")
    alpha = re.search("[A-Z]+", cell)[0]
    num = int(re.search("\d+", cell)[0])

    return {"ws": ws, "alpha": alpha, "num": num}


class CharacterExportView(LoginRequiredMixin, VerifiedAccountMixin, DetailView):
    model = Charakter


    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

        # get char
        char = self.get_object()
        prefetch_related_objects([char],
            "eigentümer", "gfs__gfsstufenplan_set__basis", "relpersönlichkeit_set", "spezies",
            "beruf", "religion", "relattribut_set", "relfertigkeit_set",
            "affektivität_set", "releinbauten_set__item", "relausrüstung_technik_set__item",
            "relschusswaffen_set__item", "relwaffen_werkzeuge_set__item", "relitem_set__item",
            "relwesenkraft_set__wesenkraft", "reltalent_set__talent", "relrituale_runen_set__item", "relzauber_set__item"
        )

        # allowed to export?
        if request.user.groups.filter(name__iexact="spieler") and char.eigentümer.name != request.user.username:
            return redirect("character:index")


        # prepare response & xlsx-workbook
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f"attachment; filename={char.name}.xlsx"
        wb = xlsxwriter.Workbook(response, {'in_memory': True, "default_format_properties": {
            "font_name": "Arial",
            "font_size": 10,
            'num_format': '#,##0.#'
        }})

        # formats
        form_align_center_center = {'align': 'center', "valign": "vcenter"}
        form_align_bottom_center = {'align': 'center', "valign": "bottom"}
        form_align_top_left = {'align': 'left', "valign": "top"}
        form_text_wrap = { 'text_wrap': True, "valign": "top" }

        form_bold = {'bold': True}
        form_italic = {'italic': True}
        form_underline = {'underline': True}
        form_section_titel = dict(form_align_center_center, **form_bold, **form_italic, **form_underline, **{"font_size": 12})
        form_sub_titel = dict(form_align_center_center, **form_bold)

        form_cell_border = {"border": 1}

        # formats
        format_align_center_center = wb.add_format(form_align_center_center)
        format_section_titel = wb.add_format(form_section_titel)
        format_sub_titel = wb.add_format(form_sub_titel)
        format_border_top = wb.add_format({"top": 1})
        format_border_left = wb.add_format({"left": 1})
        format_border_right = wb.add_format({"right": 1})
        format_border_bottom = wb.add_format({"bottom": 1})
        format_border_left_right = wb.add_format({"left": 1, "right": 1})


        # WERTE
        werte_ws = wb.add_worksheet("Werte")
        
        # top line
        format_titel = wb.add_format(dict(form_section_titel,  **{"font_color": COLOR["red-font"]}))
        format_konz_titel = wb.add_format(dict(form_sub_titel,  **form_cell_border))
        format_konz = wb.add_format(dict(form_sub_titel, **form_cell_border, **{"bg_color": COLOR["green"], "font_size": 18}))
        format_prestige_titel = wb.add_format(dict(form_sub_titel, **form_cell_border, **form_underline, **{"font_size": 12}))
        format_prestige = wb.add_format(dict(form_sub_titel, **form_cell_border, **form_align_bottom_center, **{"font_size": 14}))

        werte_ws.write(0, 0, 'Charakter:', format_titel)
        werte_ws.merge_range("B1:D1", char.name)
        werte_ws.write(0, 4, "Spieler:", format_titel)
        werte_ws.merge_range("F1:H1", char.eigentümer.get_real_name() if char.eigentümer else None)
        werte_ws.write("I1", "Konzentration (IST/Max.)", format_konz_titel)
        werte_ws.write_row(0, 9, [0, char.konzentration or 0], format_konz)
        werte_ws.merge_range("L1:O1", "Kostet 1 SP für +2 Konz.")

        # right off
        werte_ws.merge_range("P2:R2", "Verzehr", format_prestige_titel)
        werte_ws.merge_range("P3:R4", char.verzehr, format_prestige)
        werte_ws.merge_range("P5:R5", "Prestige", format_prestige_titel)
        werte_ws.merge_range("P6:R7", char.prestige, format_prestige)
        werte_ws.merge_range("P9:R9", "Hat MG?", format_prestige_titel)
        werte_ws.merge_range("P10:R11", 0, format_prestige)
        werte_ws.merge_range("P12:R12", "0 = nein, 1 = ja")


        # center down
        format_gsh_titel = wb.add_format(dict(form_sub_titel, **{"left": 1}))
        format_gsh = wb.add_format(dict(form_sub_titel, **{"right": 1}))
        format_ini_titel = wb.add_format(dict(form_sub_titel, **{"bg_color": COLOR["orange-yellow"], "left": 1}))
        format_ini = wb.add_format(dict(form_sub_titel, **{"bg_color": COLOR["orange-yellow"]}))
        format_asWi_topic = wb.add_format(dict(form_section_titel, **form_cell_border, **{"bg_color": COLOR["grau 2"]}))
        format_asWi = wb.add_format(dict(form_sub_titel, **form_cell_border, **{"font_size": 24, "bg_color": COLOR["grau 2"]}))
        format_limit_topic__first = wb.add_format(dict(form_section_titel, **{"bg_color": COLOR["grau 1"], "left": 1}))
        format_limit_topic__last = wb.add_format(dict(form_section_titel, **{"bg_color": COLOR["grau 1"]}))
        format_limit_titel = wb.add_format(dict(form_sub_titel, **{"bg_color": COLOR["grau 1"], "left": 1}))
        format_limit = wb.add_format(dict(form_sub_titel, **form_underline, **{"font_size": 14, "font_color": COLOR["red-font"], "bg_color": COLOR["grau 1"]}))
        werte_ws.write("I2", "Glück", format_gsh_titel)
        werte_ws.write("J2", 100, format_gsh)
        werte_ws.write("I3", "Sanität", format_gsh_titel)
        werte_ws.write("J3", 100, format_gsh)
        werte_ws.write("I4", "Humor", format_gsh_titel)
        werte_ws.write("J4", "=N8*5", format_gsh)
        werte_ws.write("I5", "Initiative", format_ini_titel)
        werte_ws.write("J5", "=N9+N5"+(f"+{char.initiative_bonus}" if char.initiative_bonus else ""), format_ini)
        werte_ws.write("I6", "W4", format_ini_titel)
        werte_ws.write("J6", "=N3", format_ini)
        werte_ws.merge_range("I7:I8", "Astral-WI", format_asWi_topic)
        werte_ws.merge_range("J7:J8", "=N9+N10"+(f"+{char.astralwiderstand_bonus}" if char.astralwiderstand_bonus else ""), format_asWi)
        werte_ws.write("I9", "Limits", format_limit_topic__first)
        werte_ws.write("J9", None, format_limit_topic__last)
        werte_ws.write("I10", "Körperlich", format_limit_titel)
        werte_ws.write("J10", "=(N3+N5+N6+N7)/2", format_limit)
        werte_ws.write("I11", "Geistig", format_limit_titel)
        werte_ws.write("J11", "=(N4+N8+N9)/2", format_limit)
        werte_ws.write("I12", "Magisch", format_limit_titel)
        werte_ws.write("J12", "=(N9+N10)/2", format_limit)

        # Vor- & Nachteile
        format_teil_titel = wb.add_format(dict(form_sub_titel, **form_cell_border, **{"font_size": 12}))
        format_vorteil = wb.add_format(dict(form_text_wrap, **form_cell_border, **form_align_top_left, **{"bg_color": COLOR["green"]}))
        format_nachteil = wb.add_format(dict(form_text_wrap, **form_cell_border, **form_align_top_left, **{"bg_color": COLOR["red"]}))
        werte_ws.merge_range("I13:I15", "Vorteile", format_teil_titel)
        werte_ws.merge_range("J13:R15", ", ".join([rel.__repr__() for rel in char.relvorteil_set.order_by("teil__titel").filter(will_create=False)]), format_vorteil)

        werte_ws.merge_range("I16:I18", "Nachteile", format_teil_titel)
        werte_ws.merge_range("J16:R18", ", ".join([rel.__repr__() for rel in char.relnachteil_set.order_by("teil__titel").filter(will_create=False)]), format_nachteil)

        # continue center down
        format_state_titel = wb.add_format(dict(form_sub_titel, **form_italic, **{"left": 1}))
        format_state_subtitel = wb.add_format(dict(form_italic, **form_align_center_center, **{"left": 1}))
        format_state_subtitel__last = wb.add_format(dict(form_italic, **form_align_center_center, **{"right": 1}))
        format_state_percent = wb.add_format(dict(form_align_center_center, **{"left": 1}))
        format_state_percent__last = wb.add_format(dict(form_align_center_center, **{"left": 1, "bottom": 1}))
        format_state = wb.add_format(dict(form_sub_titel, **{"right": 1}))
        format_state__last = wb.add_format(dict(form_sub_titel, **{"right": 1, "bottom": 1}))
        format_zufall = wb.add_format(dict(form_align_center_center, **form_cell_border))
        format_sp = wb.add_format(dict(form_sub_titel, **{"bg_color": COLOR["orange-yellow"]}))
        format_manifest = wb.add_format(dict(form_section_titel, **form_cell_border, **{"bg_color": COLOR["magenta"]}))
        format_currencies = wb.add_format(dict(form_sub_titel, **{"bg_color": COLOR["green"]}))
        format_ep = wb.add_format(dict(form_section_titel, **{"bg_color": COLOR["red"]}))
        format_death = wb.add_format(dict(form_sub_titel, **form_cell_border, **{"bg_color": COLOR["black"], "font_color": COLOR["white"]}))

        werte_ws.write("I19", "Zustandsmonitor", format_state_titel)
        werte_ws.write("J19", None, format_state_subtitel__last)
        werte_ws.write("I20", "% HP", format_state_subtitel)
        werte_ws.write("J20", "Malus", format_state_subtitel__last)
        werte_ws.write("I21", "<80%", format_state_percent)
        werte_ws.write("J21", -1, format_state)
        werte_ws.write("I22", "<60%", format_state_percent)
        werte_ws.write("J22", -2, format_state)
        werte_ws.write("I23", "<50%", format_state_percent)
        werte_ws.write("J23", -3, format_state)
        werte_ws.write("I24", "<30%", format_state_percent)
        werte_ws.write("J24", -4, format_state)
        werte_ws.write("I25", "<10%", format_state_percent__last)
        werte_ws.write("J25", -5, format_state__last)
        werte_ws.write_row("I26", ["Tot ab", "=N5*(-2)"], format_death)
        werte_ws.write("K19", "IP", format_sub_titel)
        werte_ws.write("L19", char.ip, format_currencies)
        werte_ws.write("K20", "TP", format_sub_titel)
        werte_ws.write("L20", char.tp, format_currencies)
        werte_ws.write_row("K21", ["Skillpunkte", char.sp], format_sp)
        werte_ws.write_row("K22", ["Manifest", char.manifest - char.sonstiger_manifestverlust], format_manifest)
        werte_ws.write("K24", "EP", format_align_center_center)
        werte_ws.write("L24", char.ep, format_ep)
        werte_ws.write("K25", "Stufe", format_align_center_center)
        werte_ws.write("L25", char.ep_stufe, format_ep)

        werte_ws.merge_range("K26:L26", "Zufall: 12 (SW = 4)", format_zufall)


        # lower half of middle
        format_wesen_titel = wb.add_format(dict(form_section_titel, **{"font_size": 8, "top": 1, "bottom": 1, "left": 1, "bg_color": COLOR["grau 3"]}))
        format_wesen = wb.add_format(dict(form_sub_titel, **form_italic, **{"top": 1, "bottom": 1, "bg_color": COLOR["grau 3"]}))
        format_person_titel = wb.add_format(dict(form_align_center_center, **{"left": 1}))
        format_person_titel__first = wb.add_format(dict(form_align_center_center, **{"left": 1, "top": 1}))
        format_person = wb.add_format(dict(form_align_center_center, **{"right": 1}))
        persönlichkeiten = ", ".join([p["persönlichkeit__titel"] for p in char.relpersönlichkeit_set.values("persönlichkeit__titel")])

        werte_ws.write("I27", "Lebewesen (Stufe):", format_wesen_titel)
        werte_ws.merge_range("J27:L27", f"{char.gfs.titel if char.gfs else ', '.join([s['titel'] for s in char.spezies.values('titel')])} ({char.skilltree_stufe})", format_wesen)
        werte_ws.write("I28", "Persönlichkeit:", format_wesen_titel)
        werte_ws.merge_range("J28:L28", persönlichkeiten, format_wesen)

        werte_ws.write("I29", "Gewicht:", format_person_titel__first)
        werte_ws.merge_range("J29:L29", f"{char.gewicht} kg", format_person)
        werte_ws.write("I30", "Größe:", format_person_titel)
        werte_ws.merge_range("J30:L30", f"{char.größe} cm", format_person)
        werte_ws.write("I31", "Alter:", format_person_titel)
        werte_ws.merge_range("J31:L31", f"{char.alter}", format_person)
        werte_ws.write("I32", "Geschlecht:", format_person_titel)
        werte_ws.merge_range("J32:L32", char.geschlecht, format_person)
        werte_ws.write("I33", "Sexualität:", format_person_titel)
        werte_ws.merge_range("J33:L33", char.sexualität, format_person)
        werte_ws.write("I34", "Beruf:", format_person_titel)
        werte_ws.merge_range("J34:L34", char.beruf.titel, format_person)
        werte_ws.write("I35", "Präf. Arm:", format_person_titel)
        werte_ws.merge_range("J35:L35", char.präf_arm, format_person)
        werte_ws.write("I36", "Religion:", format_person_titel)
        werte_ws.merge_range("J36:L36", char.religion.titel, format_person)
        werte_ws.write("I37", "Hautfarbe:", format_person_titel)
        werte_ws.merge_range("J37:L37", char.hautfarbe, format_person)
        werte_ws.write("I38", "Haarfarbe:", format_person_titel)
        werte_ws.merge_range("J38:L38", char.haarfarbe, format_person)
        werte_ws.write("I39", "Augenfarbe:", format_person_titel)
        werte_ws.merge_range("J39:L39", char.augenfarbe, format_person)
        werte_ws.write_row("I40", [None, None, None, None], format_border_top)
        

        # colorful dice
        format_colorful_titel = wb.add_format(dict(form_align_center_center, **form_italic, **{"left": 1}))
        format_colorful_titel_emph = wb.add_format(dict(form_align_center_center, **form_italic, **form_bold, **{"left": 1}))
        format_colorful = wb.add_format(dict(form_sub_titel, **{"right": 1}))

        werte_ws.merge_range("M19:O19", "Reaktion", format_colorful_titel_emph)
        werte_ws.merge_range("P19:R19", "=(N3+N7+N9)/2"+(f"+{char.reaktion_bonus}" if char.reaktion_bonus else ""), format_colorful)
        werte_ws.write("S19", "(SCH+GES+WK)/2")
        werte_ws.merge_range("M20:O20", "Rüstung Schutz | Stärke", format_colorful_titel)
        werte_ws.merge_range("P20:R20", "__ | __ HP", format_colorful)
        werte_ws.write("S20", "s. Rüstung")
        werte_ws.merge_range("M21:O21", "Haltbarkeit der Rüstung", format_colorful_titel)
        werte_ws.merge_range("P21:R21", "__", format_colorful)
        werte_ws.write("S21", "s. Rüstung")
        werte_ws.merge_range("M22:O22", "nat. Schadenswiderstand", format_colorful_titel_emph)
        werte_ws.merge_range("P22:R22", "=N5+N6"+(f"+{char.natürlicher_schadenswiderstand_bonus}" if char.natürlicher_schadenswiderstand_bonus else ""), format_colorful)
        werte_ws.write("S22", "ST+VER (xHP pro Erfolg, normal 1)")
        werte_ws.merge_range("M23:O23", "Intuition", format_colorful_titel)
        werte_ws.merge_range("P23:R23", "=(N4+2+N3)/2", format_colorful)
        werte_ws.write("S23", "(IN+2*SCH)/2")
        werte_ws.merge_range("M24:O24", "Geh-/Lauf- und Sprintrate", format_colorful_titel)
        werte_ws.write_row("P24", ["=N3*2", "=N3*4", "=N3*4+G3"], format_colorful)
        werte_ws.write("S24", "SCH*2, SCH*4, SCH*4 + Laufen + NE auf Laufen *2m")
        werte_ws.merge_range("M25:O25", "Bewegung Astral (in m/10sek)", format_colorful_titel)
        werte_ws.merge_range("P25:R25", "=2*N10*(N9+N3)", format_colorful)
        werte_ws.write("S25", "2*MA*(WK+SCH)")
        werte_ws.merge_range("M26:O26", "Schwimmen (in m/10sek)", format_colorful_titel)
        werte_ws.merge_range("P26:R26", "=P24/3+G4/5", format_colorful)
        werte_ws.write("S26", "Gehrate/3+Schwimmen/5")
        werte_ws.merge_range("M27:O27", "Tauchen (in m/10sek)", format_colorful_titel)
        werte_ws.merge_range("P27:R27", "=P24/5+G4/5", format_colorful)
        werte_ws.write("S27", "Gehrate/5+Schwimmen/5")
        werte_ws.merge_range("M28:O28", "Tragfähigkeit", format_colorful_titel)
        werte_ws.merge_range("P28:R28", "=N5*3+N7", format_colorful)
        werte_ws.write("S28", "ST*3+GES")
        werte_ws.merge_range("M29:O29", "Heben pro Erfolg (kg)", format_colorful_titel)
        werte_ws.merge_range("P29:R29", "=N5*4+N12", format_colorful)
        werte_ws.write("S29", "ST*4+N")
        werte_ws.merge_range("M30:O30", "Ersticken nach x Sekunden", format_colorful_titel)
        werte_ws.merge_range("P30:R30", "=N9*3+G10+G22+G4*3", format_colorful)
        werte_ws.write("S30", "WK*3+Heben+Entschlossenheit+Schwimmen*3")
        werte_ws.merge_range("M31:O31", "Immunsystem (W100)", format_colorful_titel)
        werte_ws.merge_range("P31:R31", "=N5*5+N6+G23+G11", format_colorful)
        werte_ws.write("S31", "ST*5+VER+Resistenz+Konstitution")
        werte_ws.merge_range("M32:O32", "Regeneration in HP pro Tag", format_colorful_titel)
        werte_ws.merge_range("P32:R32", "=N5+N9", format_colorful)
        werte_ws.write("S32", "ST+WK")
        werte_ws.merge_range("M33:O33", "Manaoverflow", format_colorful_titel)
        werte_ws.merge_range("P33:R33", "=(N9+N10)*3", format_colorful)
        werte_ws.write("S33", "(WK+MA)*3")
        werte_ws.merge_range("M34:O34", "Crit.-Value Angriff", format_colorful_titel)
        werte_ws.merge_range("P34:R34", char.crit_attack, format_colorful)
        werte_ws.merge_range("M35:O35", "Crit.-Value Verteidigung", format_colorful_titel)
        werte_ws.merge_range("P35:R35", char.crit_defense, format_colorful)
        werte_ws.write_row("M36", [None, None, None, None, None, None], format_border_top)


        # HP
        format_border_top_left = wb.add_format({"top": 1, "left": 1})
        format_hp_plus_titel = wb.add_format(dict(form_align_center_center, **{"top": 1}))
        format_hp_plus = wb.add_format(dict(form_sub_titel, **{"top": 1}))
        format_hp = wb.add_format(dict(form_sub_titel, **form_cell_border, **{"bg_color": COLOR["green"], "font_size": 12}))
        werte_ws.write("M36", "HP +", format_hp_plus_titel)
        werte_ws.write("N36", char.HPplus_fix if char.HPplus_fix is not None else char.HPplus, format_hp_plus)
        werte_ws.write("M37", "Rang HP", format_align_center_center)
        werte_ws.write("N37", char.rang, format_sub_titel)
        werte_ws.write("M38", "HP", format_section_titel)
        werte_ws.write("N38", "=N36+(N37/10)+(L25*2)+(N5*5)", format_hp)
        werte_ws.write("M39", "gHP", format_section_titel)
        werte_ws.write("N39", "=N9*5"+(f"+{char.HPplus_geistig}"if char.HPplus_geistig else ""), format_hp)
        werte_ws.write_row("M40", [None, None], format_border_top)
        werte_ws.write(f"O36", None, format_border_top_left)
        for i in range(37, 40):
            werte_ws.write(f"O{i}", None, format_border_left)



        # Attrs
        format_attr_titel = wb.add_format(dict(form_sub_titel, **{"bg_color": COLOR["grau 4"], "top": 1}))
        format_attr = wb.add_format(dict(form_align_center_center, **{"bg_color": COLOR["grau 4"], "font_size": 12, "left": 1}))
        format_attr_basis = wb.add_format(dict(form_section_titel, **{"bg_color": COLOR["grau 1"], "font_size": 12}))
        format_attr_bonus = wb.add_format(dict(form_italic, **form_align_center_center, **{"bg_color": COLOR["grau 2"]}))
        format_attr_max = wb.add_format(dict(form_sub_titel, **form_align_center_center, **{"bg_color": COLOR["light-blue"], "font_size": 12, "right": 1}))
        format_fert_attr = wb.add_format(dict(form_align_bottom_center, **form_cell_border, **{"font_size": 16}))
        format_fert_attr__odd = wb.add_format(dict(form_align_bottom_center, **form_cell_border, **{"font_size": 16, "bg_color": COLOR["grau 1"]}))
        format_fert_ap = wb.add_format(dict(form_align_bottom_center, **form_bold, **form_italic, **form_cell_border, **{"font_size": 18, "bg_color": COLOR["grau 1"]}))
        format_fg = wb.add_format(dict(form_align_bottom_center, **form_cell_border, **{"font_size": 14, "bg_color": COLOR["grau 1"]}))

        werte_ws.write_row(1, 10, ["Attribut", "Basis", "Bonus", "Wert", "Max."], format_attr_titel)
        for attr in char.relattribut_set.values("fg", titel=F("attribut__titel"), basis=F("aktuellerWert"), bonus=F("aktuellerWert_bonus"), max=F("maxWert")):
            # attr
            row = split_position(POSITION[attr["titel"]])
            row_num = row["num"]
            werte_ws.write(row_num-1, 10, attr["titel"], format_attr)
            werte_ws.write(row_num-1, 11, attr["basis"], format_attr_basis)
            werte_ws.write(row_num-1, 12, attr["bonus"], format_attr_bonus)
            werte_ws.write(row_num-1, 13, f'=L{row_num} + M{row_num}', format_attr_basis)
            werte_ws.write(row_num-1, 14, attr["max"], format_attr_max)

            if "MA" in attr["titel"]:
                werte_ws.write(row_num-1, 10, '=IF(P10 = 0,"MA","MG")', format_attr)
                werte_ws.write(row_num-1, 13, f'=L{row_num} + M{row_num} - ROUND(IF(P10 = 0,10-L22,0))', format_attr_basis)

            # fg
            fg_row = split_position(POSITION[f'fg_{attr["titel"]}'])
            fg_alpha = fg_row["alpha"]
            fg_num = fg_row["num"]
            werte_ws.merge_range(f"B{fg_num}:B{fg_num+2}", f"=K{row['num']}", format_fert_attr if fg_num%2 == 0 else format_fert_attr__odd)
            werte_ws.merge_range(f"C{fg_num}:C{fg_num+2}", f"={row['alpha']}{row['num']}", format_fert_ap)
            werte_ws.merge_range(f"{fg_alpha}{fg_num}:{fg_alpha}{fg_num+2}", attr["fg"], format_fg)


        # Fertigkeiten
        format_fert_heading = wb.add_format(dict(form_section_titel, **form_cell_border, **{"font_size": 12}))
        format_fert_titel = wb.add_format(dict(form_align_center_center, **form_cell_border, **{"font_size": 8}))
        format_fert_fp = wb.add_format(dict(form_align_center_center, **form_cell_border, **{"font_size": 12, "bg_color": COLOR["lavender"]}))
        format_fert_fp_bonus = wb.add_format(dict(form_align_center_center, **form_cell_border))
        format_fert_limit = wb.add_format(dict(form_sub_titel, **form_italic, **form_cell_border, **{"font_size": 12}))
        format_fert_pool = wb.add_format(dict(form_sub_titel, **form_cell_border, **{"font_size": 12, "bg_color": COLOR["grau 1"]}))
        
        werte_ws.write_row("A2", ["Fertigkeit", "Attribut", "AP", "FP", "+", "FG", "Pool", "Limit"], format_fert_heading)
        werte_ws.write_row("A33", ["Fertigkeit", "Attribute", "CP1", "CP2", "FP", "+", "Pool", "Limit"], format_fert_heading)
        for fert in char.relfertigkeit_set.values("fertigkeit__titel", "fertigkeit__limit", "fp", "fp_bonus", attr1=F("fertigkeit__attr1__titel"), attr2=F("fertigkeit__attr2__titel")):
            row= split_position(POSITION[fert["fertigkeit__titel"]])["num"]

            werte_ws.write(f"A{row}", fert["fertigkeit__titel"], format_fert_titel)
            werte_ws.write(f"{'D' if not fert['attr2']  else 'E'}{row}", fert["fp"], format_fert_fp)
            werte_ws.write(f"{'E' if not fert['attr2']  else 'F'}{row}", fert["fp_bonus"], format_fert_fp_bonus)
            werte_ws.write(f"H{row}", fert["fertigkeit__limit"], format_fert_limit)

            if fert['attr2']:
                werte_ws.write(f"B{row}", f"{fert['attr1']} + {fert['attr2']}", format_fert_titel)
                werte_ws.write(f"C{row}", f"={POSITION[fert['attr1']]}", format_fert_titel)
                werte_ws.write(f"D{row}", f"={POSITION[fert['attr2']]}", format_fert_titel)
                werte_ws.write(f"G{row}", f"=SUM(C{row}:F{row})", format_fert_pool)

            else:
                werte_ws.write(f"G{row}", f"=C{row - row%3} + D{row} + E{row} + F{row - row%3}", format_fert_pool)


        # Ramsch & Inventar
        format_ramsch_titel = wb.add_format(dict(form_section_titel, **form_cell_border))
        format_large_cell = wb.add_format(dict(form_text_wrap, **form_cell_border, **form_align_top_left))
        format_text_wrap = wb.add_format(form_text_wrap)
        for i in range(45, 144):
            werte_ws.write(f"A{i}", None, format_border_left)
            werte_ws.write(f"H{i}", None, format_border_right)


        # Gfs-Fähigkeiten
        werte_ws.merge_range("A44:H44", "Wesen-Eigenschaften/Fähigkeiten", format_ramsch_titel)
        if char.gfs:
            for i, r in enumerate(RelGfsAbility.objects.filter(char=char)):
                werte_ws.write(f"A{45+i}", r.ability.name, format_border_left)
                werte_ws.merge_range(f"B{45+i}:G{45+i}", r.ability.beschreibung, format_text_wrap)
        # Zauber, Rituale & Runen
        werte_ws.merge_range("A55:H55", "Zauber, Rituale und Runen", format_ramsch_titel)
        for i, r in enumerate(char.relzauber_set.all()[:8]):
            werte_ws.write_row(f"A{56+i}", [r.item.name], format_border_left)
        for i, r in enumerate(char.relrituale_runen_set.all()[:8]):
            werte_ws.write_row(f"D{56+i}", [r.anz, r.item.name, f"Stufe {r.stufe}"])
        # Talente
        werte_ws.merge_range("A64:H64", "Talente", format_ramsch_titel)
        for i, r in enumerate(char.reltalent_set.all()[:3]):
            werte_ws.write_row(f"A{65+i}", [r.talent.titel], format_border_left)
        # Wesenkraft
        werte_ws.merge_range("A68:H68", "Wesenkräfte", format_ramsch_titel)
        for i, r in enumerate(char.relwesenkraft_set.all()[:3]):
            werte_ws.write_row(f"A{69+i}", [r.wesenkraft.titel], format_border_left)
        # Items
        werte_ws.merge_range("A72:H72", "Items", format_ramsch_titel)
        for i, r in enumerate(char.relitem_set.all()[:10]):
            werte_ws.write(f"A{73+i}", r.anz, format_border_left)
            werte_ws.write(f"B{73+i}", r.item.name)
        # Waffen & Werkzeuge
        werte_ws.merge_range("A83:H83", "Waffen & Werkzeuge", format_ramsch_titel)
        for i, r in enumerate(char.relwaffen_werkzeuge_set.all()[:8]):
            werte_ws.write(f"A{84+i}", r.anz, format_border_left)
            werte_ws.write(f"B{84+i}", r.item.name)
        # Schusswaffen
        werte_ws.merge_range("A92:H92", "Schusswaffen", format_ramsch_titel)
        for i, r in enumerate(char.relschusswaffen_set.all()[:8]):
            werte_ws.write(f"A{93+i}", r.anz, format_border_left)
            werte_ws.write_row(f"B{93+i}", [r.item.name, f"BS {r.item.bs} ({r.item.erfolge} Erfolge)", f"ZS {r.item.zs}", f"Präzi {r.item.präzision}"])
        # Ausrüstung & Technik
        werte_ws.merge_range("A101:H101", "Ausrüstung und Technische Geräte", format_ramsch_titel)
        for i, r in enumerate(char.relausrüstung_technik_set.all()[:8]):
            werte_ws.write(f"A{102+i}", r.anz, format_border_left)
            werte_ws.write(f"B{102+i}", r.item.name)
        # TODO ?
        werte_ws.merge_range("A107:H107", "Holoboard & Zubehör", format_ramsch_titel)
        # Einbauten
        werte_ws.merge_range("A113:H113", "Cyber- und Bioware", format_ramsch_titel)
        for i, r in enumerate(char.releinbauten_set.all()[:8]):
            werte_ws.write(f"A{114+i}", r.anz, format_border_left)
            werte_ws.write(f"B{114+i}", r.item.name)

        # Affektivität
        werte_ws.merge_range("A122:H122", "Personen, Begleiter und Haustiere", format_ramsch_titel)
        werte_ws.write_row("A123", ["Name", "Wert", "Grad"], format_ramsch_titel)
        werte_ws.merge_range("D123:E123", "UM", format_ramsch_titel)
        werte_ws.merge_range("F123:H123", "Notizen", format_ramsch_titel)
        personen_aff = char.affektivität_set.values_list("name", "wert", Value("?"), Value("?"), "notizen")
        for i in range(0, 11):
            index = 124+i
            a = personen_aff[i] if i < len(personen_aff) else None

            werte_ws.write(f"A{index}", a[0] if a is not None else None, format_border_left_right)
            werte_ws.write_row(f"B{index}", a[1:3] if a is not None else [None, None], format_border_right)
            werte_ws.merge_range(f"D{index}:E{index}", a[3] if a is not None else None, format_border_right)
            werte_ws.merge_range(f"F{index}:H{index}", a[4] if a is not None else None, format_border_right)
        # Notizen
        notizen = []
        if char.notizen: notizen.append(char.notizen)
        if char.wesenschaden_waff_kampf:
            notizen.append(f"+{char.wesenschaden_waff_kampf} HP im waffenlosen Kampf")
        if char.wesenschaden_andere_gestalt:
            notizen.append(f"+{char.wesenschaden_andere_gestalt} HP im waffenlosen Kampf der anderen Gestalt")
        if "skilltree" in char.processing_notes:
            for s in char.processing_notes["skilltree"]: notizen.append(s)

        werte_ws.merge_range("A135:H135", "Notizen", format_ramsch_titel)
        werte_ws.merge_range("A136:H143", "\n".join(notizen), format_large_cell)




        # Geld, HP, Mana
        geld_ws = wb.add_worksheet("Geld, HP, Mana")

        format_mana_titel = wb.add_format(dict(form_section_titel, **{"font_size": 14}))
        format_money_spent = wb.add_format(dict(form_align_center_center, **{"font_size": 12, "bg_color": COLOR["red"]}))
        format_money_received = wb.add_format(dict(form_align_center_center, **{"font_size": 12, "bg_color": COLOR["green"]}))


        # hp
        format_hp = wb.add_format(dict(form_sub_titel, **form_cell_border, **{"bg_color": COLOR["green"], "font_size": 12}))
        format_border_bottom_left = wb.add_format({"bottom": 1, "left": 1})
        format_border_bottom_right = wb.add_format({"bottom": 1, "right": 1})
        geld_ws.write("H1", "HP Max.", format_ramsch_titel)
        geld_ws.write("I1", "=Werte!N38", format_hp)
        geld_ws.merge_range("J1:K1", "Geistige HP Max.", format_section_titel)
        geld_ws.write("L1", "=Werte!N39", format_hp)

        geld_ws.write("G2", "Schaden", format_section_titel)
        geld_ws.write("G5", "Bonus", format_section_titel)

        geld_ws.write("H13", "HP aktuell", format_section_titel)
        geld_ws.write("I13", "=I1+SUM(H5:I12)-SUM(H2:I4)", format_konz)
        geld_ws.write("H14", "Malus (ab %)", format_section_titel)
        geld_ws.write("I14", "=ROUND(I13/I1*100)")
    
        geld_ws.write("J13", "HP aktuell", format_section_titel)
        geld_ws.write("K13", "=L1+SUM(J5:L12)-SUM(J2:L4)", format_konz)
        geld_ws.write("J14", "Malus (ab %)", format_section_titel)
        geld_ws.write("K14", "=ROUND(K13/L1*100)")

        geld_ws.write_row("H2", [None, None, None, None, None], format_border_top)
        geld_ws.write_row("H5", [None, None, None, None, None], format_border_top)
        geld_ws.write_row("H5", [None, None, None, None, None], format_border_top)
        geld_ws.write_row("H12", [None, None, None, None, None], format_border_bottom)
        for i in range(2, 13):
            if i in [4, 12]:
                geld_ws.write(f"H{i}", None, format_border_bottom_left)
                geld_ws.write(f"I{i}", None, format_border_bottom_right)
                geld_ws.write(f"L{i}", None, format_border_bottom_right)
            else:
                geld_ws.write(f"H{i}", None, format_border_left)
                geld_ws.write(f"I{i}", None, format_border_right)
                geld_ws.write(f"L{i}", None, format_border_right)

        # mana
        format_manaoverflow = wb.add_format(dict(form_align_bottom_center, **form_bold, **form_italic, **{"font_size": 18, "bg_color": COLOR["grau 1"]}))
        geld_ws.merge_range("H17:I18", "Manaverbrauch", format_mana_titel)
        geld_ws.merge_range("J17:J18", "=SUM(H19:M27)", format_konz)
        geld_ws.merge_range("K17:L18", "Manaoverflow", format_sub_titel)
        geld_ws.merge_range("M17:M18", "=Werte!P33", format_manaoverflow)

        geld_ws.write_row("H19", [None, None, None, None, None, None], format_border_top)
        geld_ws.write_row("H28", [None, None, None, None, None, None], format_border_top)
        for i in range(19, 28):
            geld_ws.write(f"G{i}", None, format_border_right)
            geld_ws.write(f"N{i}", None, format_border_left)


        # money left
        geld_ws.write("A2", "Geld max.", format_section_titel)
        geld_ws.write("A3", 15000000, format_manaoverflow) # TODO ?
        geld_ws.write("A4", "Kontostand", format_section_titel)
        geld_ws.write("A5", "=SUM(E2:E1000)-SUM(C2:C1000)", format_konz)
        geld_ws.write("A6", "=ROUND(A5/A3*100)", format_align_center_center)

        # money center
        format_money_reason = wb.add_format(dict(form_align_center_center, **{"right": 1}))

        geld_ws.merge_range("C1:D1", "Ausgaben", format_fert_heading)
        geld_ws.merge_range("E1:F1", "Einnahmen", format_fert_heading)
        geld_ws.write("E2", char.geld, format_money_received)
        geld_ws.write("F2", "aktuelles Guthaben", format_money_reason)
        geld_ws.write("B1", None, format_border_bottom)
        for i in range(0, 1000):
            geld_ws.write(f"B{2+i}", i+1, format_border_left_right)
            geld_ws.write(f"C{2+i}", None, format_money_spent)
            geld_ws.write(f"D{2+i}", None, format_money_reason)
            if i:
                geld_ws.write(f"E{2+i}", None, format_money_received)
                geld_ws.write(f"F{2+i}", None, format_money_reason)








        # Spezial- & Wissensfertigkeiten
        spF_wF_ws = wb.add_worksheet("Wissen & Spezi.")

        format_wissen_attr = wb.add_format(dict(form_align_center_center, **{"font_size": 8}))
        format_wissen_dice = wb.add_format(dict(form_sub_titel, **{"font_size": 12}))
        format_wissen_wert = wb.add_format(dict(form_sub_titel, **{"font_size": 12, "bg_color": COLOR["grau 1"]}))
        format_spezial_gesamt = wb.add_format(dict(form_sub_titel, **{"font_size": 12}))
        format_spezial_korrektur = wb.add_format(dict(form_align_center_center, **form_italic, **{"font_size": 12, "bg_color": COLOR["grau 1"]}))
        format_spezial_wp = wb.add_format(dict(form_align_center_center, **{"font_size": 12}))

        # Wissensfertigkeiten
        spF_wF_ws.write_row(0, 0, ['Wissensfertigkeit', 'Attribute', 'Fertigkeit', 'WP', 'Schwellwert'], format_section_titel)
        wissen_qs = Wissensfertigkeit.objects.prefetch_related("fertigkeit", "attr1", "attr2", "attr3").annotate(
                        attr=Concat(F("attr1__titel"), Value(' + '), F("attr2__titel"), Value(' + '), F("attr3__titel"), output_field=CharField()),
                        wp=Subquery(RelWissensfertigkeit.objects.filter(wissensfertigkeit=OuterRef("id"), char=char)[:1].values("stufe")),
                    )

        for i, wissen in enumerate(wissen_qs):
            ferts = " + ".join([s.titel for s in wissen.fertigkeit.all()])
            wert = "+".join([POSITION[e] for e in [*wissen.attr.split(" + "), *ferts.split(" + ")]])

            spF_wF_ws.write(f"A{i+2}", wissen.titel, format_align_center_center)
            spF_wF_ws.write(f"B{i+2}", wissen.attr, format_wissen_attr)
            spF_wF_ws.write(f"C{i+2}", ferts, format_align_center_center)
            spF_wF_ws.write(f"D{i+2}", wissen.wp, format_wissen_dice)
            spF_wF_ws.write(f"E{i+2}", f'={wert}+{Wissensfertigkeit.WISSENSF_STUFENFAKTOR}*D{i+2}', format_wissen_wert)


        # spezialfertigkeiten
        spF_wF_ws.write_row(0, 6, ['Spezialfertigkeit', 'Attribute', 'Gesamt', 'Ausgleich', 'Korr.', 'WP', 'W20 Probe'], format_section_titel)
        spezial_qs = Spezialfertigkeit.objects.annotate(
                        attr=Concat(F("attr1__titel"), Value(' + '), F("attr2__titel"), output_field=CharField()))

        for i, spezial in enumerate(spezial_qs):
            attr_wert = "+".join([POSITION[attr] for attr in spezial.attr.split(" + ")])
            ausgleich = " + ".join([fert["titel"] for fert in spezial.ausgleich.values("titel")])
            fert_wert = "+".join([POSITION[fert] for fert in ausgleich.split(" + ")])
            wp_query = spezial.relspezialfertigkeit_set.filter(char=char).values("stufe")
            wp = wp_query.first()["stufe"] -5 if wp_query.exists() else None

            spF_wF_ws.write(f"G{i+2}", spezial.titel, format_align_center_center)
            spF_wF_ws.write(f"H{i+2}", spezial.attr, format_wissen_attr)
            spF_wF_ws.write(f"I{i+2}", f'={attr_wert}', format_spezial_gesamt)
            spF_wF_ws.write(f"J{i+2}", ausgleich, format_wissen_attr)
            spF_wF_ws.write(f"K{i+2}", f'=ROUND(({fert_wert})/2)', format_spezial_korrektur)
            spF_wF_ws.write(f"L{i+2}", wp, format_spezial_wp)
            spF_wF_ws.write(f"M{i+2}", f'=I{i+2} + L{i+2}', format_wissen_wert)

        # highlight owned
        format_spF_wF_blank = wb.add_format({"bg_color": COLOR["magenta"]})
        format_spF_wF_nonblank = wb.add_format({"bg_color": COLOR["green"]})
        spF_wF_ws.conditional_format(f'D2:D{wissen_qs.count()+1}', {'type': 'blanks', 'format': format_spF_wF_blank})
        spF_wF_ws.conditional_format(f'D2:D{wissen_qs.count()+1}', {'type': 'no_blanks', 'format': format_spF_wF_nonblank})
        spF_wF_ws.conditional_format(f'L2:L{spezial_qs.count()+1}', {'type': 'blanks', 'format': format_spF_wF_blank})
        spF_wF_ws.conditional_format(f'L2:L{spezial_qs.count()+1}', {'type': 'no_blanks', 'format': format_spF_wF_nonblank})









        # set Width of columns
        for ws in wb.worksheets(): ws.autofit()
        werte_ws.set_column("A:A", 25)
        werte_ws.set_column("B:B", 12)
        werte_ws.set_column("C:H", 6)
        werte_ws.set_column("J:J", 5)
        werte_ws.set_column("K:K", 10)
        werte_ws.set_column("L:O", 8)
        werte_ws.set_column("P:R", 3)
        
        spF_wF_ws.set_column("D:D", 10)
        spF_wF_ws.set_column("E:E", 15)
        spF_wF_ws.set_column("H:H", 10)
        spF_wF_ws.set_column("I:I", 10)
        spF_wF_ws.set_column("J:J", 25)
        spF_wF_ws.set_column("K:K", 7)
        spF_wF_ws.set_column("L:L", 5)
        spF_wF_ws.set_column("M:M", 12)
        
        geld_ws.set_column("A:A", 20)
        geld_ws.set_column("D:D", 35)
        geld_ws.set_column("F:F", 35)
        geld_ws.set_column("G:G", 10)
        geld_ws.set_column("H:H", 15)
        geld_ws.set_column("J:J", 15)



        chart = wb.add_chart({'type': 'radar', 'subtype': 'filled'})
        chart.set_legend({'none': True})
        chart.add_series({
            'categories': '=Werte!$K$3:$K$12',
            'values':     '=Werte!$O$3:$O$12',
            'border': {'color': 'black'},
            'fill':       {
                'color': COLOR["diagram-red"],
                'transparency': 15,
            },
        })
        chart.add_series({
            'categories': '=Werte!$K$3:$K$12',
            'values':     '=Werte!$N$3:$N$12',
            'border': {'color': 'black'},
            'fill':       {
                'color': COLOR["diagram-blue"],
                'transparency': 15,
            },
        })
        werte_ws.insert_chart('S1', chart)
        
        # construct response
        wb.close()
        return response