import json, xlsxwriter, re

from io import BytesIO

from django.db.models.functions import Concat
from django.db.models import F, Subquery, OuterRef, Value, CharField
from django.http import HttpResponse

from character.models import *
from log.models import Log
from ppServer.utils import ConcatSubquery

class CharakterExporter:
    COLOR = {
        "black": "#000000",
        "grau 1": "#b2b2b2",
        "grau 2": "#dddddd",
        "grau 3": "#eeeeee",
        "white": "#ffffff",

        "green": "#66ff66",
        "red": "#ff9999",
        "red-font": "#fe3349",
        "orange-yellow": "#ffcc00",
        "blue-pastel": "#cfe7f5",
        "yellow-pastel": "#ffffcc",
        "green-pastel": "#99ffcc",
        "lavender-pastel": "#ffccff",
    }


    def __init__(self, char: Charakter):
        self.char = char
        self._POSITION = {}

        self._generate()

    def export(self) -> HttpResponse:
        return self.response

    def _generate(self):

        # prepare response & xlsx-workbook
        self.response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.response['Content-Disposition'] = f"attachment; filename={self.char.name}.xlsx"
        wb = xlsxwriter.Workbook(self.response, {'in_memory': True, "default_format_properties": {
            "font_name": "Arial",
            "font_size": 10,
            'num_format': '#,##0.#'
        }})


        # werte/front page
        werte_ws = wb.add_worksheet("Werte")

        werte_ws = self._attrs(wb, werte_ws)
        werte_ws, ROW_AFTER_FERTS = self._ferts(wb, werte_ws)

        werte_ws = self._top_line(wb, werte_ws)
        werte_ws, ROW_LOWER_HALF, ROW_AFTER_CENTER = self._center(wb, werte_ws)
        werte_ws = self._right_off(wb, werte_ws)
        werte_ws = self._colorful_dice(wb, werte_ws, ROW_LOWER_HALF)
        werte_ws = self._hp(wb, werte_ws, ROW_AFTER_CENTER)
        werte_ws = self._fields_below_ferts(wb, werte_ws, ROW_AFTER_FERTS)
        werte_ws = self._media(wb, werte_ws)

        # other sheets
        geld_ws = self._geld_hp_mana_ws(wb)
        spF_wF_ws = self._sp_wi_ws(wb)
        self._history_ws(wb)


        # # set Width of columns
        # for ws in wb.worksheets(): ws.autofit()
        werte_ws.set_column("A:A", 25)
        werte_ws.set_column("B:B", 12)
        werte_ws.set_column("C:F", 6)
        werte_ws.set_column("G:G", 14)
        werte_ws.set_column("H:H", 6)
        werte_ws.set_column("I:I", 20)
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

        
        # construct response
        wb.close()


    # UTILS

    def _position(self, key: str):
        return self._POSITION[key] if key in self._POSITION else ""
    
    def _split_position(self, key: str):
        pos = self._position(key)
        if not pos: return {"ws": None, "alpha": None, "num": 0}

        ws, cell = pos.split("!")
        alpha = re.search("[A-Z]+", cell)[0]
        num = int(re.search(r"\d+", cell)[0])

        return {"ws": ws, "alpha": alpha, "num": num}



    def _attrs(self, wb, werte_ws):
        # format
        format_head =       wb.add_format({'align': 'center', "valign": "vcenter", "bg_color": self.COLOR["grau 1"], 'bold': True, "top": 1})
        format_attr =       wb.add_format({'align': 'center', "valign": "vcenter", "bg_color": self.COLOR["grau 1"], "font_size": 12, "left": 1})
        format_attr_basis = wb.add_format({'align': 'center', "valign": "vcenter", "bg_color": self.COLOR["grau 3"], 'bold': True, 'italic': True, 'underline': True, "font_size": 12})
        format_attr_bonus = wb.add_format({'align': 'center', "valign": "vcenter", "bg_color": self.COLOR["grau 2"], 'italic': True})
        format_attr_sum =   wb.add_format({'align': 'center', "valign": "vcenter", "bg_color": self.COLOR["red"], 'bold': True, 'italic': True, 'underline': True, "font_size": 12})
        format_attr_max =   wb.add_format({'align': 'center', "valign": "vcenter", "bg_color": self.COLOR["blue-pastel"], 'bold': True, "font_size": 12, "right": 1})
        
        # Attrs
        attr_qs = self.char.relattribut_set.values(titel=F("attribut__titel"), basis=F("aktuellerWert"), bonus=F("aktuellerWert_bonus"), basis_fix=F("aktuellerWert_fix"), max=F("maxWert"), max_fix=F("maxWert_fix"))
        ROW = max(1, 3 - len(attr_qs) +10)
        ROW_INITIAL = ROW
        
        werte_ws.write_row(f"K{ROW}", ["Attribut", "Basis", "Bonus", "Wert", "Max."], format_head)
        for attr in attr_qs:
            # attr
            ROW += 1
            self._POSITION[attr["titel"]] = f"Werte!N{ROW}"

            werte_ws.write(f"K{ROW}", "MG" if attr["titel"] == "MA" and self.char.no_MA and not self.char.no_MA_MG else attr["titel"], format_attr)
            werte_ws.write(f"L{ROW}", attr["basis"] if attr["basis_fix"] is None else attr["basis_fix"], format_attr_basis)
            werte_ws.write(f"M{ROW}", attr["bonus"] if attr["basis_fix"] is None else 0, format_attr_bonus)
            werte_ws.write(f"N{ROW}", f'=$L{ROW} + $M{ROW}', format_attr_sum)
            werte_ws.write(f"O{ROW}", attr["max"] if attr["max_fix"] is None else attr["max_fix"], format_attr_max)

        self._POSITION["attr_labels"] =  f"Werte!$K${ROW_INITIAL+1}:$K${ROW}"
        self._POSITION["attr_werte"] =   f"Werte!$N${ROW_INITIAL+1}:$N${ROW}"
        self._POSITION["attr_max"] =     f"Werte!$O${ROW_INITIAL+1}:$O${ROW}"

        return werte_ws


    def _ferts(self, wb, werte_ws):
        # format
        format_heading =    wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 12, 'bold': True, 'italic': True, 'underline': True})
        format_titel =      wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 12, "bold": True})
        format_titel_expert = wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 12, "bold": True, "italic": True, "font_color": self.COLOR["red-font"]})
        format_attribut =   wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 14})
        format_fp =         wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 12, "bold": True, "bg_color": self.COLOR["blue-pastel"]})
        format_fg =         wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 16, 'bold': True, "bg_color": self.COLOR["yellow-pastel"]})
        format_fp_bonus =   wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 12, "bold": True, "bg_color": self.COLOR["green-pastel"]})
        format_pool =       wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 14, 'bold': True, "bg_color": self.COLOR["lavender-pastel"]})
        format_gruppe =     wb.add_format({'align': 'center', "valign": "vcenter", "border": 1, "font_size": 10, 'bold': True})
        
        # Fertigkeiten & Klassen
        ROW = 3
        klassen = {k.klasse.titel: k.stufe for k in self.char.relklasse_set.prefetch_related("klasse").all()}

        werte_ws.write_row(f"A{ROW}", ["Fertigkeit", "Attribut", "FP", "FG", "Bonus", "Pool", "FG-Klassenname", "Klassenstufe"], format_heading)
        gruppen = {rel.gruppe: rel for rel in self.char.relgruppe_set.all()}
        for i, fert in enumerate(self.char.relfertigkeit_set.values("fertigkeit__titel", "fertigkeit__impro_possible", "fp", "fp_bonus", "fertigkeit__gruppe", attribut=F("fertigkeit__attribut__titel"))):
            ROW += 1
            
            # Klassen
            is_first_of_gruppe = i % 3 == 0
            if is_first_of_gruppe:
                relgruppe = gruppen[fert["fertigkeit__gruppe"]]
                klasse_name = relgruppe.get_gruppe_display()

                werte_ws.merge_range(f"D{ROW}:D{ROW+2}", relgruppe.fg, format_fg)
                werte_ws.merge_range(f"G{ROW}:G{ROW+2}", klasse_name, format_gruppe)
                werte_ws.merge_range(f"H{ROW}:H{ROW+2}", klassen[klasse_name] if klasse_name in klassen else 0, format_gruppe)

            self._POSITION[fert["fertigkeit__titel"]] = f"F{ROW}"

            werte_ws.write(f"A{ROW}", fert["fertigkeit__titel"], format_titel if fert["fertigkeit__impro_possible"] else format_titel_expert)
            werte_ws.write(f"B{ROW}", "MG" if fert["attribut"] == "MA" and self.char.no_MA and not self.char.no_MA_MG else fert["attribut"], format_attribut)
            werte_ws.write(f"C{ROW}", fert["fp"], format_fp)
            werte_ws.write(f"E{ROW}", fert["fp_bonus"], format_fp_bonus)
            werte_ws.write(f"F{ROW}", f"={self._position(fert['attribut'])} + C{ROW} + D{ROW - i%3} + E{ROW}", format_pool)

        return werte_ws, ROW+1


    def _top_line(self, wb, werte_ws):
        # format
        format_titel = wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_color": self.COLOR["red-font"]})
        format_content = wb.add_format({"valign": "vcenter", 'bold': True, "font_size": 12})

        # top line
        werte_ws.merge_range("A1:A2", 'Charakter:', format_titel)
        werte_ws.merge_range("B1:D2", self.char.name if self.char.name else "<NO NAME>", format_content)
        werte_ws.merge_range("E1:F2", "Spieler:", format_titel)
        werte_ws.merge_range("G1:H2", self.char.eigentümer.__str__() if self.char.eigentümer else None, format_content)

        return werte_ws


    def _center(self, wb, werte_ws):
        # format
        format_align_center_center =wb.add_format({'align': 'center', "valign": "vcenter"})
        format_border_top =         wb.add_format({"top": 1})
        format_border_bottom =      wb.add_format({"bottom": 1})

        format_gsh_titel =          wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "left": 1})
        format_gsh =                wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "right": 1})
        format_ini_titel =          wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "bg_color": self.COLOR["orange-yellow"], "left": 1})
        format_ini =                wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "bg_color": self.COLOR["orange-yellow"]})

        format_teil_titel =         wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "border": 1, "font_size": 12})
        format_vorteil =            wb.add_format({'text_wrap': True, "border": 1, 'align': 'left', "valign": "top", "bg_color": self.COLOR["green"]})
        format_nachteil =           wb.add_format({'text_wrap': True, "border": 1, 'align': 'left', "valign": "top", "bg_color": self.COLOR["red"]})

        format_zufall =             wb.add_format({'align': 'center', "valign": "vcenter", "border": 1})
        format_sp =                 wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "bg_color": self.COLOR["orange-yellow"]})
        format_manifest =           wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12, "border": 1, "bg_color": self.COLOR["lavender-pastel"]})
        format_currencies =         wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "bg_color": self.COLOR["green"]})
        format_ep =                 wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12, "bg_color": self.COLOR["grau 3"]})
        format_death =              wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "border": 1, "bg_color": self.COLOR["black"], "font_color": self.COLOR["white"]})

        format_wesen_titel =        wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 8, "top": 1, "bottom": 1, "left": 1, "bg_color": self.COLOR["grau 3"]})
        format_wesen =              wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, "top": 1, "bottom": 1, "bg_color": self.COLOR["grau 3"]})
        format_person_titel =       wb.add_format({'align': 'center', "valign": "vcenter", "left": 1})
        format_person_titel__first =wb.add_format({'align': 'center', "valign": "vcenter", "left": 1, "top": 1})
        format_person =             wb.add_format({'align': 'center', "valign": "vcenter", "right": 1})

        # center down
        ROW = 3
        werte_ws.write_row(f"I{ROW-1}", [None, None], format_border_bottom)
        werte_ws.write(f"I{ROW}", "Glück", format_gsh_titel)
        werte_ws.write(f"J{ROW}", self.char.glück, format_gsh)

        ROW += 1
        werte_ws.write(f"I{ROW}", "Sanität", format_gsh_titel)
        werte_ws.write(f"J{ROW}", self.char.sanität, format_gsh)

        ROW += 1
        werte_ws.write(f"I{ROW}", "Humor", format_gsh_titel)
        werte_ws.write(f"J{ROW}", f"={self._position('UM')}*5", format_gsh)

        ROW += 1
        werte_ws.write(f"I{ROW}", "Initiative", format_ini_titel)
        werte_ws.write(f"J{ROW}", f"=2*{self._position('SCH')}+{self._position('WK')}+{self._position('GES')}"+(f"+{self.char.initiative_bonus}" if self.char.initiative_bonus else ""), format_ini)

        ROW = max(ROW+1, int(re.search(r"\d+$", self._position("attr_labels")).group(0)))

        # Vor- & Nachteile
        ROW += 1
        werte_ws.merge_range(f"I{ROW}:I{ROW+2}", "Vorteile", format_teil_titel)
        werte_ws.merge_range(f"J{ROW}:R{ROW+2}", ", ".join([rel.__repr__() for rel in self.char.relvorteil_set.prefetch_related("teil").order_by("teil__titel").filter(will_create=False)]), format_vorteil)

        ROW += 3
        werte_ws.merge_range(f"I{ROW}:I{ROW+2}", "Nachteile", format_teil_titel)
        werte_ws.merge_range(f"J{ROW}:R{ROW+2}", ", ".join([rel.__repr__() for rel in self.char.relnachteil_set.prefetch_related("teil", "attribut", "fertigkeit", "engelsroboter").order_by("teil__titel").filter(will_create=False)]), format_nachteil)

        # continue center down
        ROW += 3
        ROW_LOWER_HALF = ROW        
        werte_ws.write_row(f"I{ROW}", ["Skillpunkte", self.char.sp], format_sp)
        werte_ws.merge_range(f"K{ROW}:L{ROW}", "Zufall: 12 (SW = 4)", format_zufall)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "EP", format_align_center_center)
        werte_ws.write(f"J{ROW}", self.char.ep, format_ep)

        ROW += 1
        self._POSITION["ep_stufe"] = f"Werte!J{ROW}"
        werte_ws.write(f"I{ROW}", "Stufe", format_align_center_center)
        werte_ws.write(f"J{ROW}", self.char.ep_stufe, format_ep)
        werte_ws.merge_range(f"K{ROW-1}:L{ROW-1}", "Manifest", format_manifest)
        werte_ws.merge_range(f"K{ROW}:L{ROW}", self.char.manifest - self.char.sonstiger_manifestverlust if self.char.manifest_fix is None else self.char.manifest_fix, format_manifest)


        # lower half of middle
        ROW += 1
        werte_ws.write(f"I{ROW}", "Lebewesen (Stufe):", format_wesen_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", f"{self.char.gfs.titel if self.char.gfs else '-'} ({self.char.skilltree_stufe})", format_wesen)

        ROW += 1
        werte_ws.write(f"I{ROW}", "Klassen (Stufe):", format_wesen_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", ", ".join([f"{rel.klasse.titel} ({rel.stufe})" for rel in self.char.relklasse_set.prefetch_related("klasse").all()]), format_wesen)

        ROW += 1
        werte_ws.write(f"I{ROW}", "Persönlichkeit:", format_wesen_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.persönlichkeit.titel if self.char.persönlichkeit else None, format_wesen)

        ROW += 1
        werte_ws.write(f"I{ROW}", "Gewicht:", format_person_titel__first)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", f"{self.char.gewicht} kg", format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Größe:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", f"{self.char.größe} cm", format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Alter:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", f"{self.char.alter}", format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Geschlecht:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.geschlecht, format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Sexualität:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.sexualität, format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Beruf:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.beruf.titel if self.char.beruf else "", format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Präf. Arm:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.präf_arm, format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Religion:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.religion.titel if self.char.religion else "", format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Hautfarbe:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.hautfarbe, format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Haarfarbe:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.haarfarbe, format_person)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Augenfarbe:", format_person_titel)
        werte_ws.merge_range(f"J{ROW}:L{ROW}", self.char.augenfarbe, format_person)

        werte_ws.write_row(f"I{ROW+1}", [None, None, None, None], format_border_top)

        return werte_ws, ROW_LOWER_HALF, ROW+1


    def _colorful_dice(self, wb, werte_ws, ROW):
        # format
        format_colorful_titel =      wb.add_format({'align': 'center', "valign": "vcenter", 'italic': True, "left": 1})
        format_colorful_titel_emph = wb.add_format({'align': 'center', "valign": "vcenter", 'italic': True, 'bold': True, "left": 1})
        format_colorful =            wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "right": 1})

        # colorful dice
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "physische Reaktion", format_colorful_titel_emph)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('SCH')}+{self._position('GES')}"+(f"+{self.char.reaktion_bonus}" if self.char.reaktion_bonus else ""), format_colorful)
        werte_ws.write(f"S{ROW}", "SCH+GES")

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "physischer Widerstand", format_colorful_titel_emph)
        werte_ws.merge_range(f"P{ROW}:Q{ROW}", f"={self._position('ST')}+{self._position('VER')}"+(f"+{self.char.natürlicher_schadenswiderstand_bonus}" or ""), format_colorful)
        werte_ws.write(f"R{ROW}", self.char.natürlicher_schadenswiderstand_bonus_str, format_colorful)
        werte_ws.write(f"S{ROW}", f"ST+VER")

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "astrale Reaktion", format_colorful_titel_emph)
        if self.char.no_MA_MG:
            werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('WK')}+4"+(f"+{self.char.astralwiderstand_bonus}" if self.char.astralwiderstand_bonus else ""), format_colorful)
            werte_ws.write(f"S{ROW}", "WK+4")
            werte_ws.write(f"S{ROW+1}", "WK+4")
        elif self.char.no_MA:
            werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('WK')}"+(f"+{self.char.astralwiderstand_bonus}" if self.char.astralwiderstand_bonus else ""), format_colorful)
            werte_ws.write(f"S{ROW}", "WK")
            werte_ws.write(f"S{ROW+1}", "WK")
        else:
            werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('MA')}+{self._position('WK')}"+(f"+{self.char.astralwiderstand_bonus}" if self.char.astralwiderstand_bonus else ""), format_colorful)
            werte_ws.write(f"S{ROW}", "MA+WK")
            werte_ws.write(f"S{ROW+1}", "MA+WK")

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "astraler Widerstand", format_colorful_titel_emph)
        werte_ws.merge_range(f"P{ROW}:Q{ROW}", f"=P{ROW-1}", format_colorful)
        werte_ws.write(f"R{ROW}", self.char.astralwiderstand_bonus_str, format_colorful)

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Bewegungsrate Laufen (in m)", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self.char.gfs.base_movement_speed}+{self._position('SCH')}+{self.char.speed_laufen_bonus}", format_colorful)
        werte_ws.write(f"S{ROW}", "(Gfs-Basiswert + SCH + Bonus")

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Bewegungsrate Schwimmen (in m)", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"=({self.char.gfs.base_movement_speed}+{self._position('SCH')})/2+{self.char.speed_schwimmen_bonus}", format_colorful)
        werte_ws.write(f"S{ROW}", "(Gfs-Basiswert + SCH)/2 + Bonus")

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Bewegungsrate Fliegen (in m)", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"=({self.char.gfs.base_movement_speed}+{self._position('SCH')})*2+{self.char.speed_fliegen_bonus}", format_colorful)
        werte_ws.write(f"S{ROW}", "(Gfs-Basiswert + SCH)*2 + Bonus")

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Bewegungsrate Astral (in m)", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"=({self.char.gfs.base_movement_speed}+{self._position('SCH')})*4+{self.char.speed_astral_bonus}", format_colorful)
        werte_ws.write(f"S{ROW}", "(Gfs-Basiswert + SCH)*4 + Bonus")

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Tragfähigkeit", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('ST')}*3+{self._position('GES')}", format_colorful)
        werte_ws.write(f"S{ROW}", "ST*3+GES")
        
        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Heben pro Erfolg (kg)", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('ST')}*4+{self._position('N')}", format_colorful)
        werte_ws.write(f"S{ROW}", "ST*4+N")
        
        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Ersticken nach x Sekunden", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('ST')}*3+{self._position('VER')}*3", format_colorful)
        werte_ws.write(f"S{ROW}", "ST*3+VER*3")
        
        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Immunsystem (W100)", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('ST')}*4+{self._position('VER')}*3+{self._position('WK')}*2+{self.char.immunsystem_bonus}", format_colorful)
        werte_ws.write(f"S{ROW}", "ST*4+VER*3+WK*2")
        
        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Glück", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", self.char.glück, format_colorful)
        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Sanität", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", self.char.sanität, format_colorful)

        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Regeneration in HP pro Tag", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"={self._position('ST')}+{self._position('WK')}+{self.char.nat_regeneration_bonus}", format_colorful)
        werte_ws.write(f"S{ROW}", "ST+WK")
        
        ROW += 1
        self._POSITION["manaoverflow"] = f"Werte!P{ROW}"
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Manaoverflow", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", f"=({self._position('WK')}+{self._position('MA')})*3 + {self.char.manaoverflow_bonus}", format_colorful)
        werte_ws.write(f"S{ROW}", "(WK+MA)*3")
        
        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Crit.-Value Angriff", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", self.char.crit_attack, format_colorful)
        
        ROW += 1
        werte_ws.merge_range(f"M{ROW}:O{ROW}", "Crit.-Value Verteidigung", format_colorful_titel)
        werte_ws.merge_range(f"P{ROW}:R{ROW}", self.char.crit_defense, format_colorful)
