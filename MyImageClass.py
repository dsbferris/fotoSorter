import piexif
import os
from datetime import datetime
from old.gps_convert import change_to_rational, to_deg
import json
from GpsClass import GpsClass
from subprocess import call
import platform


class MyImageClass:
    filepath: str
    json_filepath: str

    # Recommended to use PhotoTakenTime
    json_photoTakenTime: datetime | None = None
    json_creationTime: datetime | None = None

    exif_zeroth_timestamp: datetime | None = None
    exif_digitized_timestamp: datetime | None = None
    exif_original_timestamp: datetime | None = None

    json_gps: GpsClass = None
    exif_gps: GpsClass = None

    def __init__(self, filepath: str, json_filepath: str, exif_dict: dict | None = None):
        self.filepath = filepath
        self.json_filepath = json_filepath

        self._read_data_from_json()
        self._read_data_from_exif(exif_dict)

    def _read_data_from_json(self):
        # TODO COMMENT!
        with open(self.json_filepath, "r") as json_file:
            json_dict = json.load(json_file)
        if "photoTakenTime" in json_dict.keys():
            photo_taken_time = json_dict["photoTakenTime"]
            if "timestamp" in photo_taken_time:
                timestamp = photo_taken_time["timestamp"]
                timestamp = float(timestamp)
                self.json_photoTakenTime = datetime.fromtimestamp(timestamp)
        if "creationTime" in json_dict.keys():
            creation_time = json_dict["photoTakenTime"]
            if "timestamp" in creation_time:
                timestamp = creation_time["timestamp"]
                timestamp = float(timestamp)
                self.json_creationTime = datetime.fromtimestamp(timestamp)

        if "geoData" in json_dict.keys():
            self.json_gps = GpsClass(json_dict["geoData"])

    def _read_data_from_exif(self, exif_dict: dict | None = None):
        # TODO COMMENT!
        if exif_dict is None:
            exif_dict = piexif.load(self.filepath)
        keys = exif_dict.keys()
        if "0th" in keys:
            zeroth = exif_dict["0th"]
            if piexif.ImageIFD.DateTime in zeroth.keys():
                zeroth_dt = zeroth[piexif.ImageIFD.DateTime]
                self.exif_zeroth_timestamp = MyImageClass._datetime_from_exif_str(str(zeroth_dt))
        if "1st" in keys:
            first = exif_dict["1st"]
            if piexif.ImageIFD.DateTime in first.keys():
                # Most programms will only read/write to the first/0th EXIF data block,
                # but some may read/write from second/1st.
                raise NotImplementedError("THERE MIGHT BE ANOTHER DATETIME HERE!\n%s\n" % self.filepath)

        if "Exif" in keys:
            exif = exif_dict["Exif"]
            if piexif.ExifIFD.DateTimeOriginal in exif:
                original = exif[piexif.ExifIFD.DateTimeOriginal]
                self.exif_original_timestamp = MyImageClass._datetime_from_exif_str(str(original))
            if piexif.ExifIFD.DateTimeDigitized in exif:
                digitized = exif[piexif.ExifIFD.DateTimeDigitized]
                self.exif_digitized_timestamp = MyImageClass._datetime_from_exif_str(str(digitized))

        # TODO TEST!
        if "GPS" in keys:
            self.exif_gps = GpsClass(exif_dict["GPS"])

    def _set_exif_time(self, exif_dict: dict | None = None, new_timestamp: datetime | None = None) -> dict:
        """
        Sets all 3 timestamps in exif data. (DateTime, DateTimeOriginal, DateTimeDigitized)
        Takes given new_timestamp or else uses self.json_photoTakenTime.
        Does this inplace, if exif_dict is given.
        If no exif_dict is given, you have to keep the returned dict and may not use it as an inplace function.
        Else changes will not be written.
        :param exif_dict: Whole exif dict of a file.
        Can be given if you already got it on hand. If not given, it will load the exif for self.filepath.
        :param new_timestamp: If given, will take this as the new timestamp.
        If not given, will use self.json_photoTakenTime.
        :return: New exif dict which you may write to the file.
        """
        if exif_dict is None:
            exif_dict = piexif.load(self.filepath)

        if new_timestamp is None:
            new_timestamp = self.json_photoTakenTime.strftime("%Y:%m:%d %H:%M:%S")
        else:
            new_timestamp = new_timestamp.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_timestamp
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_timestamp
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_timestamp
        # TODO! Make same changes to self/MyImageClass!
        return exif_dict

    def _set_exif_gps(self, exif_dict: dict | None = None, new_gps: GpsClass | None = None) -> dict:
        """
        Sets GPS info in exif data. (Latitude, Longitude, Altitude)
        Writes new_gps or if none is provided self.json_gps.
        Does this inplace, if exif_dict is given.
        If no exif_dict is given, you have to keep the returned dict and may not use it as an inplace function.
        Else changes will not be written.
        :param exif_dict: Whole exif dict of a file.
        Can be given if you already got it on hand. If not given, it will load the exif for self.filepath.
        :param new_gps: If provided, will take this as the new GPS Info.
        If not given, will use self.json_gps.
        :return: New exif dict which you may write to the file.
        """
        if exif_dict is None:
            exif_dict = piexif.load(self.filepath)
        if new_gps is None:
            new_gps = self.json_gps
        # TODO TEST!
        exif_dict["GPS"] = new_gps.to_exif()
        return exif_dict

    def _set_file_modified_and_access_time(self, new_timestamp: datetime | None = None):
        """
        Sets file modified time.
        :param new_timestamp: Writes new_timestamp if provided. Else self.json_photoTakenTime
        :return: None. Maybe crashes your PC if something goes wrong ;)
        """
        if new_timestamp is None:
            new_timestamp = self.json_photoTakenTime
        mod_time = new_timestamp.timestamp()
        os.utime(self.filepath, (mod_time, mod_time))
        # TODO TEST!

    def _set_file_creation_time(self, new_timestamp: datetime | None = None):
        # TODO COMMENT!
        # ripped from here
        # https://stackoverflow.com/questions/56008797/how-to-change-the-creation-date-of-file-using-python-on-a-mac
        if platform.platform().lower().startswith("macos"):
            if new_timestamp is None:
                new_timestamp = self.json_photoTakenTime
            # TODO TEST!
            command = 'SetFile -d "%s" %s' % (new_timestamp.strftime('%m/%d/%Y %H:%M:%S'), self.filepath)
            call(command, shell=True)
        else:
            raise TypeError("Your OS is not supported for this operation! "
                            "Linux does not save any creation date info for files"
                            " and the Windows version of it looks super-o-mega ugly.\n"
                            "See yourself:\n"
                            "https://stackoverflow.com/questions/4996405/how-do-i-change-the-file-creation-date-of-a-windows-file")

    @staticmethod
    def _datetime_from_exif_str(exif_datetime_str) -> datetime:
        # "b'2016:12:04 16:40:46'" -> '2016:12:04 16:40:46'
        dt_str = exif_datetime_str[2:-1]
        return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")

    @staticmethod
    def _datetime_to_exif_str(dt: datetime) -> str:
        return dt.strftime("%Y:%m:%d %H:%M:%S")

    def any_json_and_exif_timestamp_match(self) -> bool:
        """
        Check if any of the json timestamps and any of the exif timestamps match each other.
        :return: True, if a match is found. False if not.
        """
        for dt in [self.exif_zeroth_timestamp, self.exif_original_timestamp, self.exif_digitized_timestamp]:
            for dt2 in [self.json_photoTakenTime, self.json_creationTime]:
                if dt is not None and dt2 is not None:
                    if dt == dt2:
                        return True
        return False

    def json_and_exif_gps_match(self) -> bool:
        # TODO COMMENT!
        # TODO CREATE ME
        pass

    def adjust_file(self, force_json: bool = False, exif_dict: dict | None = None):
        # TODO COMMENT!

        # 1a. if exif data exits, dont overwrite it
        # 2. check if only partial exif data exists and write accordingly

        # 1b. if not, write json info into exif

        # 1c. except force = true, then overwrite

        # 3. set file access/modified/creation time
        # TODO CREATE ME
        pass

    def dry_adjust_file(self, exif_dict: dict | None = None):
        # TODO COMMENT!
        # TODO CREATE ME
        # Make a dry run to gather info about how many files are getting changed in fields (time, gps).
        # Also gather where times mismatch etc...
        pass


