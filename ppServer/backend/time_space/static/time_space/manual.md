# Generelles zum Start
## Ausgabe

Manchmal antworten Phänomene auf einen eingegebenen Befehl. Zur besseren Übersicht werden sie durchnummeriert. Dabei bekommen Linearrisse die ersten Zahlen, der Rest wird von links nach rechts durchnummeriert.

Die Reihenfolge der Antworten ist weitgehend gleich, allerdings sind Runner immer die ersten. Timelagger sinf mit 6-fachem Abstand die letzten.

## Schwierigkeit

Wenn ein Zeitriss oder ein Raumriss einen falschen Befehl bekommt, steigt ihre Stufe um 1. Außerdem kann die Stufe durch andere Trigger steigen, siehe unten.

Wenn die Summe der Stufen aller Phänomene ein Vielfaches von 10 überschreitet, wird ein neues Gatter platziert (bei wachsender Stufe) oder ein Zufälliges entfernt (bei schrumpfender Stufe). 

## Kopplungen

Manche Gatter und Phänomene können sich zusammenkoppeln, weitere Details sind in den entsprechenden Abschnitten weiter unten zu finden.

- Short - beliebiger Zeitriss
- Traceback - Wurmloch
- Manabombe - beliebige Zeitanomalie
- Teleport Input - Teleport Output

### Short mit Liniendeletion

Ein Short - Liniendeletiongespann soll zerstört werden. Existieren allerdings noch Linearrisse, kann die Liniendeletion nicht entfernt werden. In dem Fall wird die Verbindung der Liniendeletion weggenommen und einem zufälligen Linearriss übergeben.
Die Liniendeletion wird dann zerstört.

# Drähte

## von unten

Bild | Zeichen
-|-
<img src="/static/time_space/images/Tile 2.png" style="background: white" loading="lazy"> | `b to t`
<img src="/static/time_space/images/Tile 4.png" style="background: white" loading="lazy"> | `b to l`
<img src="/static/time_space/images/Tile 3.png" style="background: white" loading="lazy"> | `b to r`
<img src="/static/time_space/images/Tile 5.png" style="background: white" loading="lazy"> | `b to lr`
<img src="/static/time_space/images/Tile 6.png" style="background: white" loading="lazy"> | `b to tl`
<img src="/static/time_space/images/Tile 7.png" style="background: white" loading="lazy"> | `b to tr`
<img src="/static/time_space/images/Tile 1.png" style="background: white" loading="lazy"> | `b to tlr`

## von links

Bild | Zeichen
-|-
<img src="/static/time_space/images/Tile 9.png" style="background: white" loading="lazy"> | `l to r`
<img src="/static/time_space/images/Tile 11.png" style="background: white" loading="lazy"> | `l to t`
<img src="/static/time_space/images/Tile 12.png" style="background: white" loading="lazy"> | `l to tr`

## von rechts

Bild | Zeichen
-|-
<img src="/static/time_space/images/Tile 8.png" style="background: white" loading="lazy"> | `r to l`
<img src="/static/time_space/images/Tile 10.png" style="background: white" loading="lazy"> | `r to t`
<img src="/static/time_space/images/Tile 13.png" style="background: white" loading="lazy"> | `r to tl`

## von mehreren Seiten

Bild | Zeichen
-|-
<img src="/static/time_space/images/Tile 15.png" style="background: white" loading="lazy"> | `cross to l`
<img src="/static/time_space/images/Tile 14.png" style="background: white" loading="lazy"> | `cross to r`
<img src="/static/time_space/images/Tile 17.png" style="background: white" loading="lazy"> | `double to tl`
<img src="/static/time_space/images/Tile 16.png" style="background: white" loading="lazy"> | `double to tr`


# Gatter

