import piexif
import os
from datetime import datetime
import json
from GpsClass import GpsClass
from subprocess import call
import platform


class GoogleTakeoutImage:
    """
    Contains json and exif info about an Image.
    Supports reading and writing exif to an Image.
    """
    filepath: str
    # json_filepath: str

    # Recommended to use PhotoTakenTime
    json_photoTakenTime: datetime | None = None
    json_creationTime: datetime | None = None

    exif_zeroth_timestamp: datetime | None = None
    exif_digitized_timestamp: datetime | None = None
    exif_original_timestamp: datetime | None = None

    json_gps: GpsClass = None
    exif_gps: GpsClass = None

    def __init__(self, filepath: str, json_filepath: str, exif_dict: dict | None = None):
        """
        Initialized a new Instance. filepath and json_filepath must be provided.
        exif_dict can be passed, if you already have it on hands, for example while debugging and testing.
        So you don't have to read a file over and over again.
        Reads all data from File/Image and json. No need to call a load method.

        :param filepath: Filepath to a File. This may be a file of any format,
        as you can manipulate creation, modified, access datetime for every file.
        :param json_filepath: Your initially pass file in filepath need to have a corresponding json file.
        :param exif_dict: If you already got it, pass it.
        """
        self.filepath = filepath
        if json_filepath is None or json_filepath == "":
            raise ValueError("No json path provided")
        # self.json_filepath = json_filepath
        try:
            self._read_data_from_json(json_filepath)
        except Exception as e:
            raise ValueError("Could not read/process json file.\n%s" % e)

        self._read_data_from_exif(self._save_load_exif())

    def _read_data_from_json(self, json_filepath):
        """
        Reads all available Info from json, like timestamps and GPS.
        """
        with open(json_filepath, "r") as json_file:
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

    def _save_load_exif(self) -> dict:
        try:
            return piexif.load(self.filepath)
        except Exception as e:
            raise ValueError("Unable to load exif from file")

    def _read_data_from_exif(self, exif_dict: dict | None = None):
        """
        Reads exif data from self.filename. Will use exif_dict if provided.
        :param exif_dict: exif_dict retrieved vom piexif.load()
        :return: No return. Will write values to self.
        """
        # TODO COMMENT!
        if exif_dict is None:
            exif_dict = self._save_load_exif()
        keys = exif_dict.keys()
        if "0th" in keys:
            zeroth = exif_dict["0th"]
            if piexif.ImageIFD.DateTime in zeroth.keys():
                zeroth_dt = zeroth[piexif.ImageIFD.DateTime]
                self.exif_zeroth_timestamp = GoogleTakeoutImage._datetime_from_exif_str(str(zeroth_dt))
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
                self.exif_original_timestamp = GoogleTakeoutImage._datetime_from_exif_str(str(original))
            if piexif.ExifIFD.DateTimeDigitized in exif:
                digitized = exif[piexif.ExifIFD.DateTimeDigitized]
                self.exif_digitized_timestamp = GoogleTakeoutImage._datetime_from_exif_str(str(digitized))

        # TODO TEST!
        if "GPS" in keys:
            self.exif_gps = GpsClass(exif_dict["GPS"])

    def _set_exif_time(self, exif_dict: dict | None = None, new_timestamp: datetime = json_photoTakenTime) -> dict:
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
            exif_dict = self._save_load_exif()

        new_timestamp = new_timestamp.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_timestamp
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_timestamp
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_timestamp
        # TODO! Make same changes to self/MyImageClass!
        return exif_dict

    def _set_exif_gps(self, exif_dict: dict | None = None, new_gps: GpsClass = json_gps) -> dict:
        """
        Sets GPS info in exif data. (Latitude, Longitude, Altitude)1
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
            exif_dict = self._save_load_exif()
        if new_gps is None:
            new_gps = self.json_gps
        # TODO TEST!
        exif_dict["GPS"] = new_gps.to_exif()
        return exif_dict

    def _set_file_modified_and_access_time(self, new_timestamp: datetime = json_photoTakenTime):
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

    def _set_file_creation_time(self, new_timestamp: datetime = json_photoTakenTime):
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

    def _timestamp_equals(self) -> bool:
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

    def _gps_equals(self) -> bool:
        # TODO COMMENT!
        return self.json_gps == self.exif_gps

    def _has_json_timestamp(self):
        return self.json_photoTakenTime is not None \
               or self.json_creationTime is not None

    def _has_exif_timestamp(self):
        return \
            self.exif_zeroth_timestamp is not None \
            or self.exif_original_timestamp is not None \
            or self.exif_digitized_timestamp

    def _has_json_gps(self):
        return self.json_gps is not None

    def _has_exif_gps(self):
        return self.exif_gps is not None

    def adjust_file(self, force_json: bool = False, exif_dict: dict | None = None):
        # TODO COMMENT!
        if self._has_exif_timestamp():
            if self._has_json_timestamp():
                if self._timestamp_equals():
                    # good to go.
                    pass
                else:
                    # timestamp differ. Don't override file date unless know which to use.
                    if force_json:
                        # Write json timestamp to exif
                        exif_dict = self._set_exif_time(exif_dict=exif_dict)
            else:
                # Weird. Exif timestamp but no json
                pass
        else:
            if self._has_json_timestamp():
                # Write json timestamp to exif
                exif_dict = self._set_exif_time(exif_dict=exif_dict)
                # Set file date to json date.
                self._set_file_creation_time()
                self._set_file_modified_and_access_time()
            else:
                # Sad. No info about timestamp
                pass

        if self._has_exif_gps():
            if self._has_json_gps():
                if self._gps_equals():
                    # good to go.
                    pass
                else:
                    # gps differ
                    if force_json:
                        # Write json gps to exif
                        exif_dict = self._set_exif_gps(exif_dict=exif_dict)
            else:
                # Weird. Exif but no json
                pass
        else:
            if self._has_json_gps():
                # Write json gps to exif
                exif_dict = self._set_exif_gps(exif_dict=exif_dict)
            else:
                # Sad. No info about gps
                pass

        if exif_dict is not None:
            piexif.dump(exif_dict)
            exif_dump = piexif.remove(self.filepath)
            piexif.insert(self.filepath, exif_dump)

    exit_codes = [i for i in range(-1, 5)]
    dry_run_timestamp_operation = -1
    dry_run_gps_operation = -1

    def dry_adjust_file(self):
        # TODO COMMENT!

        if self._has_exif_timestamp():
            if self._has_json_timestamp():
                if self._timestamp_equals():
                    # good to go.
                    self.dry_run_timestamp_operation = 0
                else:
                    # gps differ
                    self.dry_run_timestamp_operation = 1
            else:
                # Weird. Exif but no json
                self.dry_run_timestamp_operation = 2
        else:
            if self._has_json_timestamp():
                # Write json gps to exif
                self.dry_run_timestamp_operation = 3
            else:
                # Sad. No info about gps
                self.dry_run_timestamp_operation = 4

        if self._has_exif_gps():
            if self._has_json_gps():
                if self._gps_equals():
                    # good to go.
                    self.dry_run_gps_operation = 0
                else:
                    # gps differ
                    self.dry_run_gps_operation = 1
            else:
                # Weird. Exif but no json
                self.dry_run_timestamp_operation = 2
        else:
            if self._has_json_gps():
                # Write json gps to exif
                self.dry_run_gps_operation = 3
            else:
                # Sad. No info about gps
                self.dry_run_gps_operation = 4

    @staticmethod
    def list_path(path: str):
        # TODO RIP FROM sorter
        pass

f = 'Photo_6554014_DJI_414_jpg_4766051_0_20219197385(1) Kopie.jpg'
fp = '/Users/ferris/Downloads/Photo_6554014_DJI_414_jpg_4766051_0_20219197385(1) Kopie.jpg'
jp = '/Users/ferris/Downloads/Photo_6554014_DJI_414_jpg_4766051_0_20219197385(1) Kopie.jpg.json'
p = '/Users/ferris/Downloads'
