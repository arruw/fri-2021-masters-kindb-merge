import pandas as pd
import os
from PIL import Image
from pprint import pprint
from tqdm import tqdm
from glob import glob

OUT_ROOT = "/mnt/d/matja/dev/kindb-merge"
CROP_ROOT = "/mnt/d/matja/Downloads/Crop/Crop"

# df = pd.read_csv("./annotations/kin-images.csv")
# for index, row in tqdm(df.iterrows(), total=df.shape[0]):
#   try:
#     person_path = f"{OUT_ROOT}/{row['pid']}"
#     if not os.path.exists(person_path):
#       os.mkdir(person_path)
#     src_path = row['path'].replace("./datasets/ibb", CROP_ROOT)
#     if os.path.exists(src_path):
#       if os.path.exists(f"{person_path}/{row['iid']}.png"): continue
#       img = Image.open(src_path)
#       if src_path.startswith(CROP_ROOT):
#         img = img.resize((1024, 1024))
#       img.save(f"{person_path}/{row['iid']}.png")
#     else:
#       # if os.path.exists(f"{person_path}/todo-{row['iid']}.png"): continue
#       # img = Image.open(row['path'])
#       # img.save(f"{person_path}/todo-{row['iid']}.png")
#       pass
#   except Exception as e:
#     print(f"[ERROR] {row['path']}: {e}")
#     # input("Press Enter to continue...")

# # for i in glob(f"{OUT_ROOT}/**/todo-*.png", recursive=True):
# #   os.remove(i)
# #   # pprint(i)


# for p in glob(f"{OUT_ROOT}/*"):
#   if not os.listdir(p):
#     os.rmdir(p)