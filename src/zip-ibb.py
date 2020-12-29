from zipfile import ZipFile
from csv import DictReader

data = dict()
column_names = ["path", "watermark", "multiple_faces", "low_resolution", "comment", "hat", "sunglasses", "glasses", "occlusion", "garbage"]
with open("./datasets/ibb/annotations.csv", 'r') as csv_file:
    reader = DictReader(csv_file, fieldnames=column_names)
    next(reader)  # skip headers
    for row in reader:
        data[row["path"]] = row

def is_ok(row):
  return \
    row["watermark"] == "False" \
    and row["multiple_faces"]  == "False" \
    and row["low_resolution"]  == "False" \
    and not row["comment"].strip() \
    and row["occlusion"] == "False" \
    and row["garbage"] == "False"

ok_image_paths = list(map(lambda x: x['path'], filter(is_ok, data.values())))

all_paths = list(map(lambda x: x['path'], data.values()))

print(f"{len(ok_image_paths)}/{len(all_paths)}")

# with ZipFile('./datasets/ibb/ibb-ok.zip','w') as zip: 
#     # writing each file one by one 
#     for file in ok_image_paths: 
#         zip.write(file)
