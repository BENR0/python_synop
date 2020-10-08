#! /usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

#wmo manual on codes:
# https://community.wmo.int/activity-areas/wmo-codes/manual-codes#Codes

#Syntax description
#section 0
#MMMM D....D YYGGggi 99LLL QLLLL

#section 1
#IIiii oder IIIII iihVV Nddff 00fff 1sTTT 2sTTT 3PPPP 4PPPP 5appp 6RRRt 7wwWW 8NCCC 9GGgg

#section 2
#222Dv 0sTTT 1PPHH 2PPHH 3dddd 4PPHH 5PPHH 6IEER 70HHH 8sTTT

#333 0.... 1sTTT 2sTTT 3EsTT 4E'sss 55SSS 2FFFF 3FFFF 4FFFF 553SS 2FFFF 3FFFF 4FFFF 6RRRt 7RRRR 8NChh
    #9SSss
#444 N'C'H'H'C
#555 0sTTT 1RRRr 2sTTT 22fff 23SS 24Wt 25ww 26fff 3LLLL 5ssst 7hhZD 8N/hh 910ff 911ff 912ff  PIC IN  BOT hsTTT
    #80000 1RRRRW 2SSSS 3fff 4fff 5RR 6VVVVVV 7sTTT 8sTTT 9sTTTs
#666 1sTTT 2sTTT 3sTTT 6VVVV/VVVV 7VVVV
    #80000 0RRRr 1RRRr 2RRRr 3RRRr 4RRRr 5RRRr
#999 0ddff 2sTTT 3E/// 4E'/// 7RRRz


STATION_TYPE_CODE = {"AAXX": "Landstation (FM 12)",
                     "BBXX": "Seastation (FM 13)",
                     "OOXX": "Mobile landstation (FM 14)"}

WIND_UNIT_CODE = {"0": "meters per second estimate",
                  "1": "meters per second measured",
                  "3": "knots estimate",
                  "4": "knots measured"}

#section 1
#iihVV
PRECIP_GROUP_CODE = {"0": "Niederschlag wird in den Abschnitten 1 und 3 gemeldet",
                     "1": "Niederschlag wird nur in Abschnitt 1 gemeldet",
                     "2": "Niederschlag wird nur in Abschnitt 3 gemeldet",
                     "3": "Niederschlag nicht gemeldet -- kein Niederschlag vorhanden",
                     "4": "Niederschlag nicht gemeldet -- Niederschlagsmessung nicht durchgeführt oder nicht vorgesehen",
                     "": np.nan}

STATION_OPERATION_TYPE_CODE = {"1": "bemannte Station -- Wettergruppe wird gemeldet",
                               "2": "bemannte Station -- Wettergruppe nicht gemeldet -- kein signifikantes Wetter",
                               "3": "bemannte Station -- Wettergruppe nicht gemeldet -- Wetterbeobachtung nicht durchgeführt",
                               "4": "automatische Station, Typ 1 -- Wettergruppe gemeldet",
                               "5": "automatische Station, Typ 1 -- Wettergruppe nicht gemeldet -- kein signifikantes Wetter",
                               "6": "automatische Station, Typ 2 -- Wettergruppe nicht gemeldet -- Wetter nicht feststellbar",
                               "7": "automatische Station, Typ 2 -- Wettergruppe wird gemeldet",
                               "": np.nan}

CLOUD_HEIGHT_0_CODE = {"0": "0 bis 49 m (0 bis 166 ft)",
                       "1": "50 bis 99 m (167 - 333 ft)",
                       "2": "100 bis 199 m (334 - 666 ft)",
                       "3": "200 bis 299 m (667 - 999 ft)",
                       "4": "300 bis 599 m (1000 - 1999 ft)",
                       "5": "600 bis 999 m (2000 - 3333 ft)",
                       "6": "1000 bis 1499 m (3334 - 4999 ft)",
                       "7": "1500 bis 1999 m (5000 - 6666 ft)",
                       "8": "2000 bis 2499 m (6667 - 8333 ft)",
                       "9": "2500 m oder höher (> 8334 ft) oder wolkenlos",
                       "/": "unbekannt",
                       "": np.nan}

