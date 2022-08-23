import piexif
import os
from datetime import datetime
from gps_convert import change_to_rational, to_deg
import json
import GpsClass


class MyImageClass:
    filepath: str
    json_filepath: str

    # Recommended to use PhotoTakenTime
    json_photoTakenTime: datetime | None
    json_creationTime: datetime | None

    exif_zeroth_timestamp: datetime | None
    exif_digitized_timestamp: datetime | None
    exif_original_timestamp: datetime | None

    json_gps: GpsClass
    exif_gps: GpsClass

    def __init__(self, fp: str, json_filepath: str, exif_dict: dict | None = None):

        self.filepath = fp
        self.json_filepath = json_filepath

        self.read_data_from_json()
        self.read_data_from_exif(exif_dict)

    def read_data_from_json(self):
        with open(self.json_filepath, "r") as json_file:
            json_dict = json.load(json_file)
        if "photoTakenTime" in json_dict.keys():
            photoTakenTime = json_dict["photoTakenTime"]
            if "timestamp" in photoTakenTime:
                timestamp = photoTakenTime["timestamp"]
                timestamp = float(timestamp)
                self.json_photoTakenTime = datetime.fromtimestamp(timestamp)
        if "creationTime" in json_dict.keys():
            creationTime = json_dict["photoTakenTime"]
            if "timestamp" in creationTime:
                timestamp = creationTime["timestamp"]
                timestamp = float(timestamp)
                self.json_creationTime = datetime.fromtimestamp(timestamp)

        if "geoData" in json_dict.keys():
            geoData = json_dict["geoData"]
            if "latitude" in geoData.keys():
                latitude = geoData["latitude"]
                self.json_latitude = float(latitude)
            if "longitude" in geoData.keys():
                longitude = geoData["longitude"]
                self.json_longitude = float(longitude)
            if "altitude" in geoData.keys():
                altitude = geoData["altitude"]
                self.json_altitude = float(altitude)

    def read_data_from_exif(self, exif_dict: dict | None = None):
        if exif_dict is None:
            exif_dict = piexif.load(self.filepath)
        if "0th" in exif_dict.keys():
            zeroth = exif_dict["0th"]
            if piexif.ImageIFD.DateTime in zeroth.keys():
                zeroth_dt = zeroth[piexif.ImageIFD.DateTime]
                self.exif_zeroth_timestamp = MyImageClass.datetime_from_exif_str(zeroth_dt)
        if "1st" in exif_dict.keys():
            first = exif_dict["1st"]
            if piexif.ImageIFD.DateTime in first.keys():
                # Most programms will only read/write to the first/0th EXIF data block,
                # but some may read/write from second/1st.
                raise NotImplementedError("THERE MIGHT BE ANOTHER DATETIME HERE!\n%s\n" % self.filepath)

        if "Exif" in exif_dict.keys():
            exif = exif_dict["Exif"]
            if piexif.ExifIFD.DateTimeOriginal in exif:
                original = exif[piexif.ExifIFD.DateTimeOriginal]
                self.exif_original_timestamp = MyImageClass.datetime_from_exif_str(original)
            if piexif.ExifIFD.DateTimeDigitized in exif:
                digitized = exif[piexif.ExifIFD.DateTimeDigitized]
                self.exif_digitized_timestamp = MyImageClass.datetime_from_exif_str(digitized)

        # TODO! READ GPS FROM EXIF

    def any_json_and_exif_timestamp_equal(self):
        for dt in [self.exif_zeroth_timestamp, self.exif_original_timestamp, self.exif_digitized_timestamp]:
            for dt2 in [self.json_photoTakenTime, self.json_creationTime]:
                if dt is not None and dt2 is not None:
                    if dt == dt2:
                        return True
        return False

    def _set_exif_time(self, exif_dict: dict | None = None, new_timestamp: datetime | None = None) -> dict:
        if exif_dict is None:
            exif_dict = piexif.load(self.filepath)

        if new_timestamp is None:
            new_date = self.json_photoTakenTime.strftime("%Y:%m:%d %H:%M:%S")
        else:
            new_date = new_timestamp.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        return exif_dict

    def _set_exif_gps(self, exif_dict) -> dict:
        pass
        # TODO CREATE ME

    def adjust_exif_for_image(self, force: bool = False, exif_dict: dict | None = None):
        # Enum Idea:
        # only json
        # exif and json match
        # exif and json mismatch
        pass
        # 1. Check if exif data exists
        # 2a. if exists, don't overwrite, but mark somehow if exif and json is different
        # 2aa. except force = true, then overwrite
        # 2b. if not, write new data to file
        # TODO CREATE ME

    def _set_file_datetime(self):
        pass
        # TODO CREATE ME

    @staticmethod
    def datetime_from_exif_str(exif_str) -> datetime:
        # "b'2016:12:04 16:40:46'" -> '2016:12:04 16:40:46'
        dt_str = exif_str[2:-1]
        return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")

    @staticmethod
    def datetime_to_exif_str(dt: datetime) -> str:
        return dt.strftime("%Y:%m:%d %H:%M:%S")


# TODO MOVE FUNCTION INTO CLASS
def _adjust_exif(exif_dict, img: MyImageClass):
    if img.json_timestamp is not None and img.json_timestamp != 0:
        # TODO DONT OVERRIDE EXISTING EXIF DATETIME
        raise NotImplementedError("CHECK EXISTING DATETIME FIRST!")
        new_date = datetime.fromtimestamp(img.json_timestamp).strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date

    if img.json_latitude is not None and img.json_latitude != 0:
        pass
        # TODO CHECK THIS!!!
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
    _filepath = img.filepath
    exif_dict = piexif.load(filepath)
    new_exif = _adjust_exif(exif_dict, img)
    exif_bytes = piexif.dump(new_exif)
    piexif.remove(_filepath)
    piexif.insert(exif_bytes, _filepath)


path = r"/Users/ferris/Downloads/takeout_all"
f = r"0bbc9513-aae7-4055-bbed-b30635aa528f(1).jpg"
filepath = os.path.join(path, f)


def find_image_with_non_one_seconds_denominator(ppath: str):
    files = os.listdir(ppath)
    count = 0
    for file in files:
        if count > 20:
            return
        if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):
            exif_dict = piexif.load(os.path.join(ppath, file))
            if "GPS" in exif_dict.keys():
                if piexif.GPSIFD.GPSLatitude in exif_dict["GPS"].keys() \
                        or piexif.GPSIFD.GPSLongitude in exif_dict["GPS"].keys():
                    if exif_dict["GPS"][piexif.GPSIFD.GPSLatitude][2][1] > 1:
                        print("%d: %s" % (exif_dict["GPS"][piexif.GPSIFD.GPSLatitude][2][1], file))

                        count += 1
                    if exif_dict["GPS"][piexif.GPSIFD.GPSLongitude][2][1] > 1:
                        print("%d: %s" % (exif_dict["GPS"][piexif.GPSIFD.GPSLongitude][2][1], file))

                        count += 1
