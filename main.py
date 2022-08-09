import image_exif
import sorter
import os
import read_json
from image_exif import MyImage, create_myimage_for_image

_path = '/Users/ferris/Downloads/takeout_all/'


def mv_image_with_json(path, f, json_file, new_path):
    full_f_path = os.path.join(path, f)
    json_file_path = os.path.join(path, json_file)

    new_f_path = os.path.join(new_path, f)
    new_json_path = os.path.join(new_path, json_file)

    os.rename(full_f_path, new_f_path)
    os.rename(json_file_path, new_json_path)


def move_those_with_json_timestamp(path: str):
    _with_timestamp = "!AAA_with_time"
    path_with_timestamp = os.path.join(path, _with_timestamp)
    # sorter._create_subdir(path_with_timestamp)

    _with_timestamp_and_geo = "!AAA_with_time_and_geo"
    path_with_timestamp_and_geo = os.path.join(path, _with_timestamp_and_geo)
    # sorter._create_subdir(path_with_timestamp_and_geo)

    files = os.listdir(path)
    images: list[MyImage] = []
    ignores = [_with_timestamp, _with_timestamp_and_geo, ".DS_Store"]
    for f in files:
        if f in ignores:
            continue
        if f.endswith(".json"):
            continue

        full_f_path = os.path.join(path, f)
        json_file = sorter.get_json_for_file(file=f, path=path)
        if json_file is None:
            print("No json for %s" % f)
        else:
            json_file_path = os.path.join(path, json_file)
            img = create_myimage_for_image(full_f_path, json_file_path)
            image_exif.set_exif_for_img(img)
            # images.append(img)
            if img.timestamp is not None and img.timestamp != 0:
                if img.longitude is not None and img.longitude != 0:
                    pass
                    # move_image_with_json(path, f, json_file, path_with_timestamp_and_geo)
                else:
                    pass
                    # move_image_with_json(path, f, json_file, path_with_timestamp)


def move_those_with_exif_timestamp(path: str):
    _with_timestamp = "0a0_with_exif_time"
    path_with_timestamp = os.path.join(path, _with_timestamp)
    sorter._create_subdir(path_with_timestamp)

    _without_timestamp = "0a0_without_exif_time"
    path_without_timestamp = os.path.join(path, _without_timestamp)
    sorter._create_subdir(path_without_timestamp)

    _cannot_handle = "0a0_cannot_handle"
    path_cannot_handle = os.path.join(path, _cannot_handle)
    sorter._create_subdir(path_cannot_handle)

    files = os.listdir(path)
    # images: list[MyImage] = []
    ignores = [_with_timestamp, _without_timestamp, ".DS_Store"]
    for f in files:
        if f in ignores:
            continue
        if f.endswith(".json"):
            continue

        full_f_path = os.path.join(path, f)
        json_file = sorter.get_json_for_file(file=f, path=path)
        if json_file is None:
            print("No json for %s" % f)
        else:
            json_file_path = os.path.join(path, json_file)
            try:
                dates = image_exif.get_datetime_from_img(full_f_path)
                if dates[0] is None and dates[1] is None and dates[2] is None:
                    mv_image_with_json(path, f, json_file, path_without_timestamp)
                else:
                    # mv_image_with_json(path, f, json_file, path_with_timestamp)
                    pass
                    # TODO CHECK EXIF AND JSON TIMESTAMP MATCH!

            except:
                mv_image_with_json(path, f, json_file, path_cannot_handle)
                # print("Cannot handle file %s" % f)


if __name__ == "__main__":
    print("HELLO!")
    move_those_with_exif_timestamp(path=_path)
