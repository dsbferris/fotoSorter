from enum import Enum


class OperationEnum(Enum):
    NOT_SET = 0
    EXIF_AND_JSON_EQUAL = 1
    DIFFERENT_JSON_AND_EXIF = 2
    ONLY_JSON = 3
    ONLY_EXIF = 4
    NOTHING_BUT_SADNESS = 5