#Nddff
cloud_cover_code = {"0": "0/8 (wolkenlos)",
					"1": "1/8 oder weniger (fast wolkenlos)",
					"2": "2/8 (leicht bewölkt)",
					"3": "3/8",
					"4": "4/8 (wolkig)",
					"5": "5/8",
					"6": "6/8 (stark bewölkt)",
					"7": "7/8 oder mehr (fast bedeckt)",
					"8": "8/8 (bedeckt)",
					"9": "Himmel nicht erkennbar",
					"/": "nicht beobachtet"}

#5aPPP
A_CODE = {"0": "erst steigend, dann fallend -- resultierender Druck gleich oder höher als zuvor",
          "1": "erst steigend, dann gleichbleibend -- resultierender Druck höher als zuvor",
          "2": "konstant steigend -- resultierender Druck höher als zuvor",
          "3": "erst fallend oder gleichbleibend, dann steigend -- resultierender Druck höher als zuvor",
          "4": "gleichbleibend -- resultierender Druck unverändert",
          "5": "erst fallend, dann steigend -- resultierender Druck gleich oder tiefer als zuvor",
          "6": "erst fallend, dann gleichbleibend -- resultierender Druck tiefer als zuvor",
          "7": "konstant fallend -- resultierender Druck tiefer als zuvor",
          "8": "erst steigend oder gleichbleibend, dann fallend -- resultierender Druck tiefer als zuvor",
          "": np.nan}

#6RRRt
T_CODE = {"0": "nicht aufgeführter oder vor dem Termin endender Zeitraum",
          "1": "6 Stunden",
          "2": "12 Stunden",
          "3": "18 Stunden",
          "4": "24 Stunden",
          "5": "1 Stunde bzw. 30 Minuten (bei Halbstundenterminen)",
          "6": "2 Stunden",
          "7": "3 Stunden",
          "8": "9 Stunden",
          "9": "15 Stunden",
          "/": "Sondermessung",
          None: np.nan}

