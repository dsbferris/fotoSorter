import icloudfotos


def read_file(filepath: str):
    # reader = csv.reader(filepath)
    # TODO
    return _my_own_csv_reader(filepath)


def _my_own_csv_reader(filepath: str):
    with open(filepath, "r") as csv_file:
        count = 0

        dataset: list[icloudfotos.iFoto] = []
        for line in csv_file.readlines():
            if count == 0:
                count += 1
                continue
            else:
                split = line.split(",", 1)
                name = split[0]
                date = split[1].replace('"', "").strip()
                dataset.append(icloudfotos.iFoto(name, date))
                count += 1

        print(f"{filepath}: {count-1} entries")
        return dataset
