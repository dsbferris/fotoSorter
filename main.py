import os
from GoogleTakeoutImage import GoogleTakeoutImage, NoJsonFileException, JsonParsingException, NoExifException
from pathlib import Path

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


def make_a_dry_run(path: Path):
    media_files: list[GoogleTakeoutImage] = []
    files = iter_media_files(path)
    for f in files:
        try:
            img = GoogleTakeoutImage(f)
            media_files.append(img)
        except NoExifException as e:
            pass
        except NoJsonFileException as e:
            pass
        except JsonParsingException as e:
            pass
        except Exception as e:
            raise e
    return media_files


if __name__ == "__main__":
    g_files = make_a_dry_run(_takeout_path)
    print("got %d files" % len(g_files))
    pass
