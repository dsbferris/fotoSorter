import PIL.Image
import exif
from exif import Image
import os
import shutil
from datetime import datetime, timedelta
from PIL import Image
import pillow_heif
import filedate

processed_count = 0
exif_changed_count = 0
heif_converted_count = 0
png_converted_count = 0
copied_files_count = 0
no_exif_count = 0
not_existing_files = 0


def exif_datetime_str(date: datetime) -> str:
    return date.strftime("%Y:%m:%d %H:%M:%S")


def file_datetime_str(date: datetime) -> str:
    return date.strftime("%d.%m.%Y %H:%M:%S")


def new_filepath_str(date: datetime, extension: str, new_dir: str) -> str:
    new_file_name = date.strftime("%Y-%m-%d_%H_%M_%S" + "." + extension)
    new_path = os.path.join(new_dir, new_file_name)
    while os.path.exists(new_path):
        date += timedelta(seconds=1)
        new_file_name = date.strftime("%Y-%m-%d_%H_%M_%S" + "." + extension)
        new_path = os.path.join(new_dir, new_file_name)
    return new_path


def change_exif_datetime(_img: exif.Image, filepath: str, date: datetime) -> exif.Image:
    img = _img
    if img.has_exif:
        if img.get('datetime') is not None:
            print(f"CONTAINING {filepath} has datetime {img.get('datetime')}")
            return img
    else:
        print(f"NO EXIF for {filepath}")
        global no_exif_count
        no_exif_count += 1

    img.set("datetime", exif_datetime_str(date))
    img.set("datetime_original", exif_datetime_str(date + timedelta(seconds=1)))
    img.set("datetime_digitized", exif_datetime_str(date + timedelta(seconds=1)))
    print(f"CHANGING {filepath} exif datetime to {exif_datetime_str(date)}")
    global exif_changed_count
    exif_changed_count += 1

    return img


def change_file_creation_date(filepath: str, date: datetime):
    date_str = file_datetime_str(date)
    filedate.File(filepath).set(
        created=date_str,
        accessed=date_str,
        modified=date_str
    )
    print(f"CHANGED FILE DATES for {filepath} to {date_str}")


def read_img_from_disk(filepath: str) -> exif.Image:
    return exif.Image(img_file=filepath)


def write_image_to_disk(img: exif.Image, new_path: str):
    with open(new_path, "wb") as img_file:
        img_file.write(img.get_file())
    print(f"WRITTEN file to {new_path}")


def convert_heic_to_jpg(filepath, new_filepath):
    heif_file = pillow_heif.open_heif(filepath)
    image = PIL.Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
    )
    image.save(new_filepath)
    global heif_converted_count
    heif_converted_count += 1
    print(f"CONVERTED HEIC {filepath} to {new_filepath}")


def convert_png_to_jpg(filepath, new_filepath):
    image = PIL.Image.open(filepath)
    jpg_img = image.convert("RGB")
    jpg_img.save(new_filepath)
    global png_converted_count
    png_converted_count += 1
    print(f"CONVERTED PNG {filepath} to {new_filepath}")


def process_file(_filepath: str, date: datetime, new_dir: str) -> str:
    global copied_files_count, processed_count, not_existing_files
    if not os.path.exists(_filepath):
        print("ERROR FILE DOES NOT EXITS")
        not_existing_files += 1
        return _filepath

    filepath = _filepath
    extension = filepath.split(".")[-1]
    new_filepath = new_filepath_str(date, extension, new_dir)
    print(f"READING file: {filepath}")

    if extension.lower() not in ["heic", "jpg", "jpeg", "png"]:
        print(f"COPYING file: {filepath}")
        shutil.copyfile(filepath, new_filepath)
        change_file_creation_date(new_filepath, date)
        copied_files_count += 1
        return new_filepath
    else:
        if extension.lower() == "heic":
            extension = "jpg"
            new_filepath = new_filepath_str(date, extension, new_dir)

            convert_heic_to_jpg(filepath, new_filepath)
            filepath = new_filepath

        elif extension.lower() == "png":
            extension = "jpg"
            new_filepath = new_filepath_str(date, extension, new_dir)

            convert_png_to_jpg(filepath, new_filepath)
            filepath = new_filepath

        img = read_img_from_disk(filepath)
        img = change_exif_datetime(img, filepath, date)
        write_image_to_disk(img, new_filepath)
        change_file_creation_date(new_filepath, date)

        print("")
        processed_count += 1
        return new_filepath


def get_date_from_image(filepath: str) -> datetime or None:
    img = exif.Image(filepath)
    date = img.get('datetime')
    if date is None:
        date = img.get("datetime_original")
        if date is None:
            date = img.get("datetime_digitized")
    return date
