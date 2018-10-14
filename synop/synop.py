#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
import datetime
import logging

_logger = logging.getLogger(__name__)

#regex definitions
#split report into its sections
sections_re = re.compile(r"""(?P<section_0>[\d]{12}\s+(AAXX|BBXX|OOXX)\s+[\d]{5}\s+[\d]{5})\s+
                             (?P<section_1>(\d{5}\s+){0,9})
                             ((222\s+)(?P<section_2>(\d{5}\s+){0,9})){0,1}
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
                               (?P<Nddff>(\d|/)\d{3})\s+
                               (00(?P<fff>\d{3})\s+)?
                               (1(?P<asTTT>\d{4})\s+)?
                               (2(?P<bsTTT>\d{4})\s+)?
                               (3(?P<aPPPP>(\d\d\d\d|\d\d\d\/))\s+)?
                               (4(?P<bPPPP>(\d\d\d\d|\d\d\d\/))\s+)?
                               (5(?P<appp>\d{4})\s+)?
                               (6(?P<RRRt>\d{4})\s+)?
                               (7(?P<wwW>\d{4})\s+)?
                               (8(?P<NCCC>(\d|/){4})\s+)?
                               (9(?P<GGgg>\d{4})\s+)?""",
                               re.VERBOSE)

s1_iihVV_re = re.compile(r"""(?P<ir>\d)(?P<ix>\d)(?P<h>\d)(?P<VV>\d\d)""", re.VERBOSE)
s1_Nddff_re = re.compile(r"""(?P<N>\d)(?P<dd>\d\d)(?P<ff>\d\d)""", re.VERBOSE)
s1_00fff_re = re.compile(r"""(?P<wind_speed>\d{3})""", re.VERBOSE)
s1_1sTTT_re = re.compile(r"""(?P<air_t>\d{4})""", re.VERBOSE)
s1_2sTTT_re = re.compile(r"""(?P<dewp>\d{4})""", re.VERBOSE)
s1_3PPPP_re = re.compile(r"""(?P<p_baro>.*)""", re.VERBOSE)
s1_4PPPP_re = re.compile(r"""(?P<p_slv>.*)""", re.VERBOSE)
s1_5appp_re = re.compile(r"""(?P<a>\d)(?P<ppp>\d{3})""", re.VERBOSE)
s1_6RRRt_re = re.compile(r"""(?P<RRR>\d{3})(?P<t>(\d|/))""", re.VERBOSE)
s1_7wwWW_re = re.compile(r"""(?P<ww>\d{2})(?P<W1>\d)(?P<W2>\d)""", re.VERBOSE)
s1_8NCCC_re = re.compile(r"""(?P<N>\d)(?P<CL>(\d|/))(?P<CM>(\d|/))(?P<CH>(\d|/))""", re.VERBOSE)
s1_9GGgg_re = re.compile(r"""(?P<observation_time>.*)""", re.VERBOSE)


#split section 3
#separate handling of groups
section_3_re  = re.compile(r"""(?P<tmax_12>(1(?P<sign>\d)(?P<value>\d\d\d)\s+))?
                               (?P<tmin_12>(2(?P<sign1>\d)(?P<value1>\d\d\d)\s+))?
                               (?P<tmin_12_boden>(3(?P<ground_state>\d)(?P<sign2>\d)(?P<value2>\d\d)\s+))?
                               (?P<snow_cover>(4(?P<ground_state1>\d)(?P<value3>\d\d\d)\s+))?
                               (?P<sun_prev_day>(55(?P<duration>\d\d\d)\s+(2(?P<rad_sum>\d\d\d\d)\s+)?(3(?P<rad_diff>\d\d\d\d)\s+)?(4(?P<rad_ir>\d\d\d\d)\s+)?))?
                               (?P<sun_prev_hour>(553(?P<duration1>\d\d)\s+(2(?P<rad_sum1>\d\d\d\d)\s+)?(3(?P<rad_diff1>\d\d\d\d)\s+)?(4(?P<rad_ir1>\d\d\d\d)\s+)?))?
                               (?P<precip>(6(?P<value4>(\d\d\d|///))(?P<ref_time>\d)\s+))?
                               (7(?P<precip_24>\d\d\d\d)\s+)?
                               (?P<clouds>(8(?P<code>\d\d\d\d)\s+){0,4})?
                               (?P<special_weather>(9(?P<code1>\d\d\d\d)\s+){0,6})?""",
                               re.VERBOSE)

