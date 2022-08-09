import read_json
import piexif
import os
from datetime import datetime
from gps_convert import change_to_rational, to_deg


class MyImage:
    filepath: str
    json_filepath: str
    timestamp: float | None
    latitude: float | None
    longitude: float | None
    altitude: float | None

    def __init__(self, filepath: str, json_filepath: str, timestamp: float | None = None,
                 latitude: float | None = None, longitude: float | None = None, altitude: float | None = None):
        self.filepath = filepath
        self.json_filepath = json_filepath
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude


def create_myimage_for_image(filepath: str, json_filepath: str) -> MyImage:
    timestamp = None
    latitude = None
    longitude = None
    altitude = None
    json = read_json.read_json_file(json_filepath)
    if "photoTakenTime" in json.keys():
        photoTakenTime = json["photoTakenTime"]
        if "timestamp" in photoTakenTime:
            timestamp = photoTakenTime["timestamp"]
            timestamp = float(timestamp)
    if "geoData" in json.keys():
        geoData = json["geoData"]
        if "latitude" in geoData.keys():
            latitude = geoData["latitude"]
            latitude = float(latitude)
        if "longitude" in geoData.keys():
            longitude = geoData["longitude"]
            longitude = float(longitude)
        if "altitude" in geoData.keys():
            altitude = geoData["altitude"]
            altitude = float(altitude)

    img = MyImage(filepath, json_filepath, timestamp, latitude, longitude, altitude)
    return img


def _adjust_exif(exif_dict, img: MyImage):
    if img.timestamp is not None and img.timestamp != 0:
        # TODO DONT OVERRIDE EXISTING EXIF DATETIME
        new_date = datetime.fromtimestamp(img.timestamp).strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date

    if img.latitude is not None and img.latitude != 0:
        pass
        # TODO CHECK THIS!!!
        lat = img.latitude
        lng = img.longitude
        altitude = img.altitude

        lat_deg = to_deg(lat, ["S", "N"])
        lng_deg = to_deg(lng, ["W", "E"])

        exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
        exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
            piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
            piexif.GPSIFD.GPSLatitude: exiv_lat,
            piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
            piexif.GPSIFD.GPSLongitude: exiv_lng,
        }
        exif_dict = {"GPS": gps_ifd}

    return exif_dict


def set_exif_for_img(img: MyImage):
    _filepath = img.filepath
    exif_dict = piexif.load(filepath)
    new_exif = _adjust_exif(exif_dict, img)
    exif_bytes = piexif.dump(new_exif)
    piexif.remove(_filepath)
    piexif.insert(exif_bytes, _filepath)


def convert_exif_datetime2datetime(dt: str) -> datetime:
    # "b'2016:12:04 16:40:46'" -> '2016:12:04 16:40:46'
    dt = dt[2:-1]
    dt_format = "%Y:%m:%d %H:%M:%S"
    new_dt = datetime.strptime(dt, dt_format)
    return new_dt


def get_datetime_from_img(filepath: str) -> list[str | None]:
    exif_dict = piexif.load(filepath)
    zeroth_dt, digitized, original = None, None, None
    if "0th" in exif_dict.keys():
        zeroth = exif_dict["0th"]
        if piexif.ImageIFD.DateTime in zeroth.keys():
            zeroth_dt = zeroth[piexif.ImageIFD.DateTime]
            zeroth_dt = convert_exif_datetime2datetime(zeroth_dt)
    if "1st" in exif_dict.keys():
        first = exif_dict["1st"]
        if piexif.ImageIFD.DateTime in first.keys():
            print("WATCH OUT!")
            print(filepath)
            raise NotImplementedError("THERE MIGHT BE ANOTHER DATETIME HERE!")

    if "Exif" in exif_dict.keys():
        exif = exif_dict["Exif"]
        if piexif.ExifIFD.DateTimeOriginal in exif:
            original = exif[piexif.ExifIFD.DateTimeOriginal]
            original = convert_exif_datetime2datetime(original)
        if piexif.ExifIFD.DateTimeDigitized in exif:
            digitized = exif[piexif.ExifIFD.DateTimeDigitized]
            digitized = convert_exif_datetime2datetime(digitized)
    return [zeroth_dt, original, digitized]


path = r"/Users/ferris/Downloads/takeout_all/!AAA_with_exif_time"
f = r"0bbc9513-aae7-4055-bbed-b30635aa528f(1).jpg"
filepath = os.path.join(path, f)
