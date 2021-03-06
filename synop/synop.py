#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
import datetime
import logging
import pandas as pd
import numpy as np

from .code_descriptions import *

_logger = logging.getLogger(__name__)

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


#regex definitions
#split report into its sections
sections_re = re.compile(r"""(?P<section_0>[\d]{12}\s+(AAXX|BBXX|OOXX)\s+[\d]{5}\s+[\d]{5})\s+
                             (?P<section_1>((\d|\/){5}\s+){0,9}){0,1}
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
section_1_re  = re.compile(r"""((?P<iihVV>(\d|\/){5})\s+
                               (?P<Nddff>(\d|/){5})\s+
                               (00(?P<fff>\d{3})\s+)?
                               (1(?P<t_air>(\d|/){4})\s+)?
                               (2(?P<dewp>(\d|/){4})\s+)?
                               (3(?P<p_baro>(\d\d\d\d|\d\d\d\/))\s+)?
                               (4(?P<p_slv>(\d\d\d\d|\d\d\d\/))\s+)?
                               (5(?P<appp>\d{4})\s+)?
                               (6(?P<RRRt>(\d|/){3}\d\s+))?
                               (7(?P<wwWW>\d{2}(\d|/)(\d|/))\s+)?
                               (8(?P<NCCC>(\d|/){4})\s+)?
                               (9(?P<GGgg>\d{4})\s+)?)?""",
                               re.VERBOSE)

s1_iihVV_re = re.compile(r"""((?P<ir>\d)(?P<ix>\d)(?P<h>(\d|\/))(?P<VV>\d\d))?""", re.VERBOSE)
s1_Nddff_re = re.compile(r"""((?P<N>(\d|/))(?P<dd>\d\d)(?P<ff>\d\d))?""", re.VERBOSE)
s1_00fff_re = re.compile(r"""((?P<wind_speed>\d{3}))?""", re.VERBOSE)
#s1_1sTTT_re = re.compile(r"""(?P<air_t>\d{4})""", re.VERBOSE)
#s1_2sTTT_re = re.compile(r"""(?P<dewp>\d{4})""", re.VERBOSE)
#s1_3PPPP_re = re.compile(r"""(?P<p_baro>.*)""", re.VERBOSE)
#s1_4PPPP_re = re.compile(r"""(?P<p_slv>.*)""", re.VERBOSE)
s1_5appp_re = re.compile(r"""((?P<a>\d)(?P<ppp>\d{3}))?""", re.VERBOSE)
s1_6RRRt_re = re.compile(r"""((?P<RRR>\d{3})(?P<t>(\d|/)))?""", re.VERBOSE)
s1_7wwWW_re = re.compile(r"""((?P<ww>\d{2})(?P<W1>\d)(?P<W2>\d))?""", re.VERBOSE)
s1_8NCCC_re = re.compile(r"""((?P<N>\d)(?P<CL>(\d|/))(?P<CM>(\d|/))(?P<CH>(\d|/)))?""", re.VERBOSE)
s1_9GGgg_re = re.compile(r"""((?P<observation_time>.*))?""", re.VERBOSE)


#split section 2
section_2_re  = re.compile(r"""((222(?P<dv>\d{2}))\s+
                               (0(?P<t_water>(\d|/){4})\s+)?
                               (1(?P<aPPHH>\d{4})\s+)?
                               (2(?P<bPPHH>\d{4})\s+)?
                               ((3(?P<dddd>\d\d\d\d)\s+){0,2})?
                               (4(?P<cPPHH>\d{4})\s+)?
                               (5(?P<dPPHH>\d{4})\s+)?
                               (6(?P<IEER>\d{4})\s+)?
                               (70(?P<HHH>\d{3})\s+)?
                               (8(?P<bsTTT>\d{4})\s+)?)?""",
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

s3_EsTT_re = re.compile(r"""((?P<E>\d)(?P<sTT>\d{3}))?""", re.VERBOSE)
s3_Esss_re = re.compile(r"""((?P<E>\d)(?P<sss>\d{3}))?""", re.VERBOSE)
s3_55SSS_re = re.compile(r"""(55(?P<rad_d_hours>\d\d\d)\s+
                             (0(?P<rad_d_net_pos>\d\d\d\d)\s+)?
                             (1(?P<rad_d_net_neg>\d\d\d\d)\s+)?
                             (2(?P<rad_d_global>\d\d\d\d)\s+)?
                             (3(?P<rad_d_diff>\d\d\d\d)\s+)?
                             (4(?P<rad_d_long_down>\d\d\d\d)\s+)?
                             (5(?P<rad_d_long_up>\d\d\d\d)\s+)?
                             (6(?P<rad_d_short>\d\d\d\d)\s+)?)?""",
                             re.VERBOSE)
s3_553SS_re = re.compile(r"""(553(?P<rad_h_hours>\d\d)\s+
                             (0(?P<rad_h_net_pos>\d\d\d\d)\s+)?
                             (1(?P<rad_h_net_neg>\d\d\d\d)\s+)?
                             (2(?P<rad_h_global>\d\d\d\d)\s+)?
                             (3(?P<rad_h_diff>\d\d\d\d)\s+)?
                             (4(?P<rad_h_long_down>\d\d\d\d)\s+)?
                             (5(?P<rad_h_long_up>\d\d\d\d)\s+)?
                             (6(?P<rad_h_short>\d\d\d\d)\s+)?)?""",
                             re.VERBOSE)
s3_8NChh_re = re.compile(r"""((8(?P<c1>\d(\d|/)\d\d)\s+)?
                             (8(?P<c2>\d(\d|/)\d\d)\s+)?
                             (8(?P<c3>\d(\d|/)\d\d)\s+)?
                             (8(?P<c4>\d(\d|/)\d\d)\s+)?)?""",
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

def missing_value(f):
    def decorated(*args, **kwargs):
        if args[1] is None:
            return np.nan
        else:
            return f(*args, **kwargs)
    return decorated

class synop(object):
    """
    SYNOP report

    References
    ----------
    [1] World Meteorological Organization (WMO). 2011. Manual on Codes - International Codes,
        Volume I.1, Annex II to the WMO Technical Regulations: Part A- Alphanumeric Codes.
        2011 edition updated in 2017. WMO.
    [2] Link to WMO manual on codes: https://community.wmo.int/activity-areas/wmo-codes/manual-codes#Codes
    [3] http://www.met.fu-berlin.de/~manfred/fm12.html

    Todo
    ----
    - plausibility checks between groups
        - e.g. cloud height in 8NChh is <30m and fog events
    - handling of classes for contious variables (e.g. cloud height 0-49m etc.)
        - add additional information if value is a class or contious (se)
    - put cloud cover in groups 8NCCC and Nddff in separate method
    - translate code classes to english with wmo code tables
    - add exceptions from the wmo manual of codes for group "rules" to methods
    - check conversion of wind direction angles (also add conversion of angles to words for printing)
    - add decoding of special weather conditions in 9SSss group of section 3
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
        self.decoded = None 
        self.type = "SYNOP"
        self.datetime = None
        self.station_id = None

        
        #decoded is a dict of dicts in form {"section_x": {"group_name or variable": value}}
        self.decoded = sections_re.match(self.raw).groupdict("")
        #split raw report into its sections then split each section into
        #its groups and handle (decode) each group
        #use sorted to make sure report is decoded starting with section 0
        for sname in sorted(self.decoded.keys()):
            sraw = self.decoded[sname]
            pattern, ghandlers = self.handlers[sname]
            #TODO
            #- add try except for matching and collect string when  match is empty
            #sec_groups = patter.match(sraw).groupdict()
            #self.decoded[sname] = pattern.match(sraw).groupdict()
            gd = pattern.match(sraw).groupdict("")
            #try:
                #gd = pattern.match(sraw).groupdict("")
            #except:
                #print(self.raw)
                #print(self.decoded)
                #print(sname, sraw)

            #if section is not none create dictionary for it
            self.decoded[sname] = {}
            for gname, graw in gd.items():
                if gname not in ghandlers:
                    continue
                gpattern, ghandler = ghandlers[gname]
                #if the group can be decoded directly without further regex pattern
                #handle it directly otherwise match it against a group pattern
                if gpattern is None:
                    self.decoded[sname][gname] = ghandler(self, graw)
                else:
                    group = gpattern.match(graw)
                    #_report_match(ghandler, group.group())
                    #self.decoded[sname][gname] = ghandler(self, group.groupdict())
                    self.decoded[sname].update(ghandler(self, group.groupdict("")))


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
        return STATION_TYPE_CODE[code]


    def _handle_wind_unit(self, code):
        return WIND_UNIT_CODE.get(code)


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
        if code == "" or code == "////" or "/" in code:
            return np.nan
        else:
            sign = int(code[0])
            value = int(code[1:])
            
            if sign == 0:
                sign = -1
            elif sign == 1:
                sign = 1
            #sign = 9 => relative humidity
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
        if code == "" or code is None:
            return np.nan
        else:
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
        
        if not code == "//" and code != "":
            code = int(code)
        else:
            return np.nan
        
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

        iihVV = {"precip_group": PRECIP_GROUP_CODE.get(d["ir"]),
                 "station_operation": STATION_OPERATION_TYPE_CODE.get(d["ix"]),
                 "cloud_height": CLOUD_HEIGHT_0_CODE.get(d["h"]),
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
        if cloud_cover == "/" or cloud_cover == "":
            #not observed
            cloud_cover = np.nan
        #elif cloud_cover == "9":
            ##sky not observable/visible
            #cloud_cover = -99
        else:
            cloud_cover = int(cloud_cover)


        if d["dd"] != "":
            wind_dir = int(d["dd"])
            if wind_dir == 0:
                #no wind
                wind_dir = np.nan
            elif wind_dir == 99:
                #circular wind
                wind_dir = -99
            else:
                #01: 5-14
                #02: 15-24
                #03: 25-34
                #decoding the class to single value in the middle of the class
                wind_dir = (10 * wind_dir) - 1
        else:
            wind_dir = np.nan


        #wind speed is greater than 99 units and this group is directly followed
        #by the 00fff group
        if d["ff"] != "":
            wind_speed = int(d["ff"])
        else:
            wind_speed = np.nan

        #convert units if necessary
        #use unit indicator of section_0
        w_unit = self.decoded["section_0"]["wind_unit"]
        knots_to_mps_factor = 0.51444444444444
        if w_unit in ["knots estimate", "knots measured"]:
            wind_speed = wind_speed * knots_to_mps_factor

        Nddff = {"cloud_cover_tot": cloud_cover,
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
        ws = d["wind_speed"]
        if ws == "":
            return {"wind_speed": np.nan}
        else:
            return {"wind_speed": int(ws)}


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

        appp = {"p_tendency": A_CODE.get(d["a"]),
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

        precip_ref_time = T_CODE[d["t"]]

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
        wwWW = {"current_weather": CURRENT_WEATHER_CODE[d["ww"]],
                "w_course1": WEATHER_COURSE_CODE[d["W1"]],
                "w_course2": WEATHER_COURSE_CODE[d["W2"]]}

        return wwWW


    def _handle_8NCCC(self, d):
        """
        Handles 8NCCC group in section 1

        Information about cloud types

        N: cover of low clouds if not present amount of medium high clouds
        C: type of low clouds (CL)
        C: type of medium clouds (CM)
        C: type of high clouds (CH)


        Parameters
        ----------
        d : dict
            re groupdict

        """

        NCCC = {"cloud_cover_lowest": d["N"],
                "cloud_type_low": LOW_CLOUDS_CODE[d["CL"]],
                "cloud_type_medium": MEDIUM_CLOUDS_CODE[d["CM"]],
                "cloud_type_high": HIGH_CLOUDS_CODE[d["CH"]],
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
        #use ESTT_GROUND_CONDITIONS_CODE dictionary here
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
        sh = np.nan
        if not d["sss"] == "":
            sh = int(d["sss"])

        Esss = {"ground_cond": ESSS_GROUND_CONDITIONS_CODE[d["E"]],
                "snow_height": sh}

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
        d = {k: int(v) for k,v in d.items() if not v == ""}
        if "rad_h_hours" in d and not d["rad_h_hours"] == "":
            d["rad_h_hours"] = d["rad_h_hours"] / 10.0

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
        d = {k: int(v) for k,v in d.items() if not v == ""}
        if "rad_d_hours" in d and not d["rad_d_hours"] == "":
            d["rad_d_hours"] = d["rad_d_hours"] / 10.0

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
        if d == "":
            return np.nan
        else:
            d = int(d)

            if d >= 9998:
                precip = 999
            elif d == 9999:
                precip = np.nan
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
                h = CLOUD_HEIGHT_CLASSES[code] 
            else:
                h = np.nan

            return h, type


        layer_re = re.compile(r"""(((?P<cover>\d)(?P<type>(\d|/))(?P<height>\d\d)))?""", re.VERBOSE)

        #count cloud layers
        c_nlayers = 0


        for l, v  in list(d.items()):
            if not v is None:
                layer = layer_re.match(v).groupdict("")
                cover = layer["cover"]
                if cover != "/" and cover != "":
                    c_nlayers += 1
                    cover = int(cover)
                    d[l + "_cover"] = cover
                    #layer["cover"] = int(layer["cover"])
                else:
                    d[l + "_cover"] = np.nan
                    #layer["cover"] = "NA"

                if layer["type"] != "":
                    d[l + "_type"] = CLOUD_TYPE_CODE[layer["type"]]
                else:
                    d[l + "_type"] = np.nan
                #layer["type"] = CLOUD_TYPE_CODE[layer["type"]]

                if layer["height"] != "":
                    h, t = cheight(layer["height"])
                    d[l + "_height"] = h
                    d[l + "_measurement"] = t
                else:
                    d[l + "_height"] = np.nan
                    d[l + "_measurement"] = np.nan

                    #layer["height"] = h
                    #layer["measurement"] = t
                    #d[l] = layer
                    #drop item with l key
                del d[l]
            else:
                d[l] = np.nan

            d["c_nlayers"] = c_nlayers

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
    


    #format of the handlers is (group_regex_pattern, handler)
    #if group regex pattern is None the group can be directly decoded e.g. a single variable in a group
    #otherwise a pattern is used to split the group using regex so the handler can access each variable
    #from a dictionary
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
                      "t_air": (None, _handle_sTTT),
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
                     {"t_water": (None, _handle_sTTT),
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

    def to_dict(self, vars=None):
        """
        Convert selected variables of report to a pandas dataframe

        Parameters
        ----------
        vars : list of str
            List of variables to include

        Returns
        -------
        dict

        """
        vardict = {}

        for i in self.decoded.values():
            if i is not None:
                vardict.update(i)

        if vars is not None:
            vardict = {x:y for x,y in vardict.items() if x in vars}

        #print(vardict)
        #print("===============")

        return vardict