Bild | Gatter | Zeichen | beheben | Verhalten
-|-|-|-|-
<img src="/static/time_space/images/Mirror.png" style="background: white" loading="lazy"> | Mirror | `mirror` | 1 beliebiger Befehl | blockiert den Befehl für 3 Runden
<img src="/static/time_space/images/Inverter.png" style="background: white" loading="lazy"> | Inverter | `inverter` | - | vertauscht Befehle paarweise, s. unten
<img src="/static/time_space/images/Aktivator.png" style="background: white" loading="lazy"> | Aktivator | `button on` | - | lässt alles unverändert durch, kann durch klicken zum Desaktivator werden
<img src="/static/time_space/images/Desaktivator.png" style="background: white" loading="lazy"> | Desaktivator | `button off` | - | lässt nichts durch, kann durch klicken zum Aktivator werden
<img src="/static/time_space/images/Switch oben.png" style="background: white" loading="lazy"><img src="/static/time_space/images/Switch links.png" style="background: white" loading="lazy"><img src="/static/time_space/images/Switch rechts.png" style="background: white" loading="lazy"> | Switch | `switch` | - | lässt nur auf dem ausgewählten Output Befehle durch, der durch klicken verändert werden kann
<img src="/static/time_space/images/Konverter.png" style="background: white" loading="lazy"> | Konverter | `converter` ("converter_config" kann angegeben werden) | - | lässt alles durch, aber konvertiert genau einen Befehl in einen Anderen. Die Gegenrichtung kann auch erfolgen (konfigurierbar, s. ConverterConfig)
<img src="/static/time_space/images/Barriere.png" style="background: white" loading="lazy"> | Barriere | `barrier` ("stufe" kann angegeben werden) | 1 beliebiger Befehl | lässt nichts durch. Hält für Stufe-viele Befehle
<img src="/static/time_space/images/Manadegenerator.png" style="background: white" loading="lazy"> | Manadegenerator | `no mana` | `//inject` | lässt alles außer `//inject` durch
<img src="/static/time_space/images/Manabombe.png" style="background: white" loading="lazy"> | Manabombe | `mana bomb` | 1 beliebiger Befehl | lässt alles durch, zerstört dabei die zugehörige Zeitanomalie und macht einen beliebigen Zeitriss zu einem Splinter
<img src="/static/time_space/images/Support.png" style="background: white" loading="lazy"> | Support | `support` | `//drag` | lässt alles außer `//inject`, `//drop` durch und spawnt jeweils einen Consumer St. 1
<img src="/static/time_space/images/Sensor.png" style="background: white" loading="lazy"> | Sensor | `sensor` | `//delete` | lässt alles außer `//delete` durch
<img src="/static/time_space/images/Tracing.png" style="background: white" loading="lazy"> | Tracing | `tracing` | - | Spawnt 1 Kapselphänomen nach je 5 eintreffenden Befehlen
<img src="/static/time_space/images/Teleport Input.png" style="background: white" loading="lazy"> | Teleport Input | `teleport in` | - | gibt alle eintreffenden Befehle nur an den gekoppelten `Teleport Output` weiter und verändert danach seine Position
<img src="/static/time_space/images/Teleport Output.png" style="background: white" loading="lazy"> | Teleport Output | `teleport out` | - | nimmt Befehle nur vom gekoppelten `Teleport Input` entgegen und verändert danach seine Position

## Befehlpaare vom Inverter
- `//drag` - `//drop`
- `//inject` - `//crystallize`
- `//forward` - `//return`
 loading="lazy"
# ConverterConfig
```json
{
  "from": Befehl z.B. "//crystallize",
  "to": Befehl z.B. "//return",
  "bidirectional": true | false
}
```

# Zeitrisse

Ist ein Zeitriss mit einem Short gekoppelt, nimmt er `//naturalize` nicht als falschen Befehl wahr.