#7wwWW
CURRENT_WEATHER_CODE = {"00": "Bewölkungsentwicklung nicht beobachtet",
                         "01": "Bewölkung abnehmend",
                         "02": "Bewölkung unverändert",
                         "03": "Bewölkung zunehmend",
                         "04": "Sicht durch Rauch oder Asche vermindert",
                         "05": "trockener Dunst (relative Feuchte < 80 %)",
                         "06": "verbreiteter Schwebstaub, nicht vom Wind herangeführt",
                         "07": "Staub oder Sand bzw. Gischt, vom Wind herangeführt",
                         "08": "gut entwickelte Staub- oder Sandwirbel",
                         "09": "Staub- oder Sandsturm im Gesichtskreis, aber nicht an der Station",
                         "10": "feuchter Dunst (relative Feuchte > 80 %)",
                         "11": "Schwaden von Bodennebel",
                         "12": "durchgehender Bodennebel",
                         "13": "Wetterleuchten sichtbar, kein Donner gehört",
                         "14": "Niederschlag im Gesichtskreis, nicht den Boden erreichend",
                         "15": "Niederschlag in der Ferne (> 5 km), aber nicht an der Station",
                         "16": "Niederschlag in der Nähe (< 5 km), aber nicht an der Station",
                         "17": "Gewitter (Donner hörbar), aber kein Niederschlag an der Station",
                         "18": "Markante Böen im Gesichtskreis, aber kein Niederschlag an der Station",
                         "19": "Tromben (trichterförmige Wolkenschläuche) im Gesichtskreis",
                         "20": "nach Sprühregen oder Schneegriesel",
                         "21": "nach Regen",
                         "22": "nach Schneefall",
                         "23": "nach Schneeregen oder Eiskörnern",
                         "24": "nach gefrierendem Regen",
                         "25": "nach Regenschauer",
                         "26": "nach Schneeschauer",
                         "27": "nach Graupel- oder Hagelschauer",
                         "28": "nach Nebel",
                         "29": "nach Gewitter",
                         "30": "leichter oder mäßiger Sandsturm, an Intensität abnehmend",
                         "31": "leichter oder mäßiger Sandsturm, unveränderte Intensität",
                         "32": "leichter oder mäßiger Sandsturm, an Intensität zunehmend",
                         "33": "schwerer Sandsturm, an Intensität abnehmend",
                         "34": "schwerer Sandsturm, unveränderte Intensität",
                         "35": "schwerer Sandsturm, an Intensität zunehmend",
                         "36": "leichtes oder mäßiges Schneefegen, unter Augenhöhe",
                         "37": "starkes Schneefegen, unter Augenhöhe",
                         "38": "leichtes oder mäßiges Schneetreiben, über Augenhöhe",
                         "39": "starkes Schneetreiben, über Augenhöhe",
                         "40": "Nebel in einiger Entfernung",
                         "41": "Nebel in Schwaden oder Bänken",
                         "42": "Nebel, Himmel erkennbar, dünner werdend",
                         "43": "Nebel, Himmel nicht erkennbar, dünner werdend",
                         "44": "Nebel, Himmel erkennbar, unverändert",
                         "45": "Nebel, Himmel nicht erkennbar, unverändert",
                         "46": "Nebel, Himmel erkennbar, dichter werdend",
                         "47": "Nebel, Himmel nicht erkennbar, dichter werdend",
                         "48": "Nebel mit Reifansatz, Himmel erkennbar",
                         "49": "Nebel mit Reifansatz, Himmel nicht erkennbar",
                         "50": "unterbrochener leichter Sprühregen",
                         "51": "durchgehend leichter Sprühregen",
                         "52": "unterbrochener mäßiger Sprühregen",
                         "53": "durchgehend mäßiger Sprühregen",
                         "54": "unterbrochener starker Sprühregen",
                         "55": "durchgehend starker Sprühregen",
                         "56": "leichter gefrierender Sprühregen",
                         "57": "mäßiger oder starker gefrierender Sprühregen",
                         "58": "leichter Sprühregen mit Regen",
                         "59": "mäßiger oder starker Sprühregen mit Regen",
                         "60": "unterbrochener leichter Regen oder einzelne Regentropfen",
                         "61": "durchgehend leichter Regen",
                         "62": "unterbrochener mäßiger Regen",
                         "63": "durchgehend mäßiger Regen",
                         "64": "unterbrochener starker Regen",
                         "65": "durchgehend starker Regen",
                         "66": "leichter gefrierender Regen",
                         "67": "mäßiger oder starker gefrierender Regen",
                         "68": "leichter Schneeregen",
                         "69": "mäßiger oder starker Schneeregen",
                         "70": "unterbrochener leichter Schneefall oder einzelne Schneeflocken",
                         "71": "durchgehend leichter Schneefall",
                         "72": "unterbrochener mäßiger Schneefall",
                         "73": "durchgehend mäßiger Schneefall",
                         "74": "unterbrochener starker Schneefall",
                         "75": "durchgehend starker Schneefall",
                         "76": "Eisnadeln (Polarschnee)",
                         "77": "Schneegriesel",
                         "78": "Schneekristalle",
                         "79": "Eiskörner (gefrorene Regentropfen)",
                         "80": "leichter Regenschauer",
                         "81": "mäßiger oder starker Regenschauer",
                         "82": "äußerst heftiger Regenschauer",
                         "83": "leichter Schneeregenschauer",
                         "84": "mäßiger oder starker Schneeregenschauer",
                         "85": "leichter Schneeschauer",
                         "86": "mäßiger oder starker Schneeschauer",
                         "87": "leichter Graupelschauer",
                         "88": "mäßiger oder starker Graupelschauer",
                         "89": "leichter Hagelschauer",
                         "90": "mäßiger oder starker Hagelschauer",
                         "91": "Gewitter in der letzten Stunde, zurzeit leichter Regen",
                         "92": "Gewitter in der letzten Stunde, zurzeit mäßiger oder starker Regen",
                         "93": "Gewitter in der letzten Stunde, zurzeit leichter Schneefall/Schneeregen/Graupel/Hagel",
                         "94": "Gewitter in der letzten Stunde, zurzeit mäßiger oder starker Schneefall/Schneeregen/Graupel/Hagel",
                         "95": "leichtes oder mäßiges Gewitter mit Regen oder Schnee",
                         "96": "leichtes oder mäßiges Gewitter mit Graupel oder Hagel",
                         "97": "starkes Gewitter mit Regen oder Schnee",
                         "98": "starkes Gewitter mit Sandsturm",
                         "99": "starkes Gewitter mit Graupel oder Hagel",
                         "": np.nan
                         }