# TODO MOVE FUNCTION INTO CLASS
def _adjust_exif(exif_dict, img: MyImageClass):
    # TODO MOVE FUNCTION INTO CLASS
    if img.json_timestamp is not None and img.json_timestamp != 0:
        # TODO DONT OVERRIDE EXISTING EXIF DATETIME
        raise NotImplementedError("CHECK EXISTING DATETIME FIRST!")
        new_date = datetime.fromtimestamp(img.json_timestamp).strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date

    if img.json_latitude is not None and img.json_latitude != 0:
        lat = img.json_latitude
        lng = img.json_longitude
        altitude = img.json_altitude

        lat_deg = to_deg(lat, ["S", "N"])
        lng_deg = to_deg(lng, ["W", "E"])

        exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
        exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
            piexif.GPSIFD.GPSLatitude: exiv_lat,
            piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
            piexif.GPSIFD.GPSLongitude: exiv_lng,
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        }
        exif_dict = {"GPS": gps_ifd}

    return exif_dict


def set_exif_for_img(img: MyImageClass):
    # TODO MOVE FUNCTION INTO CLASS
    _filepath = img.filepath
    exif_dict = piexif.load(_filepath)
    new_exif = _adjust_exif(exif_dict, img)
    exif_bytes = piexif.dump(new_exif)
    piexif.remove(_filepath)
    piexif.insert(exif_bytes, _filepath)


f = 'Photo_6554014_DJI_414_jpg_4766051_0_20219197385(1) Kopie.jpg'
fp = '/Users/ferris/Downloads/Photo_6554014_DJI_414_jpg_4766051_0_20219197385(1) Kopie.jpg'
jp = '/Users/ferris/Downloads/Photo_6554014_DJI_414_jpg_4766051_0_20219197385(1) Kopie.jpg.json'
p = '/Users/ferris/Downloads'
