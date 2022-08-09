from datetime import datetime
import os

import my_exif
import read_csv

i_photo_dir = r"G:\Alle Fotos\iCloud Fotos\Photos"
i_csvs = [r"G:\Alle Fotos\iCloud Fotos\Photos\Photo Details.csv",
          r"G:\Alle Fotos\iCloud Fotos\Photos\Photo Details-1.csv"]
i_new = r"G:\Alle Fotos\iCloud NEW"


class iFoto:
    imgName: str
    importDate: datetime

    def filepath(self) -> str:
        return os.path.join(i_photo_dir, self.imgName)

    def __init__(self, name: str, date: str):
        self.importDate = date_str_to_datetime(date)
        self.imgName = name


def date_str_to_datetime(text: str) -> datetime:
    return datetime.strptime(text.strip(), r"%A %B %d,%Y %I:%M %p %Z")


def list_all_photos_in_folder(path: str) -> list[str]:
    return os.listdir(path)


def process_folder():
    dataset: list[iFoto] = []
    for csv in i_csvs:
        dataset += read_csv.read_file(csv)

    i_files = list_all_photos_in_folder(i_photo_dir)

    files_not_in_csv: list[str] = i_files.copy()
    for d in dataset:
        name = str(d.imgName)
        if name in files_not_in_csv:
            files_not_in_csv.remove(name)

    print(f"{len(files_not_in_csv)} files not in csv")
    print(files_not_in_csv)
    print("\n")

    for d in dataset:
        my_exif.process_file(d.filepath(), d.importDate, i_new)

    print(f"{my_exif.processed_count} processed")
    print(f"{my_exif.copied_files_count} got another format")
    print(f"{my_exif.not_existing_files} not existing files")
    print("")
    print(f"{my_exif.exif_changed_count} changed exif datetime")
    print(f"{my_exif.no_exif_count} got no exif data")
    print(f"{my_exif.heif_converted_count} heic converted to jpg")
    print(f"{my_exif.png_converted_count} png converted to jpg")
    print("\n")


def check_new_folder():
    new_files = os.listdir(i_new)
    count = 0
    for f in new_files:
        if f.lower().endswith("jpg"):
            filepath = os.path.join(i_new, f)
            if my_exif.get_date_from_image(filepath) is None:
                print(f"No datetime for {filepath}")
                count += 1
    print(f"No datetime for {count} images")