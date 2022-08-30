import os
import sys

from GoogleTakeoutImage import GoogleTakeoutImage, NoJsonFileException, JsonParsingException, NoExifException
from pathlib import Path

from OperationEnum import OperationEnum

_takeout_path = Path('/Users/ferris/Downloads/takeout_all/')
_download_path = Path('/Users/ferris/Downloads')


def iter_media_files(path: Path):
    for p in path.iterdir():
        if p.is_dir():
            continue
        elif p.name == ".DS_Store":
            continue
        elif p.suffix == ".json":
            continue
        else:
            yield p


def make_a_dry_run(path: Path = _takeout_path):
    media_files: list[GoogleTakeoutImage] = []
    files = iter_media_files(path)
    for f in files:
        try:
            img = GoogleTakeoutImage(f)
            img.dry_adjust_file()
            media_files.append(img)
        except NoExifException as e:
            pass
        except NoJsonFileException as e:
            pass
        except JsonParsingException as e:
            pass
        except Exception as e:
            raise e

    dick_time = {e: [] for e in OperationEnum}
    dick_gps = {e: [] for e in OperationEnum}
    for mf in media_files:
        dick_time[mf.op_timestamp].append(mf)
        dick_gps[mf.op_gps].append(mf)
    return media_files, dick_time, dick_gps


def do_it(path: Path = _takeout_path, new_path: Path = _takeout_path.joinpath("#sorted")):
    files = iter_media_files(path)
    for f in files:
        try:
            img = GoogleTakeoutImage(f)
            img.adjust_file(new_path)
        except NoExifException as e:
            pass
        except NoJsonFileException as e:
            pass
        except JsonParsingException as e:
            pass
        except Exception as e:
            raise e


if __name__ == "__main__":
    assert sys.version_info >= (3, 10)
    # do_it()
    make_a_dry_run()
    pass


def copy_paste():

    from GoogleTakeoutImage import GoogleTakeoutImage
    from datetime import datetime, timedelta
    from OperationEnum import OperationEnum
    import main
    media_files, dick_time, dick_gps = main.make_a_dry_run()
    mfs = dick_time[OperationEnum.DIFFERENT_JSON_AND_EXIF]
    count = 0
    delta = timedelta(days=1)
    diffs = []
    for mf in mfs:
        if not mf._timestamp_equals(delta):
            diffs.append(mf)