Bild | Zeitriss | Zeichen | beheben | Verhalten
-|-|-|-|-
<img src="/static/time_space/images/Zeitriss schwarz.png" style="background: white" loading="lazy"> | Liniendeletion | `liniendeletion` | `//analyze`, `//drag`, `//drop`, `//naturalize`| Verdeckt zu 5% pro Befehl einen anderen Zeitriss (nicht Liniendeletion oder Linearriss) und tauscht zu 50% Plätze. Die Ausgabe beider beginnt mit `#zahl?: `
<img src="/static/time_space/images/Zeitriss blau.png" style="background: white" loading="lazy"> | Linearriss | `linearriss` | `//return`, `//crystallize`, `//normalize` | Alle 3 Commands eine 25% Wahrscheinlichkeit ein Splinter zu werden
<img src="/static/time_space/images/Zeitriss rot.png" style="background: white" loading="lazy"> | Splinter | `splinter` | - | bei eintreffendem Befehl eine 33% Wahrscheinlichkeit in einen Linearriss UND 1-5 Duplikatoren, Looper, Timelagger, Timedelayer oder Runner zu zerfallen
<img src="/static/time_space/images/Zeitriss blau.png" style="background: white" loading="lazy"> | Duplikator | `duplikator` | `//crystallize`, `//normalize`, `//return`| Antwortet immer 2x
<img src="/static/time_space/images/Zeitriss blau.png" style="background: white" loading="lazy"> | Looper | `looper` | `//analyze`, `//drag`, `//delete`, `//naturalize` | wiederholt immer auch alte Ausgaben
<img src="/static/time_space/images/Zeitriss farblos.png" style="background: white" loading="lazy"> | Timelagger | `timelagger` | `//analyze`, `//drag`, `//drop`, `//normalize` | Antwortet als letzte 6x langsamer als Andere
<img src="/static/time_space/images/Zeitriss blau.png" style="background: white" loading="lazy"> | Timedelayer | `timedelayer` | `//forward`, `//inject`, `//normalize` | antwortet immer um 1 Befehl verspätet, stirbt auch 1x später
<img src="/static/time_space/images/Zeitriss blau.png" style="background: white" loading="lazy"> | Runner | `runner` | `//crystallize`, `//return`, `//normalize` | -

## Ausgaben nach eintreffendem Befehl

- Liniendeletion

    immer:
    `Target not found.`, `No event existing.`, `There is nothing.`, `We are wasting energy.`, `No.`, `Time is a state of mind.`, `Reach out.`, `Unidentified object found`, `Restarting ...`, `Program not ready.`, `Initializing ...`, `Please restart.`, `Converting splinter.`, `What am I?`

- Linearriss
  
    falscher o. richtiger Befehl | zerstört
    -|-
    `Growth accelerated. Manainput stabilized. Increasing size for further division.` | `Growth has been corrupted. Stabilization failed.`

- Splinter

    immer irgendein bullshit

- Duplikator

    falscher Befehl | korrekter Befehl | zerstört
    -|-|-
    `Mana has been detected`, `More mana is needed`, `Gathering more mana` | `Input has been blocked`, `Currently no power input`, `A critical error occured` | `Maintaining manaflow failed`, `Stabilization failed`, `Dew point too high`

- Looper
  
    falscher Befehl | korrekter Befehl | zerstört
    -|-|-
    `Mana in a spiral`, `Circulating more energy`, `Power ramped up` | `Dizzyness`, `Eastward it goes`, `Getting down` | `Mana falling down`, `Leaving the circle`, `Outer space`

- Timelagger
  
    falscher Befehl | korrekter Befehl | zerstört
    -|-|-
    Antwort von Phänomen zuvor | Antwort von Phänomen zuvor + (`it says`, `I guess`, `maybe`, `it shouldn't be`, `I assume`) | -

- Timedelayer
  
    falscher Befehl | korrekter Befehl | zerstört
    -|-|-
    `No`, `Wrong`, `Incorrect`, `Yesn't`, `Don't`, `Is not` | `Yes`, `Right`, `Hurt`, `Wow`, `Betrayal`, `Unfair` | `Murderer`, `Killer`, `No time for that`, `Out of existance`

- Runner

    falscher Befehl | korrekter Befehl | zerstört
    -|-|-
    `Yes`, `More power`, `POW`, `Module established`, `More mana is needed` | `Mana has been blocked`, `A critical error occurred`, `Target not found`, `Run` | `Stormy`, `Awaiting input`, `Stopped running`, `I stopped working`

# Zeitanomalien

