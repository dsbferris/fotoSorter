import json

from PIL import Image
import imagehash
import os
import numpy
import math
import time


class ImgWithHash:
    image_path: str
    image_hash: imagehash.ImageHash

    def __init__(self, path: str, h: imagehash.ImageHash):
        self.image_path = path
        self.image_hash = h


def generate_hash_for_file(filepath: str) -> imagehash.ImageHash:
    return imagehash.average_hash(image=Image.open(filepath), hash_size=64)


def generate_hashes_for_dir(dir: str) -> list[ImgWithHash]:
    l: list[ImgWithHash] = []
    files = os.listdir(dir)
    for f in files:
        filepath = os.path.join(dir, f)
        if os.path.isfile(filepath):
            if f[-4:] in [".jpg", ".png", "jpeg"]:
                # print(f"Processing file {f}")
                l.append(ImgWithHash(filepath, generate_hash_for_file(filepath)))

    return l


def generate_duplicates_list(dir: str) -> list[list[str]]:
    images_list = generate_hashes_for_dir(dir)
    count = len(images_list)
    duplicates: list[list[str]] = []
    for i in range(0, count):
        for j in range(i + 1, count):
            diff = images_list[i].image_hash - images_list[j].image_hash
            if diff == 0:
                # print(f"FOUND DUP {images_list[i].image_path} {images_list[j].image_path}")
                duplicates.append([images_list[i].image_path, images_list[j].image_path])

    return duplicates


def convert_hex_string_len_to_hash_size(str_len: int) -> int:
    # len = (size/2)^2 -> size = 2*sqrt(len)
    # size 8 -> len 16
    # size 64 -> len 1024
    return int(math.sqrt(str_len) * 2)


def generate_hashes_for_images(folder: str):
    start = time.time()
    # Using Hex-String of ImageHash because ImageHash itself is not supported with json
    image_with_hashes_list: list[tuple[str, list[str]]] = []
    files = os.listdir(folder)
    for i in range(len(files)):
        f = files[i]
        print(f"Processing {i}/{len(files)}")
        filepath = os.path.join(folder, f)
        if os.path.isfile(filepath):
            if f[-4:] in [".jpg", ".png", "jpeg"]:  # skip videos etc.
                hashes: list[str] = []
                image = Image.open(filepath)
                size_counter = 8
                while size_counter <= 1024:
                    hashes.append(imagehash.average_hash(image, size_counter).__str__())
                    size_counter *= 2
                image_with_hashes_list.append((f, hashes))
    end = time.time()
    print("This took {:.2f} seconds".format(end - start))
    with open("hash_test.json", "w") as json_file:
        json_file.write(json.dumps(image_with_hashes_list, indent=2))
    return image_with_hashes_list


def cluster_hashes(images_with_hashes: list[tuple[str, list[str]]] = None):
    if images_with_hashes is None:
        with open("hash_test.json", "r") as json_file:
            images_with_hashes: list[tuple[str, list[str]]] = json.loads(json_file.read())
        del json_file

    hashes: dict[str, list[str]] = {}
    for img in images_with_hashes:
        filepath = img[0]
        img_hashes = img[1]
        for img_hash in img_hashes:
            if img_hash in hashes:
                hashes[img_hash].append(filepath)
            else:
                hashes[img_hash] = [filepath]

    del img, img_hash, filepath, img_hashes
    return hashes


def print_dups(hashes: dict[str, list[str]]):
    dup_counts: dict[int, int] = {}
    for h in hashes:
        size_of_hash = convert_hex_string_len_to_hash_size(len(h))
        if size_of_hash in dup_counts:
            dup_counts[size_of_hash] += len(hashes[h]) - 1
        else:
            dup_counts[size_of_hash] = len(hashes[h]) - 1
    del h

    print("| hashsize | #duplicates |")
    print("| - | - |")
    for d in dup_counts:
        print(f"| {d} | {dup_counts[d]} |")
    del d