section_3_re = re.compile(r"""(0(?P<xxxx>\d{4}\s+))?
                              (1(?P<asTTT>\d{4}\s+))?
                              (2(?P<bsTTT>\d{4}\s+))?
                              (3(?P<EsTT>\d{4}\s+))?
                              (4(?P<Esss>(\d|/)\d{3}\s+))?
                              ((55(?P<SSS>\d\d\d)\s+)(2\d{4}\s+)?(3\d{4}\s+)?(4\d{4}\s+)?)?
                              ((553(?P<SS>\d\d)\s+)(2\d{4}\s+)?(3\d{4}\s+)?(4\d{4}\s+)?)?
                              (6(?P<RRRt>(\d\d\d|///)\d\s+))?
                              (7(?P<RRRR>\d{4}\s+))?
                              ((8(?P<NChh>\d(\d|/)\d\d\s+)?){0,4})?
                              (9(?P<SSss>\d{4}\s+))?""",
                              re.VERBOSE)


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
                    gpattern, ghandler = ghandlers[gname]
                    group = gpatter.match(graw)
                    _report_match(ghandler, group.group())

                    self.decoded[sname][gname] = ghandler(self, group.groupdict())
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


	@static_method
	def _handle_vis(code):
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
			dist = 6 + (code - 56)
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

        N: total cloud cover in 1/8
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
        elif cloud_cover == "9":
            #sky not observable/visible
            cloud_cover = -99
        else:
            cloud_cover = int(cloud_cover) / 8


        wind_dir = int(d["dd"])
        if wind_dir == 0:
            #no wind
            wind_dir = "NA"
        elif wind_dir == 99:
            #circular wind
            wind_dir = -99
        else:
            #is this conversion correct????
            wind_dir = (360/98) * wind_dir


        #wind speed is greater than 99 units and this group is directly followed
        #by the 00fff group
        wind_speed = int(d["ff"])

        Nddff = {"cloud_cover": cloud_cover,
                 "wind_dir": wind_dir,
                 "wind_speed": wind_speed}

        return Nddff


	def _handle_5appp(self, d):
		"""
		Handles 5appp group in section 1

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
        
        ww: current weather
        W: weather course (W1)
        W: weather course (W2)


		Parameters
		----------
        d : dict
            re groupdict

		"""

        return d


	def _handle_8NCCC(self, d):
		"""
		Handles 8NCCC group in section 1

        N: amount of low clouds if not present amount of medium high clouds
        C: type of low clouds (CL)
        C: type of medium clouds (CM)
        C: type of high clouds (CH)


		Parameters
		----------
        d : dict
            re groupdict

		"""

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
        time = d["observation_time"]

        return d


    sec0_handlers = (section_0_re,
                     {"datetime": _default_handler,
                      "MMMM": _handle_MMMM,
                      "monthdayr": _default_handler,
                      "hourr": _default_handler,
                      "wind_unit": _handle_wind_unit,
                      "station _id": _default_handler})

    sec1_handlers = (section_1_re,
                     {"iihVV": (s1_iihVV_re, _handle_iihVV),
                      "Nddff": (s1_Nddff_re, _handle_Nddff),
                      "fff": (s1_00fff_re, _handle_00fff),
                      "asTTT": (s1_1sTTT_re, _handle_sTTT),
                      "bsTTT": (s1_2sTTT_re, _handle_sTTT),
                      "aPPPP": (s1_3PPPP_re, _handle_PPPP),
                      "bPPPP": (s1_4PPPP_re, _handle_PPPP),
                      "appp": (s1_5appp_re, _handle_5appp),
                      "RRRt": (s1_6RRRt_re, _handle_6RRRt),
                      "wwWW": (s1_7wwWW_re, _handle_7wwWW),
                      "NCCC": (s1_8NCCC_re, _handle_8NCCC),
                      "GGgg": (s1_9GGgg_re, _handle_9GGgg),
                     })

    #sec2_handlers = (section_2_re,
                     #{"": })
    sec2_handlers = "test"

    sec3_handlers = (section_3_re,
                     {"xxxx": _default_handler,
                      "asTTT": _default_handler,
                      "bsTTT": _default_handler,
                      "EsTT": _default_handler,
                      "Esss": _default_handler,
                      "SSS": _default_handler,
                      "SS": _default_handler,
                      "RRRt": _default_handler,
                      "RRRR": _default_handler,
                      "NChh": _default_handler,
                      "SSss": _default_handler,
                     })

    #sec4_handlers = (section_4_re,
                     #{"": })

    #sec5_handlers = (section_5_re,
                     #{"": })

    #sec6_handlers = (section_6_re,
                     #{"": })

    #sec9_handlers = (section_9_re,
                         #{"": })

    sec4_handlers = "test"
    sec5_handlers = "test"
    sec6_handlers = "test"
    sec9_handlers = "test"

    handlers = {"section_0": sec0_handlers,
                     "section_1": sec1_handlers,
                     "section_2": sec2_handlers,
                     "section_3": sec3_handlers,
                     "section_4": sec4_handlers,
                     "section_5": sec5_handlers,
                     "section_6": sec6_handlers,
                     "section_9": sec9_handlers}


    def __str__(self):
        return NotImplementedError
