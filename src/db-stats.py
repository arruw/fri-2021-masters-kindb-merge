import csv
import pathlib
from pprint import pprint
from itertools import groupby

annotations_file_path = "./annotations/ibb-annotations.csv"

def is_useful(row):
  return \
    row["watermark"] == "False" \
    and row["multiple_faces"]  == "False" \
    and row["low_resolution"]  == "False" \
    and not row["comment"].strip() \
    and row["hat"] == "False" \
    and row["sunglasses"] == "False" \
    and row["occlusion"] == "False" \
    and row["garbage"] == "False"

def extract_member(row):
  path = pathlib.PurePath(row["path"])
  family_id = path.parent.parent.name
  member = path.parent.name
  return (family_id, member)

data = dict()
column_names = ["path", "watermark", "multiple_faces", "low_resolution", "comment", "hat", "sunglasses", "glasses", "occlusion", "garbage"]
with open(annotations_file_path, 'r') as csv_file:
    reader = csv.DictReader(csv_file, fieldnames=column_names)
    next(reader)  # skip headers
    for row in reader:
        data[row["path"]] = row

useful_members = sorted(set(map(extract_member, filter(is_useful, data.values()))))
useful_families = list(map(lambda x: (x[0], list(x[1])), groupby(useful_members, lambda x: x[0])))

all_families = set(map(lambda x: x[0], map(extract_member, data.values())))
useful_families = set(map(lambda x: x[0], filter(lambda x: len(x[1]) == 3, useful_families)))

print(f"{len(useful_families)} / {len(all_families)}")
print("Problematic families: ")
pprint(all_families - useful_families)