Bild | Zeitanomalien | Zeichen | beheben | Verhalten
-|-|-|-|-
<img src="/static/time_space/images/Zeitanomalie.png" style="background: white" loading="lazy"> | Consumer | `consumer` | `//inject` * Stufe | Wächst nach jeder Runde zu 33% um 1 Stufe. Fallen ab Stufe 5 zu einem Linearriss zusammen
<img src="/static/time_space/images/Zeitanomalie.png" style="background: white" loading="lazy"> | Eraser | `eraser` | `//crystallize` * Stufe | -
<img src="/static/time_space/images/Zeitanomalie.png" style="background: white" loading="lazy"> | Blurr | `blurr` | `//drag` * Stufe| Wächst bei `//inject`, `//drop` oder `//crystallize` um je 1 Stufe. Verschleiert ein Phänomen oder Gatter zu 1% pro Stufe pro Runde
<img src="/static/time_space/images/Zeitanomalie.png" style="background: white" loading="lazy"> | Short | `short` | `//naturalize` * Stufe | Stiehlt zu 5% pro Runde eine Stufe von jemand Anderem. Zerfällt ab Stufe 10 in einen Splinter und eine Raumfissur. Ist mit einem Zeitriss verbunden; wenn einer zerstört wird wird es auch der Andere.
<img src="/static/time_space/images/Zeitanomalie.png" style="background: white" loading="lazy"> | Traceback | `traceback` | `//crystallize` | `//crystallize` muss in der gleichen Runde auch das Partner-Wurmloch treffen, um beide zu zerstören

## Ausgaben nach eintreffendem Befehl

falscher Befehl | korrekter Befehl | zerstört
-|-|-
`Health restored!` | `Accepted!` | `Done!`

# Raumrisse

Bild | Raumriss | Zeichen | beheben | Verhalten
-|-|-|-|-
<img src="/static/time_space/images/Raumriss.png" style="background: white" loading="lazy"> | Raumfissur | `raumfissur` | `//mdv` | -
<img src="/static/time_space/images/Raumriss.png" style="background: white" loading="lazy"> | Wurmloch | `wurmloch` | `//crystallize` | `//crystallize` muss in der gleichen Runde auch den Partner-Traceback treffen, um beide zu zerstören. Mit `//bdv` kann die Stufe um 1 bis auf min. 1 gesenkt werden. Sie Können max. Stufe 3 erreichen. Für Weiteres s. unten
<img src="/static/time_space/images/Raumriss.png" style="background: white" loading="lazy"> | Raumloch | `raumloch` | - | Kann auch auf Drähten und Gattern platzieren
<img src="/static/time_space/images/Raumriss.png" style="background: white" loading="lazy"> | Kapselphänomen | `kapselphänomen` | `//bdv` | alle 5 Runden nicht immun, dann kann Raumriss zu bestimmten Wahrscheinlichkeiten mit `//bdv` entfernt werden. Wenn das nicht klappt spawnt es ein Raumloch und die eigene Stufe steigt um 1
<img src="/static/time_space/images/Raumriss.png" style="background: white" loading="lazy"> | Bizarrgebiet | `bizarrgebiet` | `//mdbv` oder 2x `//mdv` | blockert jede Runde einen random Befehl für die nächste Runde (50%) oder fügt ein Gatter für eine Runde hinzu (25%) oder entfernt ein Gatter für 1 Runde (25%)

## Fähigkeiten von Wurmlöchern

ab Stufe | Wahrscheinlichkeit pro Runde | Effekt
-|-|-
1 | 20% | ein zufälliges Gatter umplatzieren
1 | 20% | tausche Plätze von 2 zufälligen Gattern
2 | 5% | erschaffe ein Supportgatter
3 | vorhandene Tracinggatter * 1% | ersetze ein vorhandenes Kapselphänomen mit einem Raumloch

## Behebungswahrscheinlichkeiten vom Kapselphänomen

Stufe | Wahrscheinlichkeit, dass `//bdv` klappt
-|-
1 | 50%
2 | 40%
3 | 30%
4 | 20%
5 | 10%

## Ausgaben nach eintreffendem Befehl

kein Befehl | falscher Befehl | korrekter Befehl | zerstört
-|-|-|-
0 | 1 | 2 | 3

