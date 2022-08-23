import math

import piexif


# Highly recommend checking this:
# https://exiftool.org/TagNames/GPS.html
# https://gis.stackexchange.com/questions/136925/how-to-parse-exif-gps-information-to-lat-lng-decimal-numbers
# https://support.google.com/maps/answer/18539?hl=de&co=GENIE.Platform%3DDesktop
# https://www.latlong.net/lat-long-dms.html


class GpsClass:
    lat: float
    lon: float
    alt: float

    """
    
    EXIF:
    Zeitpunkt Digitalisierung: 29.08.2020, 13:03:41
    Zeitpunkt Aufnahme: 29.08.2020, 13:03:41
    
    GPS:
    Höhe: 101 m (331,36 Fuß)
    Höhenreferenz: über dem Meeresspiegel
    Datumstempel: 29.08.2020
    GPS-Version: 2.2.0.0
    Breitengrad: 52° 21’ 37,998” N
    Längengrad: 9° 45’ 43,002” O
    Zeitstempel: 11:03:24 UTC
    
    TIFF:
    Datum/Uhrzeit: 29.08.2020, 13:03:41
    
    
    JSON:
    "creationTime": {
        "timestamp": "1598733191",
        "formatted": "29.08.2020, 20:33:11 UTC"
    },
    "photoTakenTime": {
        "timestamp": "1598699021",
        "formatted": "29.08.2020, 11:03:41 UTC"
    },
    "geoData": {
        "latitude": 52.3605556,
        "longitude": 9.761944399999999,
        "altitude": 101.0,
        "latitudeSpan": 0.0,
        "longitudeSpan": 0.0
    },
    
    piexif:
    {
        0: (2, 2, 0, 0), 
        
        1: b'N', 
        2: ((52, 1), (21, 1), (38, 1)), 
        3: b'E', 
        4: ((9, 1), (45, 1), (43, 1)), 
        5: 0, 
        6: (101, 1), 
        
        7: ((11, 1), (3, 1), (24, 1)), 
        29: b'2020:08:29'}
        
    piexif.GPSIFD.GPSVersionID,     #0
    
    piexif.GPSIFD.GPSLatitudeRef,   #1
    piexif.GPSIFD.GPSLatitude,      #2
    piexif.GPSIFD.GPSLongitudeRef,  #3
    piexif.GPSIFD.GPSLongitude,     #4
    piexif.GPSIFD.GPSAltitudeRef,   #5
    piexif.GPSIFD.GPSAltitude,      #6
    
    piexif.GPSIFD.GPSTimeStamp,     #7
    piexif.GPSIFD.GPSDateStamp]     #29

    """

    def __init__(self, gps):
        """
        Creates instance of GpsClass by given input
        :param gps: Either Google Takeout JSON 'geoData' dict or piexif 'GPS' dict or simple tuple (lat, lon, alt).
        """
        if isinstance(gps, tuple.__class__):
            pass
        elif isinstance(gps, dict.__class__):
            # Minimal info needed for GPS data
            json_keys = ['latitude', 'longitude', 'altitude']
            exif_keys = [1, 2, 3, 4, 5, 6]
            is_json_format = True
            is_exif_format = True
            for key in json_keys:
                if key not in gps.keys():
                    is_json_format = False

            for key in exif_keys:
                if key not in gps.keys():
                    is_exif_format = False

            if is_json_format and not is_exif_format:
                self.lat = float(gps["latitude"])
                self.lon = float(gps["longitude"])
                self.alt = float(gps["altitude"])
                return
            elif not is_json_format and is_exif_format:
                lat_ref = gps[piexif.GPSIFD.GPSLatitudeRef]
                lat = gps[piexif.GPSIFD.GPSLatitude]

                lon_ref = gps[piexif.GPSIFD.GPSLongitudeRef]
                lon = gps[piexif.GPSIFD.GPSLongitude]

                alt_ref = gps[piexif.GPSIFD.GPSAltitudeRef]
                alt = gps[piexif.GPSIFD.GPSAltitude]

                self.lat = GpsClass.rela3_to_dd(lat)
                if lat_ref == b"N":
                    pass
                elif lat_ref == b"S":
                    self.lat = self.lat * -1
                else:
                    raise ValueError("It's either N or S. You have %s" % lat_ref)

                self.lon = GpsClass.rela3_to_dd(lon)
                if lon_ref == b"E":
                    pass
                elif lon_ref == b"W":
                    self.lon = self.lon * -1
                else:
                    raise ValueError("It's either E or W. You have %s" % lon_ref)

                self.alt = GpsClass.rela_to_dd(alt)
                if alt_ref == 0:
                    pass
                elif alt_ref == 1:
                    self.alt = self.alt * -1
                else:
                    raise ValueError("It's either above or below sea level. You have %s" % alt_ref)

            elif is_json_format and is_exif_format:
                raise ValueError("Is your given dict empty?! Why tho...\ndict len: %d" % len(gps))
            else:
                raise ValueError("Given dict does not contain all needed info. Is it even in right format?\n%s" % gps)
        else:
            raise ValueError("Unknown type for GPS. Please read documentation!")

    @staticmethod
    def rela3_to_dd(coords: tuple) -> float:
        if len(coords) != 3:
            raise ValueError("Expected 3 values inside tuple.\nGot %d values.\n%s" % (len(coords), coords))
        # degree_numerator: float = coords[0][0]
        # degree_denominator: float = coords[0][1]
        # minutes_numerator: float = coords[1][0]
        # minutes_denominator: float = coords[1][1]
        # seconds_numerator: float = coords[2][0]
        # seconds_denominator: float = coords[2][1]
        # degrees: float = degree_numerator / degree_denominator
        # minutes: float = minutes_numerator / minutes_denominator
        # seconds: float = seconds_numerator / seconds_denominator
        degrees = GpsClass.rela_to_dd(coords[0])
        minutes = GpsClass.rela_to_dd(coords[1])
        seconds = GpsClass.rela_to_dd(coords[2])
        dd = degrees + minutes / 60 + seconds / 3600
        return dd

    @staticmethod
    def rela_to_dd(tup: tuple) -> float:
        if len(tup) != 2:
            raise ValueError("Expected 2 values (numerator, denominator) inside the tuple."
                             "\nLen: %d\nTup: %s" % (len(tup), tup))
        return tup[0] / tup[1]

    @staticmethod
    def dd_to_rela(dd: float) -> tuple:
        if dd < 0:
            dd *= -1
        denominator = 1
        while int(dd) != dd:
            dd *= 10
            dd = round(dd, 4)
            denominator *= 10
        return int(dd), int(denominator)

    @staticmethod
    def dd_to_rela3(dd: float) -> tuple:
        if dd < 0:
            dd *= -1

        degree = int(dd), 1
        dd -= degree[0]
        dd *= 60
        minutes = int(dd), 1
        dd -= minutes[0]
        dd *= 60
        dd = round(dd, 3)
        seconds = GpsClass.dd_to_rela(dd)
        return degree, minutes, seconds

    def __eq__(self, other):
        # Maybe this needs some delta/epsilon for some marginal difference
        # A good precision could be 52.360555 9.761944 == 52.360505 9.762012
        # At least to the 5th after decimal point
        if isinstance(other, self.__class__):
            other: GpsClass = other
            if math.isclose(self.lat, other.lat, abs_tol=0.0001):
                if math.isclose(self.lon, other.lon, abs_tol=0.0001):
                    if math.isclose(self.alt, other.alt, abs_tol=0.0001):
                        return True
        return False

    def to_dd(self):
        return self.lat, self.lon, self.alt

    def to_exif(self) -> dict:
        if self.lat < 0:
            lat_ref = "S"
        else:
            lat_ref = "N"
        if self.lon < 0:
            lon_ref = "W"
        else:
            lon_ref = "E"
        if self.alt < 0:
            alt_ref = 1
        else:
            alt_ref = 0

        gps_dict: dict = {
            # Some version. Don't know differences between versions, but 2000 seems legit.
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: lat_ref,
            piexif.GPSIFD.GPSLatitude: GpsClass.dd_to_rela3(self.lat),
            piexif.GPSIFD.GPSLongitudeRef: lon_ref,
            piexif.GPSIFD.GPSLongitude: GpsClass.dd_to_rela3(self.lon),
            piexif.GPSIFD.GPSAltitudeRef: alt_ref,
            piexif.GPSIFD.GPSAltitude: GpsClass.dd_to_rela(self.alt),
        }
        return gps_dict