#see [1] A-353
WEATHER_COURSE_CODE = {"0": "Wolkendecke stets weniger als oder genau die Hälfte bedeckend (0-4/8)",
                       "1": "Wolkendecke zeitweise weniger oder genau, zeitweise mehr als die Hälfte bedeckend (</> 4/8)",
                       "2": "Wolkendecke stets mehr als die Hälfte bedeckend (5-8/8)",
                       "3": "Staubsturm, Sandsturm oder Schneetreiben",
                       "4": "Nebel oder starker Dunst",
                       "5": "Sprühregen",
                       "6": "Regen",
                       "7": "Schnee oder Schneeregen",
                       "8": "Schauer",
                       "9": "Gewitter",
                       "": np.nan
                      }


#8NCCC
LOW_CLOUDS_CODE = {"0": "keine tiefen Wolken",
                   "1": "Cumulus humilis oder fractus (keine vertikale Entwicklung)",
                   "2": "Cumulus mediocris oder congestus (mäßige vertikale Entwicklung)",
                   "3": "Cumulonimbus calvus (keine Umrisse und kein Amboß)",
                   "4": "Stratocumulus cumulogenitus (entstanden durch Ausbreitung von Cumulus)",
                   "5": "Stratocumulus",
                   "6": "Stratus nebulosus oder fractus (durchgehende Wolkenfläche)",
                   "7": "Stratus fractus oder Cumulus fractus (Fetzenwolken bei Schlechtwetter)",
                   "8": "Cumulus und Stratocumulus (in verschiedenen Höhen)",
                   "9": "Cumulonimbus capillatus (mit Amboß)",
                   "/": "tiefe Wolken nicht erkennbar wegen Nebel, Dunkel- oder Verborgenheit",
                   "": np.nan
                  }

MEDIUM_CLOUDS_CODE = {"0": "keine mittelhohen Wolken",
                      "1": "Altostratus translucidus (meist durchsichtig)",
                      "2": "Altostratus opacus oder Nimbostratus",
                      "3": "Altocumulus translucidus (meist durchsichtig)",
                      "4": "Bänke von Altocumulus (unregelmäßig, lentikular)",
                      "5": "Bänder von Altocumulus (den Himmel fortschreitend überziehend)",
                      "6": "Altocumulus cumulogenitus (entstanden durch Ausbreitung von Cumulus)",
                      "7": "Altocumulus (mehrschichtig oder zusammen mit Altostratus/Nimbostratus)",
                      "8": "Altocumulus castellanus oder floccus (cumuliforme Büschel aufweisend)",
                      "9": "Altocumulus eines chaotisch aussehenden Himmels",
                      "/": "mittelhohe Wolken nicht erkennbar wegen Nebel, Dunkel- oder Verborgenheit",
                      "": np.nan
                     }

