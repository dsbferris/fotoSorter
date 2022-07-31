# import image_sim_checker as sim
#
# folder = r"G:\Alle Fotos\Takeout NO SUBFOLDERS"
# image_hash_list = sim.generate_hashes_for_images(folder)
# hashes_dict = sim.cluster_hashes(image_hash_list)
# sim.print_dups(hashes_dict)


import os
import pathlib

_path = '/Users/ferris/Downloads/takeout_all'


def get_file_extension(file: str):
    """
    Get file extension for a file. Includes the dot.
    :param file: File to get the extension for
    :return: Extension with dot. (e.g. ".jpg")
    """
    return pathlib.Path(file).suffix


def get_all_file_extensions_in_folder(path: str):
    files = os.listdir(path)
    extensions = set()
    for f in files:
        suffix = get_file_extension(f.lower())
        extensions.add(suffix)
    for e in extensions:
        print(e)
    return list(extensions)


# _extensions = get_all_file_extensions_in_folder(_path)
# supported_extensions = ["jpg", "jpeg", "png", "heic"]
unsupported_extensions = [".html", ".json"]


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
        if pathlib.Path(json_file_path).exists():
            return json_file
    else:
        json_file = file + ".json"

        json_file_path = os.path.join(path, json_file)
        if pathlib.Path(json_file_path).exists():
            return json_file

        # let's try another naming method
        ext = get_file_extension(file)
        json_file = file.replace(ext, "") + ".json"  # Include dot in json, because ext contains the dot

        json_file_path = os.path.join(path, json_file)
        if pathlib.Path(json_file_path).exists():
            return json_file

    return None


def _move_file_with_json(path: str, f: str, subdir: str) -> bool:
    full_f_path = os.path.join(path, f)

    json_for_f = get_json_for_file(f, path)
    if json_for_f is not None:
        full_json_path = os.path.join(path, json_for_f)
        new_f_path = os.path.join(subdir, f)
        new_json_path = os.path.join(subdir, json_for_f)
        os.rename(full_f_path, new_f_path)
        os.rename(full_json_path, new_json_path)
        return True
    else:
        return False


def move_files_with_their_json(path: str):
    subdir = os.path.join(path, "files_with_their_json")
    subdir_path = pathlib.Path(subdir)
    if not subdir_path.exists():
        subdir_path.mkdir()
    files = os.listdir(path)
    for f in files:
        ext = get_file_extension(f)
        if ext in unsupported_extensions:
            # skip this
            pass
        else:

            # TODO Handle files with "...-bearbeitet..."
            raise NotImplementedError

            if _move_file_with_json(path, f, subdir):
                pass


# move_files_with_their_json(_path)
