#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Decoding handlers.

Handlers for decoding the SYNOP groups.

"""

import re
import logging
import numpy as np
from .code_descriptions import (STATION_TYPE_CODE, WIND_UNIT_CODE, PRECIP_GROUP_CODE, STATION_OPERATION_TYPE_CODE,
CLOUD_TYPE_CODE, CLOUD_HEIGHT_0_CODE, A_CODE, T_CODE, CURRENT_WEATHER_CODE, WEATHER_COURSE_CODE,
LOW_CLOUDS_CODE, MEDIUM_CLOUDS_CODE, HIGH_CLOUDS_CODE, ESSS_GROUND_CONDITIONS_CODE,
CLOUD_HEIGHT_CLASSES, CLOUD_TYPE_CODE)


_logger = logging.getLogger(__name__)


def default_handler(code):
    """Handle non decodable codes.

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


def handle_MMMM( code):
    """Decode station type."""
    return STATION_TYPE_CODE[code]


def handle_wind_unit(code):
    """Decode wind unit."""
    return WIND_UNIT_CODE.get(code)


def handle_sTTT(code):
    """Decode temperature.

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
            sign = 1
        elif sign == 1:
            sign = -1
        #sign = 9 => relative humidity
        elif sign == 9:
            return value

        value = sign * value * 0.1

        return value


def handle_PPPP(code):
    """Decode pressure.

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

        if code[0] == "0":
            value = 1000 + value

        return value


#@static_method
def handle_vis(code):
    """Decode visibility of synop report.

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


def handle_iihVV(d):
    """Handle iihVV group in section 1.

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
             "vis": handle_vis(d["VV"])}

    return iihVV


def handle_Nddff(d):
    """Handle Nddff group in section 1.

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

    Nddff = {"cloud_cover_tot": cloud_cover,
             "wind_dir": wind_dir,
             "wind_speed": wind_speed}

    return Nddff


def handle_00fff(d):
    """Handle 00fff group in section 1.

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


def handle_5appp(d):
    """Handle 5appp group in section 1.

    3 hourly tendency of station air pressure

    a: type of pressure tendency
    ppp: absolute pressure change over last three hours in 1/10 Hectopascal


    Parameters
    ----------
    d : dict
        re groupdict

    """
    appp = {"p_tendency": A_CODE.get(d["a"]),
             "p_diff": handle_PPPP(d["ppp"])}

    return appp


def handle_6RRRt(d):
    """Handle 6RRRt group in section 1.

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


def handle_7wwWW(d):
    """Handle 7wwWW group in section 1.

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


def handle_8NCCC(d):
    """Handle 8NCCC group in section 1.

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
            "cloud_type_high": HIGH_CLOUDS_CODE[d["CH"]]
            }

    return NCCC


def handle_9GGgg(d):
    """Handle 9GGgg group in section 1.

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
def handle_3EsTT(d):
    """Handle 3EsTT group in section 3.

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


def handle_4Esss(d):
    """Handle 4Esss group in section 3.

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


def handle_55SSS(d):
    """Handle 55SSS group and the groups following it in section 3.

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


def handle_553SS(d):
    """Handle 553SS group and the groups following it in section 3.

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


def handle_6RRRt(d):
    """Handle 6RRRt group in section 3.

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


def handle_7RRRR(d):
    """Handle 7RRRR group in section 3.

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


def handle_8NChh(d):
    """Handle 8NChh group in section 3.

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
        """Decode cloud height.

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

    for l, v in list(d.items()):
        if v is not None:
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


def handle_9GGgg(d):
    """Handle 9GGgg group in section 1.

    Observation time (UTC)

    GG: hours
    gg: minutes


    Parameters
    ----------
    d : dict
        re groupdict

    """
    return d
