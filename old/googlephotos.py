import os
import pathlib
import shutil

import read_json

g_dir = r"G:\Alle Fotos\Takeout NO SUBFOLDERS"
g_new = r"G:\Alle Fotos\Takeout NEW"

g_braces = r"G:\Alle Fotos\Takeout (1)"
g_bearbeitet = r"G:\Alle Fotos\takeout-bearbeitet"
g_removed = r"G:\Alle Fotos\Takeout REMOVED"


# gps_altitude_ref GpsAltitudeRef.ABOVE_SEA_LEVEL
# gps_altitude 52.05719237435009 float
# gps_latitude (53.0, 16.0, 32.16) (tuple<float>)
# gps_latitude_ref "N"

# json lat = 53.2756; 0,2756*60 = 16.536; 0.536*60 = 32,16...
# https://www.revilodesign.de/blog/sonstiges/latitude-und-longitude-in-gps-koordinaten-umrechnen/

# gps_longitude (10.0, 4.0, 57.05)
# gps_longitude_ref 'E'

# ['gif', 'heic', 'webp', 'mp4', 'jpg', 'png', 'jpeg', 'json', 'mov']

def mass_rename_files():
    dirs = os.listdir(g_dir)
    dirs = [r"G:\Alle Fotos\Takeout\Google Fotos\dups"]
    for d in dirs:
        path = os.path.join(g_dir, d)
        files = os.listdir(path)
        for f in files:
            source_filepath = os.path.join(path, f)
            if f.lower().endswith("json"):
                json_data = read_json.read_json_file(source_filepath)
                assert "title" in json_data.keys()
                title = json_data["title"]
                json_data["title"] = "dup_" + title
                read_json.write_json_file(json_data, source_filepath)

            new_filepath = os.path.join(path, "dup_" + f)
            shutil.move(source_filepath, new_filepath)


def move_out_braces_files():
    files = os.listdir(g_dir)
    for f in files:
        last_dot_index = f.rfind('.')

        if f[last_dot_index - 1] == ')':
            source = os.path.join(g_dir, f)
            dest = os.path.join(g_braces, f)
            shutil.move(source, dest)
            print(f"MOVED {f}")


def copy_all_bearbeitet_and_their_original():
    files = os.listdir(g_dir)
    for f in files:
        if "-bearbeitet" in f:
            original_filename = f.replace("-bearbeitet", "")
            if not os.path.exists(os.path.join(g_dir, original_filename)):
                print(f"MISSING ORIGINAL for {f}")
            else:
                orig_source = os.path.join(g_dir, original_filename)
                orig_dest = os.path.join(g_bearbeitet, original_filename)
                source = os.path.join(g_dir, f)
                dest = os.path.join(g_bearbeitet, f)
                # shutil.copyfile(orig_source, orig_dest)
                # shutil.copyfile(source, dest)
                shutil.move(source, dest)
                print(f"MOVED {f}")


def find_json_for_file(filepath: str) -> str or None:
    json_filepath = filepath + ".json"
    if not os.path.exists(json_filepath):
        open_brace_index = filepath.find('(')
        close_brace_index = filepath.find(')')
        if open_brace_index != -1 and close_brace_index != -1:
            braces_text = filepath[open_brace_index:close_brace_index + 1]
            json_filepath = filepath.replace(braces_text, "") + braces_text + ".json"
            if os.path.exists(json_filepath):
                return json_filepath
        return None
    else:
        return json_filepath


def check_json_exists_for_every_file():
    files = os.listdir(g_dir)
    for f in files:
        if not f.lower().endswith("json"):
            filepath = os.path.join(g_dir, f)
            if find_json_for_file(filepath) is None:
                print(f"MISSING JSON FOR {filepath}")


def new_filepath_for_removal(count: int, p: pathlib.Path) -> str:
    ext = p.suffix
    if count % 2 == 0:
        new_name = 'IMG_{:04d}'.format(int(count / 2)) + ext
    else:
        new_name = "IMG_{:04d}_dup".format(int(count / 2)) + ext
    return os.path.join(g_removed, new_name)


def remove_duplicates(duplicates: list[list[str]]):
    count: int = 1
    for d_pair in duplicates:
        for fp in d_pair:
            count += 1  # first image starts with count = 2, its dup with 3...
            p = pathlib.Path(fp)
            if p.exists():
                new_path = new_filepath_for_removal(count, p)
                source_json = find_json_for_file(fp)
                if source_json is not None and os.path.exists(source_json):
                    jp = pathlib.Path(source_json)
                    new_jsonpath = new_filepath_for_removal(count, jp)
                    shutil.copyfile(source_json, new_jsonpath)

                shutil.copyfile(fp, new_path)


def process_folder():
    files = os.listdir(g_dir)
    for f in files:
        filepath = os.path.join(g_dir, f)
        if not f.lower().endswith("json"):
            json_filepath = find_json_for_file(filepath)
