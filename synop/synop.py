#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""synop object for decoding SYNOP reports."""
import re
import logging
import numpy as np

from .handlers import (default_handler, handle_MMMM, handle_wind_unit, handle_iihVV, handle_Nddff, handle_00fff,
handle_sTTT, handle_PPPP, handle_5appp, handle_6RRRt, handle_7wwWW, handle_8NCCC, handle_9GGgg, handle_3EsTT,
handle_4Esss, handle_55SSS, handle_553SS, handle_7RRRR, handle_8NChh)

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
section_1_re = re.compile(r"""((?P<iihVV>(\d|\/){5})\s+
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
section_2_re = re.compile(r"""((222(?P<dv>\d{2}))\s+
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
    """Report success or failure of the given handler function. (DEBUG)."""
    if match:
        _logger.debug("%s matched '%s'", handler.__name__, match)
    else:
        _logger.debug("%s didn't match...", handler.__name__)


def missing_value(f):
    """Missing value decorator."""
    def decorated(*args, **kwargs):
        if args[1] is None:
            return np.nan
        else:
            return f(*args, **kwargs)
    return decorated


class synop(object):
    """SYNOP report.

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
        """Decode SYNOP report.

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
                    self.decoded[sname][gname] = ghandler(graw)
                else:
                    group = gpattern.match(graw)
                    #_report_match(ghandler, group.group())
                    #self.decoded[sname][gname] = ghandler(self, group.groupdict())
                    self.decoded[sname].update(ghandler(group.groupdict("")))

    #format of the handlers is (group_regex_pattern, handler)
    #if group regex pattern is None the group can be directly decoded e.g. a single variable in a group
    #otherwise a pattern is used to split the group using regex so the handler can access each variable
    #from a dictionary
    sec0_handlers = (section_0_re,
                     {"datetime": (None, default_handler),
                      "MMMM": (None, handle_MMMM),
                      "monthdayr": (None, default_handler),
                      "hourr": (None, default_handler),
                      "wind_unit": (None, handle_wind_unit),
                      "station_id": (None, default_handler)
                      })

    sec1_handlers = (section_1_re,
                     {"iihVV": (s1_iihVV_re, handle_iihVV),
                      "Nddff": (s1_Nddff_re, handle_Nddff),
                      "fff": (s1_00fff_re, handle_00fff),
                      "t_air": (None, handle_sTTT),
                      "dewp": (None, handle_sTTT),
                      "p_baro": (None, handle_PPPP),
                      "p_slv": (None, handle_PPPP),
                      "appp": (s1_5appp_re, handle_5appp),
                      "RRRt": (s1_6RRRt_re, handle_6RRRt),
                      "wwWW": (s1_7wwWW_re, handle_7wwWW),
                      "NCCC": (s1_8NCCC_re, handle_8NCCC),
                      "GGgg": (s1_9GGgg_re, handle_9GGgg),
                      })

    sec2_handlers = (section_2_re,
                     {"t_water": (None, handle_sTTT),
                      "aPPHH": (None, default_handler),
                      "bPPHH": (None, default_handler),
                      "dddd": (None, default_handler),
                      "cPPHH": (None, default_handler),
                      "dPPHH": (None, default_handler),
                      "IEER": (None, default_handler),
                      "HHH": (None, default_handler),
                      "bsTTT": (None, handle_sTTT),
                      })

    sec3_handlers = (section_3_re,
                     {"xxxx": (None, default_handler),
                      "t_max": (None, handle_sTTT),
                      "t_min": (None, handle_sTTT),
                      "EsTT": (s3_EsTT_re, handle_3EsTT),
                      "Esss": (s3_Esss_re, handle_4Esss),
                      "SSS": (s3_55SSS_re, handle_55SSS),
                      "SS": (s3_553SS_re, handle_553SS),
                      "RRRt": (s1_6RRRt_re, handle_6RRRt),
                      "precip": (None, handle_7RRRR),
                      "NChh": (s3_8NChh_re, handle_8NChh),
                      "SSss": (None, default_handler),
                      })

    sec4_handlers = (section_4_re,
                     {"any": (None, default_handler),
                      })

    sec5_handlers = (section_5_re,
                     {"any": (None, default_handler),
                      })

    sec6_handlers = (section_6_re,
                     {"any": (None, default_handler),
                      })

    sec9_handlers = (section_9_re,
                     {"any": (None, default_handler),
                      })

    handlers = {"section_0": sec0_handlers,
                "section_1": sec1_handlers,
                "section_2": sec2_handlers,
                "section_3": sec3_handlers,
                "section_4": sec4_handlers,
                "section_5": sec5_handlers,
                "section_6": sec6_handlers,
                "section_9": sec9_handlers
                }

    def __str__(self):
        def prettydict(d, indent=0):
            """Print dict (of dict) pretty with indent.

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
                    print("\t" * indent + str(key) + ": " + str(value))
            return

        prettydict(self.decoded)

        return

    def convert_units(self):
        """Convert units."""
        #convert units if necessary
        #use unit indicator of section_0
        w_unit = self.decoded["section_0"]["wind_unit"]
        wind_speed = self.decoded["section_1"]["wind_speed"]
        knots_to_mps_factor = 0.51444444444444
        if w_unit in ["knots estimate", "knots measured"]:
            wind_speed = wind_speed * knots_to_mps_factor
        else:
            return

        if "estimate" in w_unit:
            new_wind_unit = "meters per second estimate"
        else:
            new_wind_unit = "meters per second measured"

        self.decoded["section_0"]["wind_unit"] = new_wind_unit
        self.decoded["section_1"]["wind_speed"] = wind_speed

    def to_dict(self, vars=None):
        """Convert selected variables of report to a pandas dataframe.

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
