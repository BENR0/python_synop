#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
import datetime
import logging
import pandas as pd

_logger = logging.getLogger(__name__)

#regex definitions
#split report into its sections
sections_re = re.compile(r"""(?P<section_0>[\d]{12}\s+(AAXX|BBXX|OOXX)\s+[\d]{5}\s+[\d]{5})\s+
                             (?P<section_1>(\d{5}\s+){0,9})
                             ((?P<section_2>(222\d\d\s+)(\d{5}\s+){0,9})){0,1}
                             ((333\s+)(?P<section_3>(\d{5}\s+){0,9})){0,1}
                             ((444\s+)(?P<section_4>(\d{5}\s+){0,9})){0,1}
                             ((555\s+)(?P<section_5>(\d{5}\s+){0,9})){0,1}
                             ((666\s+)(?P<section_6>(\d{5}\s+){0,9})){0,1}
                             ((999\s+)(?P<section_9>(\d{5}\s+){0,9})){0,1}""",
                             re.VERBOSE)

#split section 0
section_0_re = re.compile(r"""(?P<datetime>[\d]{12})\s+
                         (?P<MMMM>AAXX|BBXX|OOXX)\s+
                         (?P<monthdayr>[\d]{2})
                         (?P<hourr>[\d]{2})
                         (?P<wind_unit>[\d]{1})\s+
                         (?P<station_id>[\d]{5})""", re.VERBOSE)


#split section 1
#separate handling of groups because resulting dictionary can not contain double regex group names
section_1_re  = re.compile(r"""(?P<iihVV>\d{5})\s+
                               (?P<Nddff>(\d|/)\d{4})\s+
                               (00(?P<fff>\d{3})\s+)?
                               (1(?P<air_t>(\d|/){4})\s+)?
                               (2(?P<dewp>(\d|/){4})\s+)?
                               (3(?P<p_baro>(\d\d\d\d|\d\d\d\/))\s+)?
                               (4(?P<p_slv>(\d\d\d\d|\d\d\d\/))\s+)?
                               (5(?P<appp>\d{4})\s+)?
                               (6(?P<RRRt>(\d|/){3}\d\s+))?
                               (7(?P<wwWW>\d{2}(\d|/)(\d|/))\s+)?
                               (8(?P<NCCC>(\d|/){4})\s+)?
                               (9(?P<GGgg>\d{4})\s+)?""",
                               re.VERBOSE)

s1_iihVV_re = re.compile(r"""(?P<ir>\d)(?P<ix>\d)(?P<h>\d)(?P<VV>\d\d)""", re.VERBOSE)
s1_Nddff_re = re.compile(r"""(?P<N>(\d|/))(?P<dd>\d\d)(?P<ff>\d\d)""", re.VERBOSE)
s1_00fff_re = re.compile(r"""(?P<wind_speed>\d{3})""", re.VERBOSE)
#s1_1sTTT_re = re.compile(r"""(?P<air_t>\d{4})""", re.VERBOSE)
#s1_2sTTT_re = re.compile(r"""(?P<dewp>\d{4})""", re.VERBOSE)
#s1_3PPPP_re = re.compile(r"""(?P<p_baro>.*)""", re.VERBOSE)
#s1_4PPPP_re = re.compile(r"""(?P<p_slv>.*)""", re.VERBOSE)
s1_5appp_re = re.compile(r"""(?P<a>\d)(?P<ppp>\d{3})""", re.VERBOSE)
s1_6RRRt_re = re.compile(r"""(?P<RRR>\d{3})(?P<t>(\d|/))""", re.VERBOSE)
s1_7wwWW_re = re.compile(r"""(?P<ww>\d{2})(?P<W1>\d)(?P<W2>\d)""", re.VERBOSE)
s1_8NCCC_re = re.compile(r"""(?P<N>\d)(?P<CL>(\d|/))(?P<CM>(\d|/))(?P<CH>(\d|/))""", re.VERBOSE)
s1_9GGgg_re = re.compile(r"""(?P<observation_time>.*)""", re.VERBOSE)


#split section 2
section_2_re  = re.compile(r"""(222(?P<dv>\d{2}))\s+
                               (0(?P<water_t>(\d|/){4})\s+)?
                               (1(?P<aPPHH>\d{4})\s+)?
                               (2(?P<bPPHH>\d{4})\s+)?
                               ((3(?P<dddd>\d\d\d\d)\s+){0,2})?
                               (4(?P<cPPHH>\d{4})\s+)?
                               (5(?P<dPPHH>\d{4})\s+)?
                               (6(?P<IEER>\d{4})\s+)?
                               (70(?P<HHH>\d{3})\s+)?
                               (8(?P<bsTTT>\d{4})\s+)?""",
                               re.VERBOSE)