HIGH_CLOUDS_CODE = {"0": "keine hohen Wolken",
                    "1": "Cirrus fibratus oder uncinus (büschelartig)",
                    "2": "Cirrus spissatus, castellanus oder floccus (dicht, in Schwaden)",
                    "3": "Cirrus spissatus cumulogenitus (aus einem Amboß entstanden)",
                    "4": "Cirrus uncinus oder fibratus (den Himmel zunehmend oder fortschreitend überziehend)",
                    "5": "Bänder von zunehmendem Cirrus oder Cirrostratus (nicht höher als 45 Grad über dem Horizont)",
                    "6": "Bänder von zunehmendem Cirrus oder Cirrostratus (mehr als 45 Grad über dem Horizont, den Himmel nicht ganz bedeckend)",
                    "7": "Cirrostratus (den Himmel stets ganz bedeckend)",
                    "8": "Cirrostratus (den Himmel nicht ganz bedeckend, aber auch nicht zunehmend)",
                    "9": "Cirrocumulus",
                    "/": "hohe Wolken nicht erkennbar wegen Nebel, Dunkel- oder Verborgenheit",
                    "": np.nan
                    }

#3EsTT
ESTT_GROUND_CONDITIONS_CODE = {"0": "trocken",
                         "1": "feucht",
                         "2": "naß",
                         "3": "überflutet",
                         "4": "gefroren",
                         "5": "Glatteis oder Eisglätte (mindestens 50 % des Erdbodens bedeckend)",
                         "6": "loser, trockener Sand, den Boden nicht vollständig bedeckend",
                         "7": "geschlossene dünne Sandschicht, den Boden vollständig bedeckend",
                         "8": "geschlossene dicke Sandschicht, den Boden vollständig bedeckend",
                         "9": "extrem trockener Boden mit Rissen"
                        }

#Esss
ESSS_GROUND_CONDITIONS_CODE = {"0": "vorwiegend (> 50 %) mit Eis bedeckt (Hagel-/Graupel-/Grieseldecke)",
                         "1": "kompakter oder nasser Schnee, weniger als die Hälfte des Bodens bedeckend (Fl)",
                         "2": "kompakter oder nasser Schnee, mehr als die Hälfte, aber den Boden nicht vollständig bedeckend (dbr)",
                         "3": "ebene Schicht kompakten oder nassen Schnees, den gesamten Boden bedeckend",
                         "4": "unebene Schicht kompakten oder nassen Schneess, den gesamten Boden bedeckend",
                         "5": "loser, trockener Schnee, weniger als die Hälfte des Bodens bedeckend (Fl)",
                         "6": "loser, trockener Schnee, mehr als die Hälfte, aber den Boden nicht vollständig bedeckend (dbr)",
                         "7": "ebene Schicht losen, trockenen Schnees, den gesamten Boden bedeckend",
                         "8": "unebene Schicht losen, trockenen Schnees, den gesamten Boden bedeckend",
                         "9": "vollständig geschlossene Schneedecke mit hohen Verwehungen (> 50 cm)",
                         "/": "Reste (< 10 %) von Schnee oder Eis (Hagel/Graupel/Griesel)",
                         "": np.nan
                        }

#8NChh
CLOUD_TYPE_CODE = {"0": "Cirrus (Ci)",
                   "1": "Cirrocumulus (Cc)",
                   "2": "Cirrostratus (Cs)",
                   "3": "Altocumulus (Ac)",
                   "4": "Altostratus (As)",
                   "5": "Nimbostratus (Ns)",
                   "6": "Stratocumulus (Sc)",
                   "7": "Stratus (St)",
                   "8": "Cumulus (Cu)",
                   "9": "Cumulonimbus (Cb)",
                   "/": "Wolkengattung nicht erkennbar"
                   }

CLOUD_HEIGHT_CLASSES = {90: 49,
                        91: 99,
                        92: 199,
                        93: 299,
                        94: 599,
                        95: 999,
                        96: 1499,
                        97: 1999,
                        98: 2499,
                        99: 2500}