# werte_ws.write_row("M36", [None, None, None, None, None, None], {"top": 1})

        return werte_ws


    def _hp(self, wb, werte_ws, ROW):
        # format
        format_align_center_center =wb.add_format({'align': 'center', "valign": "vcenter"})
        format_align_border_top =   wb.add_format({'align': 'center', "valign": "vcenter", "top": 1})
        format_section_titel =      wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12})
        format_konz_titel =         wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "border": 1})
        format_konz =               wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "border": 1, "bg_color": self.COLOR["green"], "font_size": 18})
        format_hp =                 wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "border": 1, "bg_color": self.COLOR["green"], "font_size": 12})
        
        # HP
        werte_ws.write(f"I{ROW}", "K HP Bonus", format_align_border_top)
        werte_ws.write(f"J{ROW}", self.char.HPplus_fix if self.char.HPplus_fix is not None else (self.char.HPplus + math.floor(self.char.larp_rang/20)), format_hp)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "Rang HP", format_align_center_center)
        werte_ws.write(f"J{ROW}", math.floor(self.char.rang/10), format_hp)
        
        ROW += 1
        self._POSITION["kHP"] = f"Werte!J{ROW}"
        werte_ws.write(f"I{ROW}", "Körperliche HP", format_section_titel)
        werte_ws.write(f"J{ROW}", f"=J{ROW-2}+J{ROW-1}+({0 if self.char.larp else self._position('ep_stufe')}*2)+({self._position('ST')}*5)", format_hp)
        
        ROW += 1
        werte_ws.write(f"I{ROW}", "G HP Bonus", format_align_center_center)
        werte_ws.write(f"J{ROW}", self.char.HPplus_geistig + math.ceil(self.char.larp_rang/20) + (10 if self.char.no_MA_MG else 0), format_hp)
        
        ROW += 1
        self._POSITION["gHP"] = f"Werte!J{ROW}"
        werte_ws.write(f"I{ROW}", "Geistige HP", format_section_titel)
        werte_ws.write(f"J{ROW}", f"=J{ROW-1}+{self._position('WK')}*5", format_hp)

        ROW += 1
        werte_ws.merge_range(f"I{ROW}:I{ROW+1}", "Konzentration (Max.)", format_konz_titel)
        werte_ws.merge_range(f"J{ROW}:J{ROW+1}", (self.char.konzentration if self.char.konzentration_fix is None else self.char.konzentration_fix) or 0, format_konz)
        werte_ws.merge_range(f"K{ROW}:L{ROW+1}", "1 SP = 2 Konz.")

        werte_ws.merge_range(f"M{ROW-1}:M{ROW}", "TP", format_konz_titel)
        werte_ws.merge_range(f"N{ROW-1}:N{ROW}", self.char.tp or 0, format_konz)
        werte_ws.merge_range(f"O{ROW-1}:O{ROW}", "IP", format_konz_titel)
        werte_ws.merge_range(f"P{ROW-1}:R{ROW}", self.char.ip or 0, format_konz)
        
        return werte_ws


    def _right_off(self, wb, werte_ws):
        # format
        format_prestige_titel = wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "font_size": 12, "border": 1, 'underline': True})
        format_prestige =       wb.add_format({'align': 'center', "valign": "bottom", 'bold': True, "font_size": 14, "border": 1})

        # right off
        werte_ws.merge_range("P3:R3", "Verzehr", format_prestige_titel)
        werte_ws.merge_range("P4:R5", self.char.verzehr, format_prestige)
        werte_ws.merge_range("P6:R6", "Prestige", format_prestige_titel)
        werte_ws.merge_range("P7:R8", self.char.prestige, format_prestige)
        werte_ws.merge_range("P10:R10", "Hat MG?", format_prestige_titel)
        werte_ws.merge_range("P11:R12", 1 if self.char.no_MA and not self.char.no_MA_MG else 0, format_prestige)
        werte_ws.merge_range("P13:R13", "0 = nein, 1 = ja")

        return werte_ws


    def _fields_below_ferts(self, wb, werte_ws, ROW):
        # format
        format_border_left =        wb.add_format({"left": 1})
        format_border_right =       wb.add_format({"right": 1})
        format_border_left_right =  wb.add_format({"left": 1, "right": 1})
        format_ramsch_titel =       wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12, "border": 1})
        format_text_wrap =          wb.add_format({'text_wrap': True, "valign": "top" })
        format_large_cell =         wb.add_format({'text_wrap': True, "valign": "top", "border": 1, 'align': 'left', "valign": "top"})

        # Gfs-Fähigkeiten
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Gfs-Eigenschaften/Fähigkeiten", format_ramsch_titel)
        if self.char.gfs:
            for r in RelGfsAbility.objects.prefetch_related("ability").filter(char=self.char):
                ROW += 1
                werte_ws.write(f"A{ROW}", r.ability.name, format_border_left)
                werte_ws.merge_range(f"B{ROW}:G{ROW}", r.ability.beschreibung, format_text_wrap)
                werte_ws.write(f"H{ROW}", r.notizen, format_border_right)
        # Klassen-Fähigkeiten
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Klassen-Eigenschaften/Fähigkeiten", format_ramsch_titel)
        for r in RelKlasseAbility.objects.prefetch_related("ability").filter(char=self.char):
            ROW += 1
            werte_ws.write(f"A{ROW}", r.ability.name, format_border_left)
            werte_ws.merge_range(f"B{ROW}:G{ROW}", r.ability.beschreibung, format_text_wrap)
            werte_ws.write(f"H{ROW}", r.notizen, format_border_right)
        # Zauber, Rituale & Runen
        ROW += 1
        start_zauberrow = ROW
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Zauber, Rituale und Runen", format_ramsch_titel)
        for r in self.char.relzauber_set.prefetch_related("item").all():
            ROW += 1
            werte_ws.write_row(f"A{ROW}", [r.item.name], format_border_left)
            werte_ws.write_row(f"B{ROW}", [r.tier])
            werte_ws.write(f"H{ROW}", None, format_border_right)
        
        end_zauberrow = ROW
        ROW = start_zauberrow
        for r in self.char.relrituale_runen_set.prefetch_related("item").all():
            ROW += 1
            werte_ws.write(f"D{ROW}", r.anz)
            werte_ws.merge_range(f"E{ROW}:G{ROW}", r.item.name)
            werte_ws.write(f"H{ROW}", f"Stufe {r.stufe}", format_border_right)
        # Talente
        ROW = max(end_zauberrow, ROW) + 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Talente", format_ramsch_titel)
        for r in self.char.reltalent_set.prefetch_related("talent").all():
            ROW += 1
            werte_ws.write_row(f"A{ROW}", [r.talent.titel], format_border_left)
            werte_ws.write(f"H{ROW}", None, format_border_right)
        # Wesenkraft
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Wesenkräfte", format_ramsch_titel)
        for r in self.char.relwesenkraft_set.prefetch_related("wesenkraft").all():
            ROW += 1
            werte_ws.write_row(f"A{ROW}", [r.wesenkraft.titel], format_border_left)
            werte_ws.write_row(f"B{ROW}", [r.tier])
            werte_ws.write(f"H{ROW}", None, format_border_right)
        # Items
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Items", format_ramsch_titel)
        for r in self.char.relitem_set.prefetch_related("item").all():
            ROW += 1
            werte_ws.write(f"A{ROW}", r.anz, format_border_left)
            werte_ws.write(f"B{ROW}", r.item.name)
            werte_ws.write(f"H{ROW}", None, format_border_right)
        # Waffen & Werkzeuge
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Waffen & Werkzeuge", format_ramsch_titel)
        for r in self.char.relwaffen_werkzeuge_set.prefetch_related("item").all():
            ROW += 1
            werte_ws.write(f"A{ROW}", r.anz, format_border_left)
            werte_ws.write(f"B{ROW}", r.item.name)
            werte_ws.write(f"H{ROW}", None, format_border_right)
        # Schusswaffen
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Schusswaffen", format_ramsch_titel)
        for r in self.char.relschusswaffen_set.prefetch_related("item").all():
            ROW += 1
            werte_ws.write(f"A{ROW}", r.anz, format_border_left)
            werte_ws.write_row(f"B{ROW}", [r.item.name, f"BS {r.item.bs}", f"ZS {r.item.zs} ({r.item.erfolge} Erfolge)", f"Präzi {r.item.präzision}"])
            werte_ws.write(f"H{ROW}", None, format_border_right)
        # Ausrüstung & Technik
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Ausrüstung und Technische Geräte", format_ramsch_titel)
        for r in self.char.relausrüstung_technik_set.prefetch_related("item").all():
            ROW += 1
            werte_ws.write(f"A{ROW}", r.anz, format_border_left)
            werte_ws.write(f"B{ROW}", r.item.name)
            werte_ws.write(f"H{ROW}", None, format_border_right)
        # TODO ?
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Holoboard & Zubehör", format_ramsch_titel)
        # Einbauten
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Cyber- und Bioware", format_ramsch_titel)
        for r in self.char.releinbauten_set.prefetch_related("item").all():
            ROW += 1
            werte_ws.write(f"A{ROW}", r.anz, format_border_left)
            werte_ws.write(f"B{ROW}", r.item.name)
            werte_ws.write(f"H{ROW}", None, format_border_right)

        # Affektivität
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Personen, Begleiter und Haustiere", format_ramsch_titel)
        ROW += 1
        werte_ws.write_row(f"A{ROW}", ["Name", "Wert", "Grad"], format_ramsch_titel)
        werte_ws.merge_range(f"D{ROW}:E{ROW}", "UM", format_ramsch_titel)
        werte_ws.merge_range(f"F{ROW}:H{ROW}", "Notizen", format_ramsch_titel)
        personen_aff = self.char.affektivität_set.values_list("name", "wert", Value("?"), "notizen")
        for aff in personen_aff:
            ROW += 1
            werte_ws.write(f"A{ROW}", aff[0] if aff is not None else None, format_border_left_right)
            werte_ws.write_row(f"B{ROW}", aff[1:3] if aff is not None else [None, None], format_border_right)
            werte_ws.merge_range(f"D{ROW}:E{ROW}", "?", format_border_right)
            werte_ws.merge_range(f"F{ROW}:H{ROW}", aff[3] if aff is not None else None, format_border_right)
        # Notizen
        notizen = [self.char.sonstige_items, self.char.notizen]
        if self.char.no_MA_MG:
            notizen.append(f"Verzichtet für immer auf Magie und Managetik.")
        elif self.char.no_MA:
            notizen.append(f"Kann Managetik nutzen und verzichtet für immer auf Magie.")
        if self.char.wesenschaden_waff_kampf:
            notizen.append(f"+{self.char.wesenschaden_waff_kampf} HP im waffenlosen Kampf")
        if self.char.wesenschaden_andere_gestalt:
            notizen.append(f"+{self.char.wesenschaden_andere_gestalt} HP im waffenlosen Kampf der anderen Gestalt")
        if "skilltree" in self.char.processing_notes:
            for s in self.char.processing_notes["skilltree"]: notizen.append(s)

        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW}", "Notizen", format_ramsch_titel)
        ROW += 1
        werte_ws.merge_range(f"A{ROW}:H{ROW+4}", "\n".join([n for n in notizen if n]), format_large_cell)
        ROW += 4

        return werte_ws


    def _media(self, wb, werte_ws):
        self.chart = wb.add_chart({'type': 'radar', 'subtype': 'filled'})
        self.chart.set_legend({'none': True})
        self.chart.add_series({
            'categories': f'={self._position("attr_labels")}',
            'values':     f'={self._position("attr_max")}',
            'border': {'color': 'black'},
            'fill':       {
                'color': self.COLOR["blue-pastel"],
                'transparency': 15,
            },
        })
        self.chart.add_series({
            'categories': f'={self._position("attr_labels")}',
            'values':     f'={self._position("attr_werte")}',
            'border': {'color': 'black'},
            'fill':       {
                'color': self.COLOR["red"],
                'transparency': 15,
            },
        })
        werte_ws.insert_chart('S1', self.chart)

        # add image
        if self.char.image:
            werte_ws.insert_image('S16', 'image name', {'image_data': BytesIO(self.char.image.storage.open(self.char.image.name).read())})

        return werte_ws



    def _sp_wi_ws(self, wb):
        # format
        format_align_center_center =wb.add_format({'align': 'center', "valign": "vcenter"})
        format_section_titel =      wb.add_format({'align': 'center', "valign": "vcenter", "bold": True, "font_size": 12, "italic": True, "underline": True})
        format_wissen_attr =        wb.add_format({'align': 'center', "valign": "vcenter", "font_size": 8})
        format_wissen_dice =        wb.add_format({'align': 'center', "valign": "vcenter", "bold": True, "font_size": 12})
        format_wissen_wert =        wb.add_format({'align': 'center', "valign": "vcenter", "bold": True, "font_size": 12, "bg_color": self.COLOR["grau 1"]})
        format_spezial_korrektur =  wb.add_format({'align': 'center', "valign": "vcenter", 'italic': True, "font_size": 12, "bg_color": self.COLOR["grau 1"]})
        format_spezial_wp =         wb.add_format({'align': 'center', "valign": "vcenter", "font_size": 12})
        format_spF_wF_blank =       wb.add_format({"bg_color": self.COLOR["lavender-pastel"]})
        format_spF_wF_nonblank =    wb.add_format({"bg_color": self.COLOR["green"]})
        format_spezial_gesamt =     format_wissen_dice

        # Spezial- & Wissensfertigkeiten
        spF_wF_ws = wb.add_worksheet("Wissen & Spezi.")


        # Wissensfertigkeiten
        spF_wF_ws.write_row(0, 0, ['Wissensfertigkeit', 'Attribute', 'Fertigkeit', 'WP', 'Schwellwert'], format_section_titel)
        wissen_qs = Wissensfertigkeit.objects.annotate(
                        attr=Concat(F("attr1__titel"), Value(' + '), F("attr2__titel"), Value(' + '), F("attr3__titel"), output_field=CharField()),
                        ferts=ConcatSubquery(Fertigkeit.objects.filter(wissensfertigkeit=OuterRef("pk")).values("titel"), separator=" + "),
                        wp=Subquery(RelWissensfertigkeit.objects.filter(wissensfertigkeit=OuterRef("pk"), char=self.char)[:1].values("stufe")),
                    )

        for i, wissen in enumerate(wissen_qs):
            wert = "+".join([self._position(e) for e in [*wissen.attr.split(" + "), *wissen.ferts.split(" + ")]])

            spF_wF_ws.write(f"A{i+2}", wissen.titel, format_align_center_center)
            spF_wF_ws.write(f"B{i+2}", wissen.attr, format_wissen_attr)
            spF_wF_ws.write(f"C{i+2}", wissen.ferts, format_align_center_center)
            spF_wF_ws.write(f"D{i+2}", wissen.wp, format_wissen_dice)
            spF_wF_ws.write(f"E{i+2}", f'={wert}+{Wissensfertigkeit.WISSENSF_STUFENFAKTOR}*D{i+2}', format_wissen_wert)


        # spezialfertigkeiten
        spF_wF_ws.write_row(0, 6, ['Spezialfertigkeit', 'Attribute', 'Gesamt', 'Ausgleich', 'Korr.', 'WP', 'W20 Probe'], format_section_titel)
        spezial_qs = Spezialfertigkeit.objects.annotate(
            attr=Concat(F("attr1__titel"), Value(' + '), F("attr2__titel"), output_field=CharField()),
            ferts=ConcatSubquery(Fertigkeit.objects.filter(spezialfertigkeit=OuterRef("pk")).values("titel"), separator=" + "),
            wp=Subquery(RelSpezialfertigkeit.objects.filter(spezialfertigkeit=OuterRef("pk"), char=self.char)[:1].values("stufe")),
        )

        for i, spezial in enumerate(spezial_qs):
            attr_wert = "+".join([self._position(attr) for attr in spezial.attr.split(" + ")]) + "-5"
            fert_wert = "+".join([self._position(fert) for fert in spezial.ferts.split(" + ")]) if spezial.ferts else "0"

            spF_wF_ws.write(f"G{i+2}", spezial.titel, format_align_center_center)
            spF_wF_ws.write(f"H{i+2}", spezial.attr, format_wissen_attr)
            spF_wF_ws.write(f"I{i+2}", f'={attr_wert}', format_spezial_gesamt)
            spF_wF_ws.write(f"J{i+2}", spezial.ferts, format_wissen_attr)
            spF_wF_ws.write(f"K{i+2}", f'=ROUND(({fert_wert})/2)', format_spezial_korrektur)
            spF_wF_ws.write(f"L{i+2}", spezial.wp, format_spezial_wp)
            spF_wF_ws.write(f"M{i+2}", f'=I{i+2} + L{i+2}', format_wissen_wert)

        # highlight owned
        spF_wF_ws.conditional_format(f'D2:D{wissen_qs.count()+1}', {'type': 'blanks', 'format': format_spF_wF_blank})
        spF_wF_ws.conditional_format(f'D2:D{wissen_qs.count()+1}', {'type': 'no_blanks', 'format': format_spF_wF_nonblank})
        spF_wF_ws.conditional_format(f'L2:L{spezial_qs.count()+1}', {'type': 'blanks', 'format': format_spF_wF_blank})
        spF_wF_ws.conditional_format(f'L2:L{spezial_qs.count()+1}', {'type': 'no_blanks', 'format': format_spF_wF_nonblank})

        return spF_wF_ws


    def _geld_hp_mana_ws(self, wb):
        format_border_top =         wb.add_format({"top": 1})
        format_border_left =        wb.add_format({"left": 1})
        format_border_right =       wb.add_format({"right": 1})
        format_border_bottom =      wb.add_format({"bottom": 1})
        format_border_left_right =  wb.add_format({"left": 1, "right": 1})
        format_border_bottom_left = wb.add_format({"bottom": 1, "left": 1})
        format_border_bottom_right =wb.add_format({"bottom": 1, "right": 1})

        format_align_center_center =wb.add_format({'align': 'center', "valign": "vcenter"})
        format_ramsch_titel =       wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12, "border": 1})
        format_section_titel =      wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12})
        format_konz =               wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "border": 1, "bg_color": self.COLOR["green"], "font_size": 18})
        format_sub_titel =          wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True})
        format_fert_heading =       wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12, "border": 1, "font_size": 12})
        format_mana_titel =         wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, 'italic': True, 'underline': True, "font_size": 12, "font_size": 14})
        format_money_spent =        wb.add_format({'align': 'center', "valign": "vcenter", "font_size": 12, "bg_color": self.COLOR["red"]})
        format_money_received =     wb.add_format({'align': 'center', "valign": "vcenter", "font_size": 12, "bg_color": self.COLOR["green"]})
        format_hp =                 wb.add_format({'align': 'center', "valign": "vcenter", 'bold': True, "border": 1, "bg_color": self.COLOR["green"], "font_size": 12})
        format_manaoverflow =       wb.add_format({'align': 'center', "valign": "bottom", 'bold': True, 'italic': True, "font_size": 18, "bg_color": self.COLOR["grau 1"]})
        format_money_reason =       wb.add_format({'align': 'center', "valign": "vcenter", "right": 1})



        # Geld, HP, Mana
        geld_ws = wb.add_worksheet("Geld, HP, Mana")

        # hp
        geld_ws.write("H1", "HP Max.", format_ramsch_titel)
        geld_ws.write("I1", f"={self._position('kHP')}", format_hp)
        geld_ws.merge_range("J1:K1", "Geistige HP Max.", format_section_titel)
        geld_ws.write("L1", f"={self._position('gHP')}", format_hp)

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
        geld_ws.merge_range("H17:I18", "Manaverbrauch", format_mana_titel)
        geld_ws.merge_range("J17:J18", "=SUM(H19:M27)", format_konz)
        geld_ws.merge_range("K17:L18", "Manaoverflow", format_sub_titel)
        geld_ws.merge_range("M17:M18", f"={self._position('manaoverflow')}", format_manaoverflow)

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
        geld_ws.merge_range("C1:D1", "Ausgaben", format_fert_heading)
        geld_ws.merge_range("E1:F1", "Einnahmen", format_fert_heading)

        index_received = 2
        index_spent = 2
        for t in [*self.char.card.get_transactions()][::-1]:
            if t.sender == self.char.card:
                geld_ws.write(f"C{index_spent}", t.amount, format_money_spent)
                geld_ws.write(f"D{index_spent}", f"{t.receiver}: {t.reason}" if t.receiver else (t.reason or "-"), format_money_reason)
                index_spent += 1
            else:
                geld_ws.write(f"E{index_received}", t.amount, format_money_received)
                geld_ws.write(f"F{index_received}", f"{t.sender}: {t.reason}" if t.sender else (t.reason or "-"), format_money_reason)
                index_received += 1

        geld_ws.write("B1", None, format_border_bottom)
        for i in range(0, 1000):
            geld_ws.write(f"B{2+i}", i+1, format_border_left_right)
            
        for i in range(index_spent, 1000):
            geld_ws.write(f"C{i}", None, format_money_spent)
            geld_ws.write(f"D{i}", None, format_money_reason)

        for i in range(index_received, 1000):
            geld_ws.write(f"E{i}", None, format_money_received)
            geld_ws.write(f"F{i}", None, format_money_reason)

        return geld_ws

        
    def _history_ws(self, wb):
        # history
        history_ws = wb.add_worksheet("Historie & Debug")
        history_ws.write("A1", json.dumps(self.char.processing_notes))

        history_ws.write_row("A3", ["Spieler", "Art", "Notizen", "Kosten", "Timestamp"])
        for i, log in enumerate(Log.objects.prefetch_related("spieler").filter(char=self.char, art__in=("s", "u", "i"))):
            history_ws.write_row(f"A{4+i}", [log.spieler.__str__() if log.spieler else "", log.get_art_display(), log.notizen, log.kosten, log.timestamp.__str__()])

        return history_ws