#split section 3
#separate handling of groups
#section_3_re  = re.compile(r"""(?P<tmax_12>(1(?P<sign>\d)(?P<value>\d\d\d)\s+))?
                               #(?P<tmin_12>(2(?P<sign1>\d)(?P<value1>\d\d\d)\s+))?
                               #(?P<tmin_12_boden>(3(?P<ground_state>\d)(?P<sign2>\d)(?P<value2>\d\d)\s+))?
                               #(?P<snow_cover>(4(?P<ground_state1>\d)(?P<value3>\d\d\d)\s+))?
                               #(?P<sun_prev_day>(55(?P<duration>\d\d\d)\s+(2(?P<rad_sum>\d\d\d\d)\s+)?(3(?P<rad_diff>\d\d\d\d)\s+)?(4(?P<rad_ir>\d\d\d\d)\s+)?))?
                               #(?P<sun_prev_hour>(553(?P<duration1>\d\d)\s+(2(?P<rad_sum1>\d\d\d\d)\s+)?(3(?P<rad_diff1>\d\d\d\d)\s+)?(4(?P<rad_ir1>\d\d\d\d)\s+)?))?
                               #(?P<precip>(6(?P<value4>(\d\d\d|///))(?P<ref_time>\d)\s+))?
                               #(7(?P<precip_24>\d\d\d\d)\s+)?
                               #(?P<clouds>(8(?P<code>\d\d\d\d)\s+){0,4})?
                               #(?P<special_weather>(9(?P<code1>\d\d\d\d)\s+){0,6})?""",
                               #re.VERBOSE)

section_3_re = re.compile(r"""(0(?P<xxxx>\d{4}\s+))?
                              (1(?P<t_max>\d{4}\s+))?
                              (2(?P<t_min>\d{4}\s+))?
                              (3(?P<EsTT>\d{4}\s+))?
                              (4(?P<Esss>(\d|/)\d{3}\s+))?
                              (?P<SSS>(55\d\d\d\s+)(0\d{4}\s+)?(1\d{4}\s+)?(2\d{4}\s+)?(3\d{4}\s+)?(4\d{4}\s+)?(6\d{4}\s+)?(6\d{4}\s+)?)?
                              (?P<SS>(553\d\d\s+)(0\d{4}\s+)?(1\d{4}\s+)?(2\d{4}\s+)?(3\d{4}\s+)?(4\d{4}\s+)?(6\d{4}\s+)?(6\d{4}\s+)?)?
                              (6(?P<RRRt>(\d\d\d|///)\d\s+))?
                              (7(?P<precip>\d{4}\s+))?
                              (?P<NChh>(8\d(\d|/)\d\d\s+){0,4})?
                              (9(?P<SSss>\d{4}\s+){0,9})?""",
                              re.VERBOSE)

s3_EsTT_re = re.compile(r"""(?P<E>\d)(?P<sTT>\d{3})""", re.VERBOSE)
s3_Esss_re = re.compile(r"""(?P<E>\d)(?P<sss>\d{3})""", re.VERBOSE)
s3_55SSS_re = re.compile(r"""(55(?P<hours>\d\d\d)\s+
                             (0(?P<net_pos>\d\d\d\d)\s+)?
                             (1(?P<net_neg>\d\d\d\d)\s+)?
                             (2(?P<global>\d\d\d\d)\s+)?
                             (3(?P<diff>\d\d\d\d)\s+)?
                             (4(?P<long_down>\d\d\d\d)\s+)?
                             (5(?P<long_up>\d\d\d\d)\s+)?
                             (6(?P<short>\d\d\d\d)\s+)?)?""",
                             re.VERBOSE)
s3_553SS_re = re.compile(r"""(553(?P<hours>\d\d)\s+
                             (0(?P<net_pos>\d\d\d\d)\s+)?
                             (1(?P<net_neg>\d\d\d\d)\s+)?
                             (2(?P<global>\d\d\d\d)\s+)?
                             (3(?P<diff>\d\d\d\d)\s+)?
                             (4(?P<long_down>\d\d\d\d)\s+)?
                             (5(?P<long_up>\d\d\d\d)\s+)?
                             (6(?P<short>\d\d\d\d)\s+)?)?""",
                             re.VERBOSE)
