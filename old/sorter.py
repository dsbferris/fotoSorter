import os
from pathlib import Path
import re


def rreplace(s: str, old: str, new: str, occurrence: int):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def get_file_extension(file: str):
    """
    Get file extension for a file. Includes the dot.
    :param file: File to get the extension for
    :return: Extension with dot. (e.g. ".jpg")
    """
    return Path(file).suffix


def get_all_file_extensions_in_folder(path: str):
    files = os.listdir(path)
    extensions = set()
    for f in files:
        suffix = get_file_extension(f.lower())
        extensions.add(suffix)
    for e in extensions:
        print(e)
    return list(extensions)


_unsupported_extensions = [".html", ".json"]


def get_json_for_file(file: str, path: str) -> str | None:
    """
    Returns filename for corresponding json-file to given file
    :param file: File to find a json-file for.
    :param path: Path or pseudo-working directory in which to check if a json-file exists.
    :return: None if no json-file can be found. If not None, its guaranteed to be a valid file inside path.
    """
    json_file: str
    if '(' in file:
        first_open_brace_index = file.index('(')
        first_close_brace_index = file.index(')')
        braces_text = file[first_open_brace_index:first_close_brace_index + 1]
        file_edit = file.replace(braces_text, "", 1)
        json_file = file_edit + braces_text + ".json"

        json_file_path = os.path.join(path, json_file)
        if Path(json_file_path).exists():
            return json_file

    # maybe file contains braces but doesn't follow that one specific naming scheme
    json_file = file + ".json"

    json_file_path = os.path.join(path, json_file)
    if Path(json_file_path).exists():
        return json_file

    # let's try another naming method
    ext = Path(file).suffix
    json_file = file.replace(ext, "") + ".json"  # Include dot in json, because ext contains the dot

    json_file_path = os.path.join(path, json_file)
    if Path(json_file_path).exists():
        return json_file

    # ok, one more naming method
    try:
        filename, extension = file.rsplit(".", 1)
    except:
        return None

    regex_result = re.findall('_\d$', filename)
    if len(regex_result) > 0:
        json_file = rreplace(filename, regex_result[0], "", 1)
        json_file += "." + extension + regex_result[0] + ".json"
        json_file_path = os.path.join(path, json_file)
        if Path(json_file_path).exists():
            return json_file

    return None


def _move_file_with_json(path: str, f: str, new_path: str) -> bool:
    """
    Moves file with it's metadata-json file into given subdirectory. Might raise Exceptions on file move.
    :param path: Path where file f and its json is located
    :param f: File to movie with its json
    :param new_path: New path. Files will be moved there.
    :return: True if file with its json were moved. False if file got no corresponding json.
    """
    full_f_path = os.path.join(path, f)

    json_for_f = get_json_for_file(f, path)
    if json_for_f is not None:
        full_json_path = os.path.join(path, json_for_f)
        new_f_path = os.path.join(new_path, f)
        new_json_path = os.path.join(new_path, json_for_f)
        os.rename(full_f_path, new_f_path)
        os.rename(full_json_path, new_json_path)
        return True
    else:
        return False


def _create_subdir(subdir: str):
    subdir_path = Path(subdir)
    if not subdir_path.exists():
        subdir_path.mkdir()


def _move_out_bearbeitet_files(path: str, new_path: str):
    bearbeitet = "-bearbeitet"
    files = os.listdir(path)
    for f in files:
        if bearbeitet in f:
            clean_filename = f.replace(bearbeitet, "")
            if _move_file_with_json(path, clean_filename, new_path):
                full_f_path = os.path.join(path, f)
                new_f_path = os.path.join(new_path, f)
                os.rename(full_f_path, new_f_path)
            else:
                print("Error with bearbeitet file: %s" % f)


def _merge_bearbeitet_files(path: str, new_path: str):
    bearbeitet = "-bearbeitet"
    files = os.listdir(path)
    for f in files:
        if bearbeitet in f:
            clean_filename = f.replace(bearbeitet, "")
            json = get_json_for_file(f, path)
            full_f_path = os.path.join(path, f)
            new_path = os.path.join(new_path, clean_filename)


def move_files_with_their_json(path: str):
    sorted_subdir = os.path.join(path, "sorted")
    _create_subdir(sorted_subdir)
    # bearbeitet_subdir = os.path.join(path, "!AAA_bearbeitet")
    # create_subdir(bearbeitet_subdir)

    # _move_out_bearbeitet_files(path, bearbeitet_subdir)
    files = os.listdir(path)
    for f in files:
        if f == ".DS_Store":
            continue
        ext = get_file_extension(f)
        if ext in _unsupported_extensions:
            # skip this
            pass
        else:
            if _move_file_with_json(path, f, sorted_subdir):
                pass


# move_files_with_their_json(fotos_path)