s3_8NChh_re = re.compile(r"""(8(?P<layer_1>\d(\d|/)\d\d)\s+)?
                             (8(?P<layer_2>\d(\d|/)\d\d)\s+)?
                             (8(?P<layer_3>\d(\d|/)\d\d)\s+)?
                             (8(?P<layer_4>\d(\d|/)\d\d)\s+)?""",
                             re.VERBOSE)




section_4_re = re.compile(r"""(?P<any>.*\s+)?""", re.VERBOSE)

section_5_re = section_4_re

section_6_re = section_4_re

section_9_re = section_4_re


def _report_match(handler, match):
    """
    Report success or failure of the given handler function. (DEBUG)
    """
    if match:
        _logger.debug("%s matched '%s'", handler.__name__, match)
    else:
        _logger.debug("%s didn't match...", handler.__name__)


class synop(object):
    """
    SYNOP report

    References
    ----------
    [1] World Meteorological Organization (WMO). 2011. Manual on Codes - International Codes,
        Volume I.1, Annex II to the WMO Technical Regulations: Part A- Alphanumeric Codes.
        2011 edition updated in 2017. WMO.
    """
    
    def __init__(self, report):
        """
        Decode SYNOP report
        
        Parameters
        ----------
        report : str
            Raw SYNOP report
        
        """
        self.raw = report
        self.type = "SYNOP"
        self.datetime = None
        self.station_id = None

        self.decoded = sections_re.match(self.raw).groupdict()

        #split raw report into its sections then split each section into
        #its groups and handle (decode) each group
        for sname, sraw in self.decoded.items():
            if not sraw is None:
                pattern, ghandlers = self.handlers[sname]
                #sec_groups = patter.match(sraw).groupdict()
                self.decoded[sname] = pattern.match(sraw).groupdict()
                #for gname, graw in sec_groups.items():
                for gname, graw in self.decoded[sname].items():
                    if not graw is None:
                        gpattern, ghandler = ghandlers[gname]
                        if gpattern is None:
                            self.decoded[sname][gname] = ghandler(self, graw)
                        else:
                            group = gpattern.match(graw)
                            _report_match(ghandler, group.group())
                            self.decoded[sname][gname] = ghandler(self, group.groupdict())
                    else:
                        self.decoded[sname][gname] = None
            else:
                self.decoded[sname] = None
        


    def _default_handler(self, code):
        """
        Default handler

        Parameters
        ----------
        code : str
            Raw data to be decoded

        Returns
        -------
        str
            input string
        """
        return code


    def _handle_MMMM(self,  code):
        station_type_code = {"AAXX": "Landstation (FM 12)",
                             "BBXX": "Seastation (FM 13)",
                             "OOXX": "Mobile landstation (FM 14)"}

        return station_type_code[code]


    def _handle_wind_unit(self, code):
        wind_unit_code = {"0": "meters per second estimate",
                          "1": "meters per second measured",
                          "3": "knots estimate"}

        return wind_unit_code[code]


    def _handle_sTTT(self, code):
        """
        Decode temperature
        
        Parameters
        ----------
        code : str
            Temperature with first charater defining the sign or
            type of unit (°C or relative humidity in % for dewpoint)
            
        Returns
        -------
        float
            Temperature in degree Celsius
            
        """
        sign = int(code[0])
        value = int(code[1:])
        
        if sign == 0:
            sign = -1
        elif sign == 1:
            sign = 1
        elif sign == 9:
            return value

        value = sign * value * 0.1
        
        return value


    def _handle_PPPP(self, code):
        """
        Decode pressure
        
        Parameters
        ----------
        code : str
            Pressure code without thousands in  1/10 Hectopascal.
            If last character of code is "/" pressure is given as
            full Hectopascal.
            
        Returns
        -------
        float
            Pressure in Hectopascal
            
        """
        if code[-1] == "/":
            value = int(code[0:-1])
        else:
            value = int(code) * 0.1
            
        value = 1000 + value
        
        return value


    #@static_method
    def _handle_vis(self, code):
        """
        Decode visibility of synop report
        
        Parameters
        ----------
        code : str
            VV part of iihVV group
        
        Returns
        -------
        float
            Visibility in km

        """
        vislut = {90: 0.05,
                  91: 0.05,
                  92: 0.2,
                  93: 0.5,
                  94: 1,
                  95: 2,
                  96: 4,
                  97: 10,
                  98: 20,
                  99: 50}
        
        if not code == "//":
            code = int(code)
        else:
            return "NA"
        
        if code <= 50:
            dist = 0.1 * code
        elif code > 50 and code <= 80:
            dist = 6 + (code - 56) * 1
        elif code > 80 and code <= 89:
            dist = 35 + (code - 81) * 5
        else:
            dist = vislut[code]
        
        return dist


    def _handle_iihVV(self, d):
        """
        Handles iihVV group in section 1

        i: precipitation group indicator (ir)
        i: station type and weather group indicator (ix)
        h: cloud base of lowest observed cloud
        VV: horizontal visibility

        Parameters
        ----------
        d : dict
            re groupdict

        """
        precip_group_code = {"0": "Niederschlag wird in den Abschnitten 1 und 3 gemeldet",
                             "1": "Niederschlag wird nur in Abschnitt 1 gemeldet",
                             "2": "Niederschlag wird nur in Abschnitt 3 gemeldet",
                             "3": "Niederschlag nicht gemeldet -- kein Niederschlag vorhanden",
                             "4": "Niederschlag nicht gemeldet -- Niederschlagsmessung nicht durchgeführt oder nicht vorgesehen"}

        station_operation_type_code = {"1": "bemannte Station -- Wettergruppe wird gemeldet",
                                       "2": "bemannte Station -- Wettergruppe nicht gemeldet -- kein signifikantes Wetter",
                                       "3": "bemannte Station -- Wettergruppe nicht gemeldet -- Wetterbeobachtung nicht durchgeführt",
                                       "4": "automatische Station, Typ 1 -- Wettergruppe gemeldet",
                                       "5": "automatische Station, Typ 1 -- Wettergruppe nicht gemeldet -- kein signifikantes Wetter",
                                       "6": "automatische Station, Typ 2 -- Wettergruppe nicht gemeldet -- Wetter nicht feststellbar",
                                       "7": "automatische Station, Typ 2 -- Wettergruppe wird gemeldet"}

        cloud_height_0_code = {"0": "0 bis 49 m (0 bis 166 ft)",
                               "1": "50 bis 99 m (167 - 333 ft)",
                               "2": "100 bis 199 m (334 - 666 ft)",
                               "3": "200 bis 299 m (667 - 999 ft)",
                               "4": "300 bis 599 m (1000 - 1999 ft)",
                               "5": "600 bis 999 m (2000 - 3333 ft)",
                               "6": "1000 bis 1499 m (3334 - 4999 ft)",
                               "7": "1500 bis 1999 m (5000 - 6666 ft)",
                               "8": "2000 bis 2499 m (6667 - 8333 ft)",
                               "9": "2500 m oder höher (> 8334 ft) oder wolkenlos",
                               "/": "unbekannt"}

        iihVV = {"precip_group": precip_group_code[d["ir"]],
                 "station_operation": station_operation_type_code[d["ix"]],
                 "cloud_height": cloud_height_0_code[d["h"]],
                 "vis": self._handle_vis(d["VV"])}

        return iihVV


    def _handle_Nddff(self, d):
        """
        Handles Nddff group in section 1

        N: total cloud cover in okta
        dd: wind direction in dekadegree (10 minute mean)
        ff: wind speed (10 minute mean)

        Parameters
        ----------
        d : dict
            re groupdict

        """
        cloud_cover = d["N"]
        if cloud_cover == "/":
            #not observed
            cloud_cover = "NA"
        #elif cloud_cover == "9":
            ##sky not observable/visible
            #cloud_cover = -99
        else:
            cloud_cover = int(cloud_cover)


        wind_dir = int(d["dd"])
        if wind_dir == 0:
            #no wind
            wind_dir = "NA"
        elif wind_dir == 99:
            #circular wind
            wind_dir = -99
        else:
            #01: 5-14
            #02: 15-24
            #03: 25-34
            #decoding the class to single value in the middle of the class
            wind_dir = (10 * wind_dir) - 1


        #wind speed is greater than 99 units and this group is directly followed
        #by the 00fff group
        wind_speed = int(d["ff"])

        Nddff = {"cloud_cover": cloud_cover,
                 "wind_dir": wind_dir,
                 "wind_speed": wind_speed}

        return Nddff


    def _handle_00fff(self, d):
        """
        Handles 00fff group in section 1

        This group is only present if wind speed is above 99 units.

        fff: wind speed (10 minute mean)

        Parameters
        ----------
        d : dict
            re groupdict

        """

        return int(d["wind_speed"])


    def _handle_5appp(self, d):
        """
        Handles 5appp group in section 1

        3 hourly tendency of station air pressure

        a: type of pressure tendency
        ppp: absolute pressure change over last three hours in 1/10 Hectopascal


        Parameters
        ----------
        d : dict
            re groupdict

        """
        a_code = {"0": "erst steigend, dann fallend -- resultierender Druck gleich oder höher als zuvor",
                  "1": "erst steigend, dann gleichbleibend -- resultierender Druck höher als zuvor",
                  "2": "konstant steigend -- resultierender Druck höher als zuvor",
                  "3": "erst fallend oder gleichbleibend, dann steigend -- resultierender Druck höher als zuvor",
                  "4": "gleichbleibend -- resultierender Druck unverändert",
                  "5": "erst fallend, dann steigend -- resultierender Druck gleich oder tiefer als zuvor",
                  "6": "erst fallend, dann gleichbleibend -- resultierender Druck tiefer als zuvor",
                  "7": "konstant fallend -- resultierender Druck tiefer als zuvor",
                  "8": "erst steigend oder gleichbleibend, dann fallend -- resultierender Druck tiefer als zuvor"}

        appp = {"p_tendency": a_code[d["a"]],
                 "p_diff": self._handle_PPPP(d["ppp"])}

        return appp


    def _handle_6RRRt(self, d):
        """
        Handles 6RRRt group in section 1

        Amount of melted precipitation

        RRR: precipitation amount in mm
        t: reference time


        Parameters
        ----------
        d : dict
            re groupdict

        """
        t_code = {"0": "nicht aufgeführter oder vor dem Termin endender Zeitraum",
                  "1": "6 Stunden",
                  "2": "12 Stunden",
                  "3": "18 Stunden",
                  "4": "24 Stunden",
                  "5": "1 Stunde bzw. 30 Minuten (bei Halbstundenterminen)",
                  "6": "2 Stunden",
                  "7": "3 Stunden",
                  "8": "9 Stunden",
                  "9": "15 Stunden",
                  "/": "Sondermessung"}

        precip_ref_time = t_code[d["t"]]

        precip = int(d["RRR"])
        if precip > 989:
            precip = (precip - 990) * 0.1
            if precip == 0:
                #only traces of precipitation not measurable < 0.05
                precip = 0.05

        RRRt = {"precip": precip,
                "ref_time": precip_ref_time}
        return RRRt


    def _handle_7wwWW(self, d):
        """
        Handles 7wwWW group in section 1

        Current weather and weather course
        
        ww: current weather
        W: weather course (W1)
        W: weather course (W2)


        Parameters
        ----------
        d : dict
            re groupdict

        """
        currrent_weather_code = {"00": "Bewölkungsentwicklung nicht beobachtet",
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
                                 "99": "starkes Gewitter mit Graupel oder Hagel"
                                 }

        #see [1] A-353
        weather_course_code = {"0": "Wolkendecke stets weniger als oder genau die Hälfte bedeckend (0-4/8)",
                               "1": "Wolkendecke zeitweise weniger oder genau, zeitweise mehr als die Hälfte bedeckend (</> 4/8)",
                               "2": "Wolkendecke stets mehr als die Hälfte bedeckend (5-8/8)",
                               "3": "Staubsturm, Sandsturm oder Schneetreiben",
                               "4": "Nebel oder starker Dunst",
                               "5": "Sprühregen",
                               "6": "Regen",
                               "7": "Schnee oder Schneeregen",
                               "8": "Schauer",
                               "9": "Gewitter"
                              }

        wwWW = {"current_weather": current_weather_code[d["ww"]],
                "w_course1": weather_course_code[d["W1"]],
                "w_course2": weather_course_code[d["W2"]]}

        return wwWW


    def _handle_8NCCC(self, d):
        """
        Handles 8NCCC group in section 1

        Information about cloud types

        N: amount of low clouds if not present amount of medium high clouds
        C: type of low clouds (CL)
        C: type of medium clouds (CM)
        C: type of high clouds (CH)


        Parameters
        ----------
        d : dict
            re groupdict

        """
        low_clouds_code = {"0": "keine tiefen Wolken",
                           "1": "Cumulus humilis oder fractus (keine vertikale Entwicklung)",
                           "2": "Cumulus mediocris oder congestus (mäßige vertikale Entwicklung)",
                           "3": "Cumulonimbus calvus (keine Umrisse und kein Amboß)",
                           "4": "Stratocumulus cumulogenitus (entstanden durch Ausbreitung von Cumulus)",
                           "5": "Stratocumulus",
                           "6": "Stratus nebulosus oder fractus (durchgehende Wolkenfläche)",
                           "7": "Stratus fractus oder Cumulus fractus (Fetzenwolken bei Schlechtwetter)",
                           "8": "Cumulus und Stratocumulus (in verschiedenen Höhen)",
                           "9": "Cumulonimbus capillatus (mit Amboß)",
                           "/": "tiefe Wolken nicht erkennbar wegen Nebel, Dunkel- oder Verborgenheit"
                          }

        medium_clouds_code = {"0": "keine mittelhohen Wolken",
                              "1": "Altostratus translucidus (meist durchsichtig)",
                              "2": "Altostratus opacus oder Nimbostratus",
                              "3": "Altocumulus translucidus (meist durchsichtig)",
                              "4": "Bänke von Altocumulus (unregelmäßig, lentikular)",
                              "5": "Bänder von Altocumulus (den Himmel fortschreitend überziehend)",
                              "6": "Altocumulus cumulogenitus (entstanden durch Ausbreitung von Cumulus)",
                              "7": "Altocumulus (mehrschichtig oder zusammen mit Altostratus/Nimbostratus)",
                              "8": "Altocumulus castellanus oder floccus (cumuliforme Büschel aufweisend)",
                              "9": "Altocumulus eines chaotisch aussehenden Himmels",
                              "/": "mittelhohe Wolken nicht erkennbar wegen Nebel, Dunkel- oder Verborgenheit"
                             }

        high_clouds_code = {"0": "keine hohen Wolken",
                            "1": "Cirrus fibratus oder uncinus (büschelartig)",
                            "2": "Cirrus spissatus, castellanus oder floccus (dicht, in Schwaden)",
                            "3": "Cirrus spissatus cumulogenitus (aus einem Amboß entstanden)",
                            "4": "Cirrus uncinus oder fibratus (den Himmel zunehmend oder fortschreitend überziehend)",
                            "5": "Bänder von zunehmendem Cirrus oder Cirrostratus (nicht höher als 45 Grad über dem Horizont)",
                            "6": "Bänder von zunehmendem Cirrus oder Cirrostratus (mehr als 45 Grad über dem Horizont, den Himmel nicht ganz bedeckend)",
                            "7": "Cirrostratus (den Himmel stets ganz bedeckend)",
                            "8": "Cirrostratus (den Himmel nicht ganz bedeckend, aber auch nicht zunehmend)",
                            "9": "Cirrocumulus",
                            "/": "hohe Wolken nicht erkennbar wegen Nebel, Dunkel- oder Verborgenheit"
                            }

        NCCC = {"cloud_amount": d["N"],
                "cloud_type_low": low_clouds_code[d["CL"]],
                "cloud_type_medium": medium_clouds_code[d["CM"]],
                "cloud_type_high": high_clouds_code[d["CH"]],
               }

        return NCCC


    def _handle_9GGgg(self, d):
        """
        Handles 9GGgg group in section 1

        Observation time (UTC)

        GG: hours
        gg: minutes

        Parameters
        ----------
        d : dict
            re groupdict

        """
        time = d["observation_time"]

        return d

    #############################
    #Handling of section 3 groups
    #############################
    def _handle_3EsTT(self, d):
        """
        Handles 3EsTT group in section 3

        12 respectively 15 hour minimum temperature 5cm above ground/snow cover

        E: condition of the ground, the snow respectively
        sTT: temperature with s being the sign
             only reported at 06, 09, and 18 UTC. /// at 00 and 12 UTC

        Parameters
        ----------
        d : dict
            re groupdict

        """
        ground_condition_code = {"0": "trocken",
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

        return d
    

    def _handle_4Esss(self, d):
        """
        Handles 4Esss group in section 3

        Snow height
        Only reported at 00, 06, 12, 18 UTC.

        E: condition of the ground with snow/ice
        sss: snow height in cm

        Parameters
        ----------
        d : dict
            re groupdict

        """
        ground_condition_code = {"0": "vorwiegend (> 50 %) mit Eis bedeckt (Hagel-/Graupel-/Grieseldecke)",
                                 "1": "kompakter oder nasser Schnee, weniger als die Hälfte des Bodens bedeckend (Fl)",
                                 "2": "kompakter oder nasser Schnee, mehr als die Hälfte, aber den Boden nicht vollständig bedeckend (dbr)",
                                 "3": "ebene Schicht kompakten oder nassen Schnees, den gesamten Boden bedeckend",
                                 "4": "unebene Schicht kompakten oder nassen Schneess, den gesamten Boden bedeckend",
                                 "5": "loser, trockener Schnee, weniger als die Hälfte des Bodens bedeckend (Fl)",
                                 "6": "loser, trockener Schnee, mehr als die Hälfte, aber den Boden nicht vollständig bedeckend (dbr)",
                                 "7": "ebene Schicht losen, trockenen Schnees, den gesamten Boden bedeckend",
                                 "8": "unebene Schicht losen, trockenen Schnees, den gesamten Boden bedeckend",
                                 "9": "vollständig geschlossene Schneedecke mit hohen Verwehungen (> 50 cm)",
                                 "/": "Reste (< 10 %) von Schnee oder Eis (Hagel/Graupel/Griesel)"
                                }

        Esss = {"ground_cond": ground_condition_code[d["E"]],
                "snow_height": int(d["sss"])}

        return d
    

    def _handle_55SSS(self, d):
        """
        Handles 55SSS group and the groups following it in section 3

        55SSS: Sunshine duration of the previous day in 1/10 hours (only reported at 06 UTC)
        0FFFF: positive net radiation in J/m^⁻2
        1FFFF: negative net radiation in J/m^⁻2
        2FFFF: sum of global radiation in J/m^⁻2
        3FFFF: sum of diffuse sky radiation in J/m^⁻2
        4FFFF: sum of downward long-wave radiation radiation in J/m^⁻2
        5FFFF: sum of upward long-wave radiation radiation in J/m^⁻2
        6FFFF: sum of short-wave radiation radiation in J/m^⁻2

        SSS: hours
        FFF: radiation in J/m^-2

        Parameters
        ----------
        d : dict
            re groupdict

        """
        d = {k: int(v) for k,v in d.items() if not v is None}
        d["hours"] = d["hours"] / 10.0

        return d
    

    def _handle_553SS(self, d):
        """
        Handles 553SS group and the groups following it in section 3

        553SS: Sunshine duration of the the last full or half (only for half hour measurements)
               hour in 1/10 hours (only reported at 06 UTC)
        0FFFF: positive net radiation in kJ/m^⁻2
        1FFFF: negative net radiation in kJ/m^⁻2
        2FFFF: sum of global radiation in kJ/m^⁻2
        3FFFF: sum of diffuse sky radiation in kJ/m^⁻2
        4FFFF: sum of downward long-wave radiation radiation in kJ/m^⁻2
        5FFFF: sum of upward long-wave radiation radiation in kJ/m^⁻2
        6FFFF: sum of short-wave radiation radiation in kJ/m^⁻2

        SSS: hours
        FFF: radiation in kJ/m^-2

        Parameters
        ----------
        d : dict
            re groupdict

        """
        d = {k: int(v) for k,v in d.items() if not v is None}
        d["hours"] = d["hours"] / 10.0

        return d
    

    def _handle_6RRRt(self, d):
        """
        Handles 6RRRt group in section 3

        Melted precipitation.
        Three hourly precipitation height.

        NOTE: Only present if regulation 12.2.5.2 applies (see ref [1] A-24)

        GG: hours
        gg: minutes

        Parameters
        ----------
        d : dict
            re groupdict

        """

        return d
    

    def _handle_7RRRR(self, d):
        """
        Handles 7RRRR group in section 3

        Reports total precipitation amount during the 24 hour period
        ending at the time of observation in 1/10 of millimetre.

        RRRR: precip in 1/10 mm (9999 for trace)

        Parameters
        ----------
        d : dict
            re groupdict

        """
        d = int(d)

        if d >= 9998:
            precip = 999
        elif d == 9999:
            precip = "NA"
        else:
            precip = d

        return precip
    

    def _handle_8NChh(self, d):
        """
        Handles 8NChh group in section 3

        Report of cloud layers. May be repeated up to 4 times.

        N: cloud cover in okta.
           If 9 obscured by fog or other meteorological phenomena.
           If / observation not made or not possible due to phenomena other
           than 9
        C: cloud type
        hh: height of cloud base in m

        Parameters
        ----------
        d : dict
            re groupdict

        """
        cloud_type_code = {"0": "Cirrus (Ci)",
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

        cloud_height_classes = {90: 49,
                                91: 99,
                                92: 199,
                                93: 299,
                                94: 599,
                                95: 999,
                                96: 1499,
                                97: 1999,
                                98: 2499,
                                99: 2500}

        def cheight(code):
            """
            Decode cloud height

            Parameters
            ----------
            code : str

            Returns
            -------
            int
                Cloud height in m
            """
            code = int(code)

            type = "continous"

            if code <= 50:
                h = code * 30
            elif code >= 56 and code <= 80:
                h = 1800 + (code - 56) * 300
            elif code >= 81 and code <= 89:
                h = 10500 + (code - 81) * 1500
            elif code >= 90:
                type = "classes"
                h = cloud_height_classes[code] 

            return h, type


        layer_re = re.compile(r"""((?P<cover>\d)(?P<type>(\d|/))(?P<height>\d\d))""", re.VERBOSE)

        for l, v  in d.items():
            if not v is None:
                layer = layer_re.match(v).groupdict()
                cover = layer["cover"]
                if cover != "/":
                    layer["cover"] = int(layer["cover"])
                else:
                    layer["cover"] = "NA"

                layer["type"] = cloud_type_code[layer["type"]]
                h, t = cheight(layer["height"])
                layer["height"] = h
                layer["measurement"] = t
                d[l] = layer
            else:
                d[l] = None

        return d
    

    def _handle_9GGgg(self, d):
        """
        Handles 9GGgg group in section 1

        Observation time (UTC)

        GG: hours
        gg: minutes



        Parameters
        ----------
        d : dict
            re groupdict

        """

        return d
    


    sec0_handlers = (section_0_re,
                     {"datetime": (None, _default_handler),
                      "MMMM": (None, _handle_MMMM),
                      "monthdayr": (None, _default_handler),
                      "hourr": (None, _default_handler),
                      "wind_unit": (None, _handle_wind_unit),
                      "station_id": (None, _default_handler)})

    sec1_handlers = (section_1_re,
                     {"iihVV": (s1_iihVV_re, _handle_iihVV),
                      "Nddff": (s1_Nddff_re, _handle_Nddff),
                      "fff": (s1_00fff_re, _handle_00fff),
                      "air_t": (None, _handle_sTTT),
                      "dewp": (None, _handle_sTTT),
                      "p_baro": (None, _handle_PPPP),
                      "p_slv": (None, _handle_PPPP),
                      "appp": (s1_5appp_re, _handle_5appp),
                      "RRRt": (s1_6RRRt_re, _handle_6RRRt),
                      "wwWW": (s1_7wwWW_re, _handle_7wwWW),
                      "NCCC": (s1_8NCCC_re, _handle_8NCCC),
                      "GGgg": (s1_9GGgg_re, _handle_9GGgg),
                     })

    sec2_handlers = (section_2_re,
                     {"asTTT": (None, _handle_sTTT),
                      "aPPHH": (None, _default_handler),
                      "bPPHH": (None, _default_handler),
                      "dddd": (None, _default_handler),
                      "cPPHH": (None, _default_handler),
                      "dPPHH": (None, _default_handler),
                      "IEER": (None, _default_handler),
                      "HHH": (None, _default_handler),
                      "bsTTT": (None, _handle_sTTT),
                     })

    sec3_handlers = (section_3_re,
                     {"xxxx": (None, _default_handler),
                      "t_max": (None, _handle_sTTT),
                      "t_min": (None, _handle_sTTT),
                      "EsTT": (s3_EsTT_re, _handle_3EsTT),
                      "Esss": (s3_Esss_re, _handle_4Esss),
                      "SSS": (s3_55SSS_re, _handle_55SSS),
                      "SS": (s3_553SS_re, _handle_553SS),
                      "RRRt": (s1_6RRRt_re, _handle_6RRRt),
                      "precip": (None, _handle_7RRRR),
                      "NChh": (s3_8NChh_re, _handle_8NChh),
                      "SSss": (None, _default_handler),
                     })

    sec4_handlers = (section_4_re,
                     {"any": (None, _default_handler),
                     })

    sec5_handlers = (section_5_re,
                     {"any": (None, _default_handler),
                     })

    sec6_handlers = (section_6_re,
                     {"any": (None, _default_handler),
                     })

    sec9_handlers = (section_9_re,
                     {"any": (None, _default_handler),
                     })

    handlers = {"section_0": sec0_handlers,
                     "section_1": sec1_handlers,
                     "section_2": sec2_handlers,
                     "section_3": sec3_handlers,
                     "section_4": sec4_handlers,
                     "section_5": sec5_handlers,
                     "section_6": sec6_handlers,
                     "section_9": sec9_handlers}


    def __str__(self):
        def prettydict(d, indent = 0):
            """
            Print dict (of dict) pretty with indent

            Parameters
            ----------
            d : dict

            Returns
            -------
            print

            """
            for key, value in d.items():
                if isinstance(value, dict):
                    print("\t" * indent + str(key) + ":")
                    prettydict(value, indent + 1)
                else:
                    #print("\t" * (indent + 1) + str(value))
                    print("\t" * indent + str(key) + ": " +  str(value))
            return

        prettydict(self.decoded)

        return

    def toDF(self):
        """
        Convert selected variables of report to a pandas dataframe

        Returns
        -------
        pd.DataFrame

        """
        group_prefixes = {""}


        return
